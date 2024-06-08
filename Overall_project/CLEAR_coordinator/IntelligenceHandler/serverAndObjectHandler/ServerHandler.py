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

import socketio, requests, threading, os, base64, requests, cv2, json, numpy as np, time
from IntelligenceHandler.serverAndObjectHandler.ObjectFound import ObjectFound
from datetime import datetime, timedelta 

"""
ServerHandler is majorly responsible for the connection between the controller and worker server.
ServerHandler feeds the worker server primarily with image data, which in turn is 
transmuted into computer vision text description.

ServerHandler additionally handles communication with the LLM worker, providing contextual
input, and receiving responses that map into drone actions.
"""
class ServerHandler():
    def __init__(self, intel, workerUrl) -> None:
        self.intel = intel

        #Considers the number of objects that have been 
        #seen and accounted for since launch. Objects are recounted if lost
        #and then found again. 
        self.count = 0

        self.sio = socketio.Client()
        self.URL = workerUrl

        #Used to account for multiple LLM responses
        self.modelName = ""

        self.turn = 0
        self.lastSentImage = None
        # self.lastTimeImageCalled = 0

        self.lastSentContext = None

        #This attribute is sourced from the LLM response.
        #It contains the action, and passed values 
        self.llmGeneratedInstruction = None

        #Used to prevent LLM query while waiting for another query
        self.awaitingLLMOutput = False

        #This is used when wanting to get conversation ledger fron 
        #LLM worker. Used when applicaiton exits normally
        self.wantInstructions = False

        # For having a persistant connection
        self.session = requests.Session()
        
        serverThread = threading.Thread(target= self.startListen)
        serverThread.start()
        self.lastTimeContextGiven = 0

        if not self.intel.drone.manualControlOnly:
            self.waitingForInitData()

    #Pauses program run till being notified of 
    # the LLM worker readiniess 
    def waitingForInitData(self) :
        print("getting image dimension")
        self.getImageDimensions()

        print("waiting for llm information")
        # self.getModelName()

        while self.modelName == "" :
            #Requests model name
            time.sleep(5)
            self.getModelName()
            pass
        print("llm information given")
    
    # Once called, ServerHandler will begin working with the worker server
    def configureWorkerRelationship(self):
        self.objects = self.intel.objects 
        self.depthMatrix = self.intel.depth
        self.target = self.intel.target

        #Also of the socketio emits applicable to intelligence, 
        #majorly related to the worker server, other than keepalive.
        #keepAlive is emiited from the interface server, when the user 
        # submits a chat, or logs onto the webapp. 
        self.sio.on("context_updated")(self.context_updated)
        self.sio.on("depth_updated")(self.matrix_updated)
        self.sio.on("client_chat_updated")(self.llm_chat_updated)
        self.sio.on("instruction_updated")(self.givenInstruction)
        self.sio.on("model_name_posted")(self.getModelName)
        self.sio.on("keepAlive")(self.intel.refreshTimer)
        self.sio.on("turnoff")(self.turnOff)

        self.setup = True


    def waitingForLLMResponse(self) :
        if self.awaitingLLMOutput :
            if not hasattr(self, "responseWaitingTimer") :
                self.responseWaitingTimer = time.time()

            #seconds allowed to wait for LLM response.
            #prevents waiting forever for a response that might 
            #not come.
            # Five mins
            TOO_LONG = 60 * 1
            if time.time() > self.responseWaitingTimer + TOO_LONG :
                self.awaitingLLMOutput = False
                self.resetConversation()
                del self.responseWaitingTimer

        return self.awaitingLLMOutput

    #sends json llm instruction document. 
    #If document does not already exist, create one from
    #drone definition and retry function.
    def sendInstructions(self) :  
        data = None
        jsonFileName = (str(self.intel.drone.GPT_EVOLUTION) + "_{}.json").format(self.modelName)
        txtInitFileName = (str(self.intel.drone.GPT_SET_UP) + "_{}.txt").format(self.modelName)
        
        # Make this cleaner. Changed to not use current json
        # Used to remember old conversation.
        with open(txtInitFileName, "r") as f:
            chatBotContext = f.read()
        init = [{"role": "system", "content": chatBotContext}]
        with open(jsonFileName, "w") as file:
            json.dump(init, file)
        
        with open(jsonFileName, 'r') as f:
                data = json.load(f)

        #to put machine type in front. This allows better file organization 
        # in the autoDrone-chat repository 
        print (data)
        data = ([{"hardware" : self.intel.drone.NAME}]
                + data[:])

        url = '{}/instruction'.format(self.URL)
        # Send the POST request

        self.timeSentIntructions = time.time()
        response = self.session.post(url, json=data, headers={'Content-Type': 'application/json'})
        print("sending instructions response is : {}".format(response))

        if response.status_code == 200:
            print("POST request successful.")
            print("Response:", response.json())
        else:
            print("POST request failed with status code:", response.status_code)

    #Asks LLM worker for most recent conversation ledger file.
    #Function is called when program ends naturally. 
    def requestInstructions(self):
        self.wantInstructions = True
        response = requests.post(self.URL+"/instruction", json={'string': "want"})
        print ("request response {}".format(response))

    def turnOff(self, message):
        # Corresponds with the name in worker_server
        SERVICE_NAME = "coordinator"
        url = '{}/service_turnoff'.format(self.URL)
        response = requests.post(url, json={'service': SERVICE_NAME})
        print(f"the service is turning off with code {response}")
        self.intel.drone.droneIsRunning = False

    #Receives conversation ledger from LLM worker
    def givenInstruction(self, message): 
        if not self.wantInstructions : return

        url = '{}/instruction'.format(self.URL)

        jsonFileName = (str(self.intel.drone.GPT_EVOLUTION) + "_{}.json").format(self.modelName)

        print ("instruction given to me!")
        # Perform GET request to the URL
        response = requests.get(url)
        if response.status_code == 200:
            # Save the JSON object as a file
            with open(jsonFileName, "w") as file:
                json.dump(response.json(), file)
                self.messages = response.json()
            self.wantInstructions = False
        else:
            print("Error:", response.status_code, response.text)
        print ("given instruct complete")

    #Begin to listen to worker server
    def startListen(self) :
        # Event listeners
        self.sio.connect(self.URL)
    
    #Stop listening to the worker server
    def disconnect(self) :
        self.sio.disconnect()

    # takes in all found objects given by object-detection
    # and see's if any of the "new" objects have already been found.
    #This serves as a form of object tracking
    def updateObjects(self, input):
        newObjects = []
        for i in input:
            # for drones that rotate
            discoveredObject = ObjectFound(i, self.count, 
                    self.intel.drone.currentYawRotation)
            
            if hasattr(self.intel.drone, "OBJECTS_TO_IGNORE"):
                if discoveredObject.generalObjectName in self.intel.drone.OBJECTS_TO_IGNORE:
                    print("bad object")
                    continue

            newObjects.append(discoveredObject)
            self.count += 1
        
        if not self.objects == []:
            for i in self.objects:
                # will check for most similar object in list
                # and then update the existing object

                initSize = len(self.objects)
                foundSameObj, newObjects =  i.updateObject(newObjects)
                if foundSameObj != None:
                    #remove the object that already existed 
                    #from the new object list
                    self.count -= (initSize - len(self.objects))
                    if i.isTarget :
                        print("updating the target!")
                        self.target.updateTarget(i.midpoint)
        #appending all new objects to the existing object list
        for i in newObjects:
            print("adding new object")
            self.objects.append(i)
            print(i.naturalExport(self.intel.depth))
    
    # check all objects, and noticing if have not been seen for specified time.
    #If they are considered too old, then they are demoted to either
    #having the old status, or are deleted and removed from the object list
    def checkingAgeOfObjects(self) :
        # removing old objects
        for i in self.objects:
            if i.tooOld():
                self.demotingObject(i)

    # if given object was new, now consider it old.
    # if the object was already old, forget about the object
    def demotingObject(self, obj) :
        if obj.objectOld  :
            if hasattr(obj,"sub_objects") :
                print("deleting object {}".format(obj.tag))
                for i in obj.sub_objects :
                    obj.sub_objects.remove(i)
            self.objects.remove(obj)
            del obj
            print("removed object")
        else :
            if hasattr(obj,"sub_objects") :
                for i in obj.sub_objects :
                    i.objectOld = True
            if obj.isTarget :
                #targetTime is the amount of time
                # a target has been considered old.
                obj.targetTime = time.time()
            obj.objectOld = True

    #This is where the computer vision context is generated.
    #After the object-detection worker(s) run their process, 
    #they post to the server which emits a signal that is caught 
    #and launches this function. This function will parse the string
    #input, and start the process of making objects. 
    def context_updated(self, message):
        #This is being used in place of sleeping
        TOO_LONG_TIME = 0.075
        if not hasattr(self, "contextTimer") :
            self.contextTimer = 0
        elif (self.contextTimer + TOO_LONG_TIME - time.time()) > 0 :
            return

        url = '{}/contextInfo'.format(self.URL)
        response = self.session.get(url)

        if response.status_code == 200:
            context = response.json()['string']
            self.lastSentImage = None
            self.updateObjects(context.split('&'))
            self.contextTimer = time.time()
        else:
            print("Error:", response.status_code, response.text)

    #This is where the the depth matrix data is updated. 
    #After image input is sent to the computer vision workers, 
    #a depth perception worker will run the image, and then post the data 
    #back to the server. This funciton will then be triggered and process 
    #the data sent back to the worker server. 
    def matrix_updated(self, message):
        TOO_LONG_TIME = 0.4
        if not hasattr(self, "depthTimer") :
            self.depthTimer = 0
        elif (self.depthTimer + TOO_LONG_TIME - time.time()) > 0 :
            return
        
        url = '{}/depth'.format(self.URL)
        response = self.session.get(url)

        if response.status_code == 200:

            smallMatrix = np.array(response.json(),
                                dtype=float)
            self.depthMatrix.setTo(smallMatrix)

        else : 
            print("Error with matrix :", response.status_code, response.text)

    #This funciton sends image data from the drone to the worker server. 
    #The sent information will then be processed by the depth perception, 
    #and object-detection workers. 
    def sendImage(self, img):
        # to avoid same image being sent over and make faster.
        #if the img pointer address is different than the address of lastSentImage
        if img is not self.lastSentImage:
            self.lastSentImage = img

            # Encode the image as WebP with a quality of 80. 
            #Doing this in case worker server has bandwidth problems
            _, buffer = cv2.imencode('.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 80])
            img_base64 = base64.b64encode(buffer)
            url = '{}/image'.format(self.URL)
            
            # Use the session object for the request
            response = self.session.post(url, json={'image': img_base64.decode('utf-8')})

    def getImageDimensions(self):
        url = '{}/imageDimensions'.format(self.URL)
        DELAY_BETWEEN_RETRY = 5.00
        self.imageDimensions = None
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    width = data['width']
                    height = data['height']
                    self.imageDimensions = width, height
                    if hasattr(self, "setup") and self.setup:
                        self.intel.depth.updateDimensions(self.imageDimensions)
                        self.intel.target.updateScreenDimensions(width)
                        self.intel.drone.waitingForCamChange = False
                    return True
                else:
                    print("Error:", data['message'])
            elif response.status_code == 404:
                print("Error: No image found")
            elif response.status_code == 500:
                data = response.json()
                print("Error processing image dimensions:", data['details'])
            else:
                print("Unknown error:", response.status_code)
            print("Failed to get image dimensions\n Retrying now.")
            time.sleep(DELAY_BETWEEN_RETRY)
            
    #The generated contextual information is sent the LLM worker via 
    # the worker server. After this data is received, the LLM worker 
    #will repond, and provide information back to the controller, 
    #prompting a robotic response. hostchat refers to the LLM worker
    #while clientchat refers to this, the controller
    def sendContext(self, context) :
        url = '{}/hostChatInfo'.format(self.URL)
        print("The context being sent is : {}".format(context))

        content = {'prompt': context}
        if self.intel.lastLlmResponse is not None:
            # Updates the conversation ledgers previous reply
            content["fixResponse"] = self.intel.lastLlmResponse

        response = requests.post(url, json = content)

        if response.status_code == 200 :
            self.awaitingLLMOutput = True

        else :
            print("error sending context : " + str(response))
    
    #This function receives and saves the LLM worker response
    def llm_chat_updated(self, message) :
        TOO_LONG_TIME = 0.15
        if not hasattr(self, "llmTimer") :
            self.llmTimer = 0
        elif (self.llmTimer + TOO_LONG_TIME - time.time()) > 0 :
            return

        url = '{}/clientChatInfo'.format(self.URL)
        response = requests.get(url)

        if response.status_code == 200:
            self.llmGeneratedInstruction = response.json()['response']
            self.awaitingLLMOutput = False
            print ("llm output is : {}".format(self.llmGeneratedInstruction))
            self.lastTimeContextGiven = time.time()

        else : 
            print("Error for chat:", response.status_code, response.text)
    
    #This function returns the generated LLM response, or returns None.
    #If returning a value, that is not None, the output will be reset. 
    def getLLMOutput(self) :
        temp = None
        if self.llmGeneratedInstruction != None :
            temp = self.llmGeneratedInstruction
            self.lastTimeContextGiven = time.time()
            self.llmGeneratedInstruction = None
        return temp
    
    #Tells the LLM worker to reset the conversation ledger.
    #This is used when LLM response is breaking, and not producing
    #acceptable output
    def resetConversation(self) :
        url = '{}/resetChat'.format(self.URL)
        print("should be resetting chat")
        response = requests.post(url)

        #Will generally, already by false. But if function is called
        #by waiting too long for a response, then this will be helpful.
        self.awaitingLLMOutput = False

        if response.status_code != 200 :
            print("error sending reset request : " + str(response))

    #Asks the LLM worker which LLM model is running.
    #This information is used in chosing which LLM instruction 
    #should be provided. 
    def getModelName(self, message = None) :
        url = '{}/llmModel'.format(self.URL)
        #To ensure no repeat requests for model, 
        #prevents possible infinite loop of calls. 
        #If recieved modelname within past 4 seconds
        #dont request model name again.
        #Also this allows for updates to the modelName
        if (hasattr(self, "timeModelNameRecieved") 
            and time.time() < self.timeModelNameRecieved + 10):
            return

        response = requests.get(url)

        if response.status_code == 200:
            self.timeModelNameRecieved = time.time()
            self.modelName = response.json()['model']
            time.sleep(2)
            self.sendInstructions()
            print ("llm name is : {}".format(self.modelName))
        else : 
            print("Error for chat:", response.status_code, response.text)