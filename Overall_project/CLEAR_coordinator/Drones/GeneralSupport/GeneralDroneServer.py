# DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

# This material is based upon work supported by the Under Secretary of Defense for 
# Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions,
# findings, conclusions or recommendations expressed in this material are those 
# of the author(s) and do not necessarily reflect the views of the Under 
# Secretary of Defense for Research and Engineering.

# © 2023 Massachusetts Institute of Technology.

# Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

# The software/firmware is provided to you on an As-Is basis

# Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS Part 
# 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, 
# U.S. Government rights in this work are defined by DFARS 252.227-7013 or 
# DFARS 252.227-7014 as detailed above. Use of this work other than as specifically
# authorized by the U.S. Government may violate any copyrights that exist in this work.

import cv2
import numpy as np
import requests
import socketio
import threading
import time
from http.client import RemoteDisconnected
from urllib3.exceptions import InsecureRequestWarning
import warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

"""
DroneServer handles the conneciton between the controller, this application, with 
interface server, which connects to drone. Here commands are sent to the drone, 
while also, input from the drone is recieved. 

Additionally, this script will not function properly if the connection
to the server is limited.
"""

class DroneServer():
    def __init__(self, interfaceUrl, drone) -> None:
        # For having a persistent connection
        self.session = requests.Session()
        # Trust self-signed certificate
        self.session.verify = False
        self.sio = socketio.Client(http_session=self.session)  
        self.URL = interfaceUrl
        self.drone = drone

        if self.drone.handlesImages:
            self.sio.on("image_updated")(self.imageUpdated)

        self.sio.on("feedback_updated")(self.feedbackUpdated)
        self.sio.on("click_updated")(self.userClickUpdated)
        self.sio.on("user_chat_update")(self.userChatGiven)

        self.sio.on("consideringClick")(self.considerUserClick)
        self.sio.on("keys_updated")(self.userKeysUpdated)
        self.sio.on("roboClick_cancelled")(self.roboClick_cancelled)

        self.sio.on("readiness_requested")(self.giveReady)
        self.sio.on("system_ready")(self.systemReadyEmitted)
        self.sio.on("web_stall")(self.restartingCoordinator)
        self.sio.on("active_user_update")(self.updateActiveUsers)


        # User keys sourced from the interface
        self.keysPressed = []

        self.GOOD_CODE = 200
        self.image = None
        
        self.userChat = ""

        self.clientRotation = None
        self.systemReady = False

        # If the LLM or human user clicks on the screen
        # we will wait till the click is confirmed by the user
        self.waitingForClickResponse = False

        # Responsible for knowing when the drone is performing an action.
        # An example would be if it's grabbing an object. This is useful to know
        # so that we do not send another command while it is grabbing
        self.commandOccuring = False

        serverThread = threading.Thread(target= self.startListen, daemon=True)
        serverThread.start()

        self.resetReadiness()
        self.waitingForConnection()

    def restartingCoordinator(self, message = None):
        self.drone.droneIsRunning = False
    
    # Users that are currently on the interface
    def getActiveUsers(self):
        if hasattr(self, "activeUsers"):
            return self.activeUsers
        self.updateActiveUsers()
        return self.activeUsers
        
    # updates current list of active users
    def updateActiveUsers(self, message = None):
        url = "{}/activeUsers".format(self.URL)
        response = self.session.get(url, verify=False)

        if response.status_code == 200:
            self.activeUsers = response.json()['activeUsers']
        else :
            self.activeUsers = []
    
    def userChatGiven(self, message = None) :
        print(message)
        self.userChat = f"{message['user']} says, {message['message']}"
        print(self.userChat)

    def systemReadyEmitted(self, message = None) :
        self.systemReady = True

    def resetReadiness(self) :
        print("resetting readiness")
        self.session.post("{}/readyreset".format(self.URL), verify=False)
        time.sleep(1)

    def giveReady(self, message = None) :
        url = '{}/readyInfo'.format(self.URL)
        self.session.post(url,json={"coordinator":"coordinator"})

    def userSentMessage(self, message = None):
        url = "{}/userMessage".format(self.URL)
        response = self.session.get(url, verify=False)
        data = response.json()
        self.keysPressed = data["keys"]

    def requestReadiness(self) :
        print("Asking about readiness")
        self.session.post("{}/readyrequest".format(self.URL), verify=False)

    # Waiting for all services needed by interface to be ready
    def waitingForConnection(self) :
        url = "{}/readyInfo".format(self.URL)
        self.requestReadiness()
        self.giveReady()

        print("waiting for drone to be ready")
        while not self.systemReady :
            response = self.session.get(url,verify=False)
            print(response.content)

            if response.status_code == 200:
                # Check the name of the drone readying up. 
                # Needs to match the current drone class, otherwise 
                # changing to new class of drone
                nameUrl = "{}/coordinatorClassName".format(self.URL)
                givenClassName = None
                
                while givenClassName is None:
                    nameResponse = self.session.get(nameUrl, verify=False)

                    if nameResponse.status_code == 200:
                        givenClassName = response.content
                    else : time.sleep(2)
                
                if givenClassName != self.drone.NAME:
                    # Exception type known by GeneralDrone
                    raise type(self.drone).WrongDrone(givenClassName, self.drone.NAME)
                
                # Coordinator can begin to rock & roll
                self.systemReady = True
            elif ("coordinator is NOT ready" in str(response.content)):
                self.giveReady()
            time.sleep(20)
        print("Drone Ready!!")

    def soReady(self, message) :
        self.systemReady = True
    
    def roboClick_cancelled(self, message = None) :
        if self.waitingForClickResponse :
            self.recordMessageForIntelHandler("person denied your grab request")

        self.waitingForClickResponse = False
        self.commandOccuring = False
        self.drone.movementController.completedAction()

    def awaitingRoboClickResponse(self) :
        while self.waitingForClickResponse:
            time.sleep(0.2)
            #This is true if grab is confirmed
            if self.commandOccuring :
                return

    #post coordinate to intermediary and asks 
    #for human confirmation before grabbing
    def postClick(self, position):
        # This then ensures no other command will
        # be called when waiting for user confirmation
        self.waitingForClickResponse = True
        url = "{}/roboClick".format(self.URL)
        data = {"x": position[0], "y": position[1]}
        print ("post click : ", data)

        response = requests.post(url, json=data, verify=False)
        if response.status_code == 200:
            print("Successfully posted roboClick")
            self.awaitingRoboClickResponse()
        else:
            print(f"Failed to post roboClick, status code: {response.status_code}")
            
    def startListen(self):
        # Event listeners
        self.sio.connect(self.URL)
    
    def disconnect(self):
        self.sio.disconnect()
    
    def userKeysUpdated(self, message):
        url = "{}/keys".format(self.URL)
        response = self.session.get(url, verify=False)
        data = response.json()
        self.keysPressed = data["keys"]
        if not response.status_code == self.GOOD_CODE:
            return
        
    def imageUpdated(self, message):
        url = "{}/image".format(self.URL)
        try :
            response = self.session.get(url, verify=False)
            if not response.status_code == self.GOOD_CODE:
                return

            # Convert binary data to numpy array
            nparr = np.frombuffer(response.content, np.uint8)

            # Decode numpy array to image
            self.image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        #Means server is likly being overworked
        except RemoteDisconnected:
            print("The server closed the connection without response.")
        
        except Exception as e :
            print ("Image exception occurred")
            time.sleep(0.1)

    #Gets most recently known image
    def getImage(self) :
        while type(self.image) == type(None) : 
            time.sleep(0.1)
        return self.image
    
    #Gets most recently known rotation
    def getRotation(self) :
        return self.clientRotation
    
    #just formats movement data for send
    def movementDict(self, arr) :
        return {"velocities" : arr}
    
    # Queries for rotation of drone
    def askRotation(self) :
        return {"Command": "clientRotation?"}
    
    #will update peceived audio and commandOccuring
    def feedbackUpdated(self, message) :
        print("feedback updated has been called")
        url = '{}/feedbackInfo'.format(self.URL)
        try : 
            response = self.session.get(url, verify=False)

            if response.status_code == 200:
                data = response.json()
                print(f"The data is \n {data}")
                for key in data.keys():
                    if hasattr(self, key) :
                        #setting the attribute equal found value
                        value = data[key]
                        if data[key] is not None and type(data[key]) == str:
                            if str(data[key]).lower() == "true" :
                                value = True
                            elif str(data[key]).lower() == "false" :
                                value = False
                        setattr(self, key, value)
                        if key == "commandOccuring" :
                            if (not self.commandOccuring) :
                                self.drone.movementController.completedAction()
                                self.waitingForClickResponse = False
                        #Means a human web client is activly using the application
                        if key == "userChat" :
                            self.drone.intelligence.refreshTimer()
                        
                        if key == "comment":
                            self.commentGiven(value)
            else:
                print("Error:", response.status_code, response.text)
        except Exception as e: 
            print(f"Something went ary with the feedback: {e}")
    
    def commentGiven(self, comment):
        print(f"comment given is {comment}")
        if comment == "changingCamera":
            self.drone.waitingForCamChange = True
            self.drone.intelligence.serverHandler.getImageDimensions()
        
    def sendMovement(self, movement, askRotation = False) :
        url = '{}/instructionInfo'.format(self.URL)
        data = {}
        data.update(self.movementDict(movement))
        if askRotation :
            data.update(self.askRotation())
        response = self.session.post(url, json=data, verify=False)
    
    #Useful for sending a list of string commands
    #or a single command
    def sendInstructions(self, command):
        self.commandOccuring = True
        url = '{}/instructionInfo'.format(self.URL)
        data = {}
        data.update({"Command":command})
        return self.session.post(url, json=data)
    
    def sendChat(self, chat) :
        url = '{}/userMessage'.format(self.URL)
        data = {"user" : "CLEAR", "message" : chat}
        return self.session.post(url, json=data, verify=False)
    
    # This is appended to the robot user conversation
    def sendCommandDescription(self, chat) :
        url = "{}/describeCommand".format(self.URL)
        data = {"command" : chat}
        return self.session.post(url, json=data, verify=False)

    def recordMessageForIntelHandler(self, message) :
        self.drone.message = message
