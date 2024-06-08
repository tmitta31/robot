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

from ObjectDetection.SubClassDetector import *
from ObjectDetection.support.Object import Object as Obj
from ultralytics import YOLO
from PIL import Image
import requests
import os

class Detector:
    # -> None ensures that the constructor returns None value
    def __init__(self) -> None:

        yoloPath = "ObjectDetection/models/yolov8x.pt"
        try :
            self.model = YOLO(yoloPath)
        except Exception as e :
            url = (os.environ.get('WORKER_ADDRESS') 
                   + "/download/yolov8x.pt")
            print("Error with the GitHub API, user has overused git pull.\n"\
                   ,"Either wait, or upload the YOLO model to the worker server\n"\
                    ,"at {}".format(url))
            
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                # Write the contents to a file
                with open(yoloPath, 'wb') as f:
                    f.write(response.content)

                self.model = YOLO(yoloPath)
            else :
                assert "Was not able to download the model"

        # once making more models, and having program generated models ->
        #  will load all in array to iterativly load 
        self.humanModel = SubClassDetector("ObjectDetection/models/people")
        self.gesturesModel = SubClassDetector("ObjectDetection/models/hands")

        self.person = []

    def generalObjectDetecting(self, media, threshold = 50) : 
        results = self.model.predict(source=media)  # save plotted images
        names = self.model.names
        return self.getFoundObjects(results, names, media, threshold)
        
    def getFoundObjects(self, results, names, image, threshold) :
        objects = []
        imH, imW, imC = image.shape

        for r in results:
            boxes = r.boxes
            for box in boxes:
                classConfidence = round(100*box.conf[0].tolist())
                classIndex = int(box.cls)
                classLabelText = names[classIndex]

                #y and x was swapped so might be funky on run
                xmin,ymin,xmax,ymax = box.xyxy[0]
                # ymin,xmin,ymax,xmax = box.xyxy[0]


                xmin, xmax, ymin, ymax = (int(xmin), int(xmax), int(ymin), int(ymax))

                generalObject = Obj(xmin,ymin,xmax,ymax,
                    classLabelText, classConfidence, None)
                if (classLabelText == "person") : 
                    # Slicing to crop the image
                    crop = image[ymin:int(ymax),xmin:xmax]

                    im = Image.fromarray(crop)
                    im.save("woag.jpeg")
                    #In OutputObj, the mid point of the object is related to the given target mid point
                
                    self.humanModel.specify(crop, xmin, ymin)

                    if (self.humanModel.item != None and
                        self.humanModel.item.confidence > threshold) :
                        #labeled as person:specific person name
                        person = Obj(xmin,ymin,xmax,ymax,
                            classLabelText + ':' + self.humanModel.item.classifcation, 
                            self.humanModel.item.confidence,
                            None)

                        generalObject = person

                    self.gesturesModel.specify(crop, xmin, ymin)

                    if (self.gesturesModel.item != None 
                        and self.gesturesModel.item.confidence > threshold) :

                        generalLabel = "hand gesture"
                        gesture = Obj(self.gesturesModel.item.xmin, self.gesturesModel.item.ymin, 
                                    self.gesturesModel.item.xmax, self.gesturesModel.item.ymax,
                                    generalLabel + ':' + self.gesturesModel.item.classifcation, 
                                    self.gesturesModel.item.confidence, None)
                        generalObject.sub_objects.append(gesture)

                objects.append(generalObject)
        return objects

    def predictImage(self, media, threshold) :
        return self.generalObjectDetecting(media, threshold)

