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
class Target():
    def __init__(self, screenDimension, depth):
        self.active = False
        self.screenWidth = screenDimension
        self.target = None
        self.depth = depth
        # self.lock = threading.Lock()

    def updateScreenDimensions(self, screenWidth):
        self.screenWidth = screenWidth

    #Sets the target to no longer be considered
    #active. This then stops tracking processes
    def setUnactive(self) :
        self.active = False

    #Sets the perceieved distance between the drone
    #and the target. To clarify, does not tell
    #movement to maintain this distance, but instead
    #just notes the current distance between the drone and 
    #the object. 
    def setDistance(self, distance) :
        self.distance = distance
    
    #Sets the target to be a certain object, updating the 
    #the target, alongside the object which was 
    #selected to be the target. 
    def setTarget(self, target, depth) :
        self.target = target
        self.midpoint = self.target.midpoint
        self.target.isTarget = True
        self.distance = self.depth.getElement((self.midpoint[1],self.midpoint[0]))

        self.target.timeUpdated = time.time()
        self.active = True
        text = self.target.generalObjectName

        print("target set to ".format(str(text)))

    # def getTarget(self) :
    #     self.lock.acquire(blocking=True)

    #     self.commandLock.release()

    #updates the lastfound position of the target.
    def updateTarget(self, midpoint) :
        self.midpoint = midpoint 
        self.distance = self.depth.getElement((self.midpoint[1],self.midpoint[0]))

    
    #checks if the target midpoint x position is within 
    #10% of the midpoint of the screen. 
    def facingTheTarget(self, threshold = .10) :
        midwidthImg = self.screenWidth/2
        dif = self.target.midpoint[0] - midwidthImg
        if abs(dif/midwidthImg) < threshold :
            return True
        return False
    