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

from ObjectDetection.Detector import Detector
from ObjectDetection.support.OutputObj import Output
import requests
from PIL import Image
import cv2

class DetectiveWork() :
    GOOD_CODE = 200
    def setUp(self) :
        self.Detector = Detector()
        self.getURL = '{}/objectImage'.format(self.apiURL)
        self.postURL = '{}/contextInfo'.format(self.apiURL)

        self.identity = "object_detection"
        
        self.session = requests.Session()

    def getObjects(self, threshold, media) :
        self.objects = self.Detector.predictImage(media = media, 
        threshold = threshold)
    
    def runWorker(self) :
        self.ready = False
        response = self.session.get(self.getURL)
        threshold = .5

        # error getting response
        print(response)
        if not response.status_code == self.GOOD_CODE: return
        
        print ("Caught")
    
        self.getObjects(threshold, self.transmuteToImage(response))
        output = Output(self.objects)
        
        if hasattr(output, "objects" ):
            outputString = output.getOutputString()
            response = self.session.post(self.postURL, json={'string': outputString})
            print(response.status_code)
        
        self.ready = True
    
    def testing(self) :
        media = cv2.imread("testingImage/JakeandSpot.jpg")
        media = cv2.cvtColor(media, cv2.COLOR_RGB2BGR)


        self.getObjects(0.5, media)
        output = Output(self.objects)

        if hasattr(output, "objects" ):
            outputString = output.getOutputString()
            print(outputString)

