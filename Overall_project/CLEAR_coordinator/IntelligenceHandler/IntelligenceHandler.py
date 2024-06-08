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

import time
from IntelligenceHandler.Target import Target
from IntelligenceHandler.serverAndObjectHandler.ServerHandler import ServerHandler
from IntelligenceHandler.DepthMatrix import DepthMatrix
from IntelligenceHandler.support.ContextualSupport import ContextualSupport

"""
IntelligenceHandler coordinates all of the worker machines,
compiles all of the information recieved from these resources
to send instruction to the system being controlled.
"""
class IntelligenceHandler():
    """
    Parameters :
        1. drone :  
            the object which directly provides instruction for 
            the interface server, feeding the sytem with instruction 

        2. workerAddress :  
            The URL for the worker server, given to the ServerHandler 
    """
    def __init__(self, drone, workerAddress):
        self.drone = drone

        #objects are generated from the object-detection output.
        #stores information on items detected, and used for 
        #object tracking
        self.objects = []

        #The message sent to the worker server
        self.message = ""

        #The action chosen by the LLM response.
        #Governs robot response.
        self.action = ""

        #Used when sequence action is employed by the LLM.
        #Stores notes written by the LLM, and redeploys them for 
        #following queries. 
        self.notedSequence = []

        self.timeBetweenChatCalls = 1
        self.timeGPTCalled = 0
        
        self.contextGenerator = ContextualSupport()

        self.configureWorkerAttributes(workerAddress)

        TIME_TILL_EXPIRE_MINUTES = 1000

        #60 for seconds in minute
        self.TIME_TILL_EXPIRE =  TIME_TILL_EXPIRE_MINUTES * 60

        self.timeAlive = time.time()

        self.stall = False

        self.lastLlmResponse = None

        self.userMessageHasNotStoppedDroneYet = True

        # This is content that can be used to teach CLEAR.
        # The LLM can decide if it wants to Learn anything given
        # the content stored in this list
        self.learnableMessages = []
    
    def configureWorkerAttributes(self, workerAddress):
        self.serverHandler = ServerHandler(self, workerAddress)
        self.imgHeight, self.imgWidth = self.serverHandler.imageDimensions
        self.depth = DepthMatrix((self.imgWidth, self.imgHeight))
        self.target = Target(self.imgWidth, self.depth)
        self.serverHandler.configureWorkerRelationship()

    #Main loop for the IntelligenceHandler object. Loops till 
    #program begins termination. From here, processes regarding handling images,
    #object perception, and LLM response is called.
    def run(self) :
        while self.drone.droneIsRunning : 
            
            # self.checkIfShouldWait()

            if self.drone.handlesImages :
                self.drone.picFrame = self.drone.getImage()
                self.serverHandler.sendImage(self.drone.picFrame)

            self.serverHandler.checkingAgeOfObjects()

            #this is a sort of query check
            self.shouldLoseTarget()
    
            llmOutput = self.serverHandler.getLLMOutput()

            # When a user sends a message stop the drone
            # and forget the target.
            if self.userHasSentMessage() and self.userMessageHasNotStoppedDroneYet:
                self.userMessageHasNotStoppedDroneYet = False
                self.drone.movementController.resetDrone()
                self.drone.movementController.completedAction()

            if llmOutput is not None :
                print ("llm output is : {}".format(llmOutput))
                self.processGPT(llmOutput)
            
            elif ((self.action == "" or self.action == "rotate")
                and not self.serverHandler.waitingForLLMResponse()) :
                    self.callGPT()
            
        self.serverHandler.disconnect()

    #If it has been determined that there are no humans interacting with 
    #the system, then all LLM and image sending processes will be stalled, 
    #and further, the readiness of the interface server will be reset. 
    #This process will be stuck in this loop till determined that human
    #is interacting with the process. The purpose of this is to save 
    #computer resources, halting images from being sent, and the LLM worker
    #to not be called.
    def checkIfShouldWait(self) :
        if (time.time() > 
            self.TIME_TILL_EXPIRE + 
            self.timeAlive) :
                #telling drone to stop uploading info.
                #Lessen computational cost on server, 
                #saving money in case of Azure web hosting
                self.drone.server.resetReadiness()

                #stop calling GPT, saves massivie costs
                self.stall = True
                while (time.time() > 
                    (self.TIME_TILL_EXPIRE + 
                    self.timeAlive)) :
                        time.sleep(2)
            
    #Resets target, adjusting attributes of the target
    #and also value in this object
    def forgetTarget(self) :
        if self.target.active :
            self.target.active = False

        if hasattr(self.target.target, "isTarget") :
            self.target.target.isTarget = False

        self.target.target = None

        print ("target lost!")

    #determines if target is too old to still be a target
    def shouldLoseTarget(self) :
        if self.target.target is None :
            return 
        
        # I need to implement locks 
        try : 
            if not self.target.target.isTarget :
                return 
            
            if not self.target.target.objectOld :
                return 
        
            if hasattr(self.target.target, "targetTime") :
                TIME_TOLERANCE = 2.5
                if (time.time() < (TIME_TOLERANCE + self.target.target.targetTime)) : 
                    return 
                else : pass
            else : 
                return
        except Exception as e :
            print("target time exception : ", e)

        self.forgetTarget()

    #Generates information from various sources of contextual input, 
    #and sends it to worker responsible for LLM response
    def callGPT(self) :
        # if self.drone.manualControlOnly or self.stall: return
        
        sleepTime = (self.timeGPTCalled + self.timeBetweenChatCalls) - time.time()

        if sleepTime > 0 : return 

        targetObject = None
        if self.target.active :
            targetObject = self.target.target
            print ("yes the target is in fact, active")
        
        context = ("{}\n".format(self.contextGenerator.
                generateBackgroundContext(target=targetObject)))
        
        for i in self.objects :
            # Only reporting objects that are not old
            if not i.objectOld:
                if not context == "" :
                    context += '\n'
                context += i.naturalExport(self.depth)
        
        if hasattr(self.drone, "extraContext"):
            context += f" {self.drone.extraContext()}"

        if hasattr(self.drone, "message") :
            context += self.drone.message
            del self.drone.message

        # if applicable adds chat input to context
        if self.userHasSentMessage() :
            print(self.drone.server.userChat)
            self.userMessageHasNotStoppedDroneYet = True
            # context += "\n user chat:\"{}\"".format(self.drone.server.userChat)
            self.addLearnableContent(self.drone.server.userChat)
            self.drone.server.userChat = ""

        if len(self.notedSequence) :
            NOTE = ". Reminder: "
            context += NOTE + self.notedSequence.pop(0)
        
        #  checking if there are any active users on the system
        activeUsers = self.drone.server.getActiveUsers()
        if len(activeUsers) > 0 :
            message = "You are interacting with "
            for i in activeUsers:
                message += f"{i},"
            
            message = message[:len(message)-1]
            context = f"{message}. {context}."
        
        if len(self.learnableMessages) > 0:
            message = "LEARNABLE_CONTENT"
            for i in self.learnableMessages:
                message += f"{i},"
            
            # Resets the learning
            self.learnableMessages = []

            message = message[:len(message)-1]
            context = f"{context}. {message}"

        self.serverHandler.sendContext(context)
        
        self.timeGPTCalled = time.time()

    def addLearnableContent(self, content):
        self.learnableMessages.append(content)

    # Will return all content in learnableMessages
    def useLearnableContent(self, content):
        self.learnableMessages.append(content)

    #This handles the sequence action. 
    #Actions are generally defined in movement or in 
    #drone definition, however, since this relates to 
    #information it is here. 
    #The function checks if the sequence command has been called,
    #and if it has, it then saves the notes into the sequence attribute.
    def sequenceHandler(self, reply) :
        flag = "sequence" 
        if flag in reply:
            print(reply)
            reply= reply[reply.find(flag):]
            print("\n\n this is the sequence statement: ", reply)
            self.notedSequence = self.contextGenerator.separateSequence(reply)
            print (self.notedSequence)
            return True
        return False
        
    #ProcessGPT parses the LLM response, detecting if a command
    #was given, and what the command is.
    def processGPT(self, reply):
        # shortens the reply 
        if reply == "conversationReset":
            self.notedSequence = []
            reply = "restart"
        
        reply = self.contextGenerator.processLlmResponse(reply)

        # This is for testing emotion response
        if hasattr(self.drone, "actionCommentary"):
            self.drone.server.userChat = self.drone.actionCommentary(reply)
        # END of testing code
            
        try:

            if reply is None or reply == "no":
                return False

            if self.sequenceHandler(reply):
                return False

            try:
                if "mess" in reply:
                    start_index = reply.find("mess")+len("mess")
                    if reply[start_index] == '(':
                        start_index += 1

                    self.message = reply[start_index: start_index + reply[start_index:].find(')')]
                    self.drone.server.sendChat(self.message)
                    return False
                
                elif ("rotate" in reply.lower() and ("right" in reply.lower() or "left" in reply.lower())):
                        dir = self.drone.movementController.setRotationDir(reply.lower())
                        self.settingAction("rotate", additionalNote = dir)
                        return False
                        
            except Exception as e:
                self.serverHandler.resetConversation()
                print("LLM gave bad output {}".format(e))
                return False

            if self.depth.ready:
                desiredAction = ""
                # Skip first character in case of bad output
                try:
                    if '(' in reply[1:]:
                        tag_start = reply.find('(') + 1
                        tag_end = reply.find(')')
                        tag = int(reply[tag_start:tag_end])
                        targ = self.returnObjectByTag(tag)
                        
                        if targ is None:
                            print("target {} not known".format(tag))
                            # reply = "ERROR"
                            return

                        desiredAction = reply[:tag_start - 1].strip()

                        if hasattr(self.drone, "approveAction"):
                            if not (self.drone.approveAction(desiredAction, targ.generalObjectName)) :
                                self.message = f"The action {desiredAction}, can not be used with {targ.generalObjectName}"
                                print(f"\n\n{self.message}\n\n")
                                self.drone.server.sendChat(self.message)
                                self.addLearnableContent(self.message)
                                return False
                            
                        self.target.setTarget(targ, self.depth)
                    else:
                        # Search for any action in the string
                        action_positions = {action: reply.find(action) for action in self.drone.actionDict if action in reply}
                        if action_positions:
                            desiredAction = min(action_positions, key=action_positions.get)
                        else:
                            desiredAction = reply
                except Exception as e:
                    self.serverHandler.resetConversation()
                    print("LLM gave incorrectly formatted expression. The error:", e)

                if (not hasattr(self.drone, "actionDict") or desiredAction not in self.drone.actionDict):
                    print("invalid action given or movement not ready")
                    reply = "ERROR"
                    self.serverHandler.resetConversation()
                    print(desiredAction)
                    return False

                self.settingAction(desiredAction)
            else:
                print("no depth matrix")
        finally:
            self.lastLlmResponse = reply

    def settingAction(self, desiredAction, additionalNote = None):
        self.action = desiredAction
        self.describeCommandToServer(additionalNote = additionalNote)
        print("action being taken is: {}".format(self.action))

    #For actions with an Object-Id parameter, like moveto,
    #this returns the intented object for the action
    def returnObjectByTag(self, tag) :
        print("The tags are: ")
        for i in self.objects :
            print(f"tag {i.tag}")
            if i.tag == tag :
                return i
            if hasattr(i,"sub_objects") :
                for j in i.sub_objects :
                    if j.tag == tag :
                        return j
        print("failed return by tag")
        return None
    
    #This is for posting to interface server.
    #It provides human participants to know what action is
    #being used by the LLM
    def describeCommandToServer(self, additionalNote = None) :
        data = str(self.action)

        print(f"The additional Note is {additionalNote}")

        if additionalNote is not None:
            data += f" {additionalNote}"

        if self.target.target != None :
            targetDescription = " {}".format(self.target.target.naturalExport(self.depth, 
                                tellPosition = False))
            
            print("the target description is : ", targetDescription)
            data += targetDescription

        print (data)

        self.drone.server.sendCommandDescription(data)

    #This just refreshes the stall timer. The stall timer resets 
    #readiness for connected drones, stopping them from posting images.
    #But also, when stalled, intelligence handler will no longer query the LLM
    def refreshTimer(self, message = None):
        self.timeAlive = time.time()
        self.stall = False
    
    # Returns bool indicating that a user has sent a message
    def userHasSentMessage(self) :
        return not bool(self.drone.server.userChat == "")