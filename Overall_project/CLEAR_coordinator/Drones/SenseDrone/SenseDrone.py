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

from Drones.SenseDrone.DroneServer import DroneServer
from MovementControllers.AerialController.AerialController import MovementController
from Drones.GeneralSupport.GeneralDrone import GeneralDrone

class SenseDrone(GeneralDrone) :
    def __init__(self, interfaceUrl, handlesImages=False) ->None:
        self.PROPORTIONAL_GAIN = 0.01
        self.INTEGRAL_GAIN = 0.0
        self.DERIVATIVE_GAIN = 0.02

        self.isAerial = True
        self.specificActions = []
        
        self.queryIfOperating = self.queryIfFlying

        self.TOO_CLOSE_TARGET_DISTANCE = 1.2
        self.TOO_CLOSE_GENERAL_DISTANCE = 0.9
        self.SLOW_DOWN_RANGE = 2

        self.ACTIONS_NEED_APPROVAL = True
        self.NAME = "SenseDrone"
        
        self.UNINTERRUPTIBLE_ACTIONS = []

        self.movementController = MovementController(self)
        # If image is being sent conventionally.
        # From drone->interface->coordinator->worker.
        # If false:
        # drone->interface->worker
        self.handlesImages = handlesImages
        self.server = DroneServer(interfaceUrl, self)
        super().__init__()

        self.GPT_SET_UP = f"Drones/{self.NAME}/llmInfo/gptCharacter"
        self.GPT_EVOLUTION = f"Drones/{self.NAME}/llmInfo/gptProgress"
        self.FPS = 30
        self.FOV = 60
        self.NEEDS_HUMAN_APPROVAL = False

        self.CORDINATE_WITH_OTHER_CLEAR_SYSTEM = True
    
    def sendMovementControls(self, left_right_velocity, for_back_velocity,
     vertical_velocity, yaw_velocity) :
        
        if (self.checkIfCommandOccuring() or 
          self.server.waitingForClickResponse): 
            return 
                
        input = [yaw_velocity, vertical_velocity, 
                 for_back_velocity, left_right_velocity]

        print(f"Movement input is: \n{input}")

        self.server.sendMovement(input)
    
    def coordinateWithOtherClear(self):
        """
        When there are multiple CLEAR systems working together, this function handles
        generating context for the other active CLEAR systems. It will relay meta objects 
        detected by this clear system to other systems. 
        """

        



    
    def queryIfFlying(self, askForText = False) :
        if askForText :
            return "You are flying and can move"
        return True