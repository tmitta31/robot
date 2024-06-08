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

from urllib3.exceptions import InsecureRequestWarning
import warnings
warnings.simplefilter('ignore', InsecureRequestWarning)
from Drones.GeneralSupport.GeneralDroneServer import DroneServer as DS

# Need to move spot specific things into this class.
# Takeout of the generic which currently houses it 
class DroneServer(DS):
    def __init__(self, interfaceUrl, drone) -> None:
        self.interfaceAddress = interfaceUrl
        super().__init__(self.interfaceAddress, drone)
        self.grabReady = False

    #Can be spurred by either roboclick or user click being vouched.
    #Means there will be a grab command sent to the drone
    def userClickUpdated(self, message):
        #If waiting for roboclicked to be vouched for
        # being at this function means it was vouced for

        url = "{}/click".format(self.URL)
        response = self.session.get(url, verify=False)
        data = response.json()
        print("The data for user click is {}".format(data))
        click = data["click"]

        point = (click['x'], click['y'])

        if response.status_code == self.GOOD_CODE:
            self.sendInstructions("grab{}".format(point))
        else :
            print("Failed to get click: status code", response.status_code)

    def considerUserClick(self, message):
        # This click was proposed by a web user
        url = "{}/considerClick".format(self.URL)
        self.drone.movementController.completedAction()

        response = self.session.get(url, verify=False)
        data = response.json()
        print("The data for user click is {}".format(data))
        click = data["click"]
        point = (click['x'], click['y'])
        self.drone.grabObject(userTarget = point)