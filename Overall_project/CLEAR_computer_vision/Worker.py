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

import cv2, importlib.util
import numpy as np

def makeWorker(wtype, url):
    return MyWorker(wtype)(url)

#there's an object detection model, 
#and a depth perception model
def returnWorkerType(key):
    module_name = None
    class_name = None

    if key == "obj":
        module_name = "ObjectDetection.DetectiveWork"
        class_name = "DetectiveWork"
    elif key == "dep":
        module_name = "DepthPrediction.DepthWork"
        class_name = "DepthWork"
    else:
        print(key)
        assert(True)

    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def MyWorker(wtype) :
    class Worker(returnWorkerType(wtype)) :
        def __init__(self, url) -> None:
            self.apiURL = url
            self.ready = True
            self.setUp() 

        # making understandable image from web request
        def transmuteToImage(self, response) :
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            # img.save("test.jpeg")
            cv2.imwrite("test.jpeg", img) 
            return img
    return Worker
