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

import cv2, time
import warnings
from ultralytics import YOLO
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings
from ObjectDetection.support.DetectedItem import *
 

class SubClassDetector :
      def __init__(self, name) -> None:
            print('Loading model...', end='')
            start_time = time.time()
            self.detectFn = YOLO("{}.pt".format(name))
            end_time = time.time()
            elapsed_time = end_time - start_time
            print('Done! Took {} seconds'.format(elapsed_time))

      def specify(self, image, startX, startY) :

            print("sub start")
            results = self.detectFn.predict(source=image, conf=0.50, )  # save plotted images
            print ("sub end")
            names = self.detectFn.names

            #Element zero is the highest scoring confidence in scan.
            # return image_with_detections

            if len(results[0].boxes) :
                  objDet = results[0].boxes[0]
                  self.item = (DetectedItem(objDet.xyxy[0], 
                        names[int(objDet.cls)],
                        objDet.conf[0], image, startX, startY))
            else : 
                  self.item = None

