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

from Drones.GeneralSupport.Exceptions.WrongDrone import WrongDrone
import time

class GeneralDrone() :
    WrongDrone = WrongDrone
    def __init__(self) ->None:
        # Error handling for wrong drone being used
        # self.WrongDrone = WrongDrone

        self.imageParts = {}
        self.image = None
        self.rotation = None
        self.droneIsRunning = True
        self.name = "woag"
        self.waitingForCamChange = False
        
        if self.handlesImages:
            self.waitingForImage = True
            self.image = self.getImage()
        else :
            self.waitingForImage = False

        self.getRotation()
        self.speed = 1
    
    #Checks if busy. If busy will return true
    #but also it will ask if actually busy.
    def checkIfCommandOccuring(self) : 
        if not self.server.commandOccuring :
            return False
        
        self.getState()
        return True

    def startingStateChange(self) :
        self.movementController.stopMovement(True)
        self.sendMovementControls(0,0,0,0)
        DELAY = 1
        time.sleep(DELAY)

    def getState(self, foo = None) :
        self.server.sendInstructions("state?")

    # should make it just call for image to be sent 
    def getImage(self):
        self.image = self.server.getImage()
        return self.image

    def getRotation(self) :
        rawRotation = self.server.getRotation()
        if rawRotation == None : 
            self.currentYawRotation = self.currentRotation = 0
        else :
            self.currentRotation = stringToInArray(self.server.getRotation())
            self.currentYawRotation = self.currentRotation[1]
        return self.currentRotation
    
def stringToInArray(s):
    parts = s.split(',')
    ints = [float(part) for part in parts]
    return ints
