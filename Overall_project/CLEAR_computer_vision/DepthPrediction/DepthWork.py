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

from DepthPrediction.DepthPredict import Detector
from DepthPrediction.OutputDepth import OutputDepth
from PIL import Image
from skimage.transform import resize
import requests
import numpy as np

class DepthWork() :
    GOOD_CODE = 200
    def setUp(self) :
        self.Detector = Detector()
        self.getURL = '{}/depthImage'.format(self.apiURL)
        self.postURL = '{}/depth'.format(self.apiURL)
        self.identity = "depth_perception"
        self.session = requests.Session()
        
    def getDepth(self, media) :
        self.depthnp = self.Detector.predictImage(media)

    def runWorker(self) :
        self.ready = False
        response = self.session.get(self.getURL)

        # error getting response
        if not response.status_code == self.GOOD_CODE: return
        
        self.getDepth(self.transmuteToImage(response))
        output = OutputDepth(self.depthnp).getOutput()

        response = self.session.post(self.postURL, json={'matrix': output.tolist()})
                    
        print(response.status_code)
        self.ready = True

    # just for debugging
    def testing(self) :
        media = Image.open("testingImage/JakeandSpot.jpg")

        originalDim = (media.height, media.width)
        
        self.getDepth(np.array(media))
        output = OutputDepth(self.depthnp).getOutput()

        print (output.shape[0] * output.shape[1] * 4)

        np.savetxt("DepthPrediction//testingOutputs//depthArray.txt", output)

        # Enlarge the matrix back to its original size
        matrix = output.astype(np.float32)

        decompressed_matrix = resize(matrix, originalDim, mode='reflect', anti_aliasing=True)

        self.Detector.makeImage(decompressed_matrix)

