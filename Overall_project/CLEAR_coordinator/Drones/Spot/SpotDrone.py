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

from Drones.Spot.DroneServer import DroneServer
from MovementControllers.TerrestrialController.TerrestrialController import MovementController
from Drones.GeneralSupport.GeneralDrone import GeneralDrone
import copy, time

class SpotDrone(GeneralDrone) :
    def __init__(self, interfaceUrl, handlesImages=False) ->None:
        # If image is being sent conventionally.
        # From drone->interface->coordinator->worker.
        # If false:
        # drone->interface->worker
        self.handlesImages = handlesImages
        self.NAME = "Spot"

        self.server = DroneServer(interfaceUrl, self)
        super().__init__()
        self.GPT_SET_UP = "Drones/Spot/llmInfo/gptCharacter"
        self.GPT_EVOLUTION = "Drones/Spot/llmInfo/gptProgress"
        self.FPS = 30
        self.FOV = 60
        self.isStanding = False
        self.specificActions = [{"stand" : self.stand}, 
                                {"sit" : self.sit},
                                {"dock" : self.dock},
                                {"getState" : self.getState},
                                {"grab" : self.grabObject},
                                {"changeCam" : self.switchCamera} ]
        
        self.TOO_CLOSE_TARGET_DISTANCE = 1.5
        self.TOO_CLOSE_GENERAL_DISTANCE = 0.9
        self.SLOW_DOWN_RANGE = 2

        self.timeSinceCamChange = 0
        self.TIME_FOR_CAM_CHANGE = 5
        
        self.queryIfOperating = self.queryIfStanding

        self.PROPORTIONAL_GAIN = 0.005
        self.INTEGRAL_GAIN = 0.0
        self.DERIVATIVE_GAIN = 0.01

        self.UNINTERRUPTIBLE_ACTIONS = ["dock", "grab"]

        # self.CONDITION_ACTIONS = [{"grab" : self.server.grabReady}]

        self.OBJECTS_TO_IGNORE = ["umbrella", "skateboard", "airplane", "bed", 
                                  "car", "bird", "potted plant", "boat", "motorcycle", "couch"]
        
        self.movementController = MovementController(self)
        self.NEEDS_HUMAN_APPROVAL = True

    def stand(self, foo) :
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return 
        
        self.startingStateChange()
        self.server.sendInstructions("stand")
        self.movementController.completedAction()
        self.isStanding = True

    def sit(self, foo) :
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return  

        self.startingStateChange()
        self.server.sendInstructions("sit")
        self.movementController.completedAction()
        self.isStanding = False

    #Grab object is called by the llm
    #it will simulate a user click for the web client
    def grabObject(self, target = None, userTarget = None) :
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return 
        
        self.startingStateChange()

        # Was not in grab mode when starting command
        if not self.server.grabReady:
            while not self.server.grabReady:
                self.server.sendInstructions("readyGrab")
                self.getState()
            return
            
        try :
            if target is not None :
                point = copy.deepcopy(target.midpoint)
            elif userTarget is not None:
                point = userTarget
            else : 
                print("no inputs for grab")
                return

            print("grabbing at {}".format(point))
            self.server.postClick(point)
        except Exception as e:
            print(f"EXCEPTION with grabbing {e}")

    def dock(self, foo = None) :
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return  

        self.server.sendInstructions("dock")
        self.movementController.completedAction()
    
    def switchCamera(self, foo = None, reset = False):
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return 
        
        DELAY_BETWEEN_SWAP = 10
        self.startingStateChange()
        if hasattr(self, "timeCameraSwitched"):
            if self.timeCameraSwitched + DELAY_BETWEEN_SWAP > time.time():
                self.movementController.completedAction()
                return

        if reset or self.server.grabReady:
            while self.server.grabReady:
                self.server.sendInstructions("readyRegCam")
                self.getState()
        else:
            while not self.server.grabReady:
                self.server.sendInstructions("readyGrab")
                self.getState()
        
        self.timeCameraSwitched = time.time()
        self.movementController.completedAction()

    def sendMovementControls(self, left_right_velocity, for_back_velocity,
     vertical_velocity, yaw_velocity, setCam = True) :
        
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return 
        
        input = [left_right_velocity, for_back_velocity,
                  vertical_velocity, yaw_velocity]
        
        print("sending movement ", input)
        self.server.sendMovement(input)

    def queryIfStanding(self, askForText = False) :
        if askForText :
            if self.isStanding :
                return "You are standing and can move"
            return "You are sitting and cannot move"
        
        return self.isStanding
    
    def approveAction(self, action, targetGeneralName):
        if (action == "grab" and targetGeneralName == "person") :
            return False
        return True
    
    def manualControls(self, arr=None) :
        if arr is None: return None
        
        if ' ' in arr:
            if self.queryIfOperating() :
                return "sit"
            else:
                return "stand"
        if 'x' in arr:
            return "dock"
        if '0' in arr:
            return "getState"
        return None
        