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

import time, copy

"""
ObjectFound represents items that have been detected by the object-detection worker(s).
This object encapsulates all data pertinent to objects, position, descriptions, status,
#and temporal proximity.
"""
class ObjectFound() :
    def __init__(self, text, tag, droneRotationState = 0):
        self.tag = tag
        self.isTarget = False
        self.lastFoundRotation = copy.deepcopy(droneRotationState)

        objectInfo = text.split(';')
        generalInfo = tuple(objectInfo[0].split(','))

        name = tuple(generalInfo[0].split(':'))
        self.generalObjectName = name[0]

        #means there exists more detail. 
        #Example if object is a person, and if the object
        #is Jake. specificName would note Jake
        if len(name) == 2 :
            self.specificName = name[1]

        generalObjectPos = generalInfo[1:]
        self.midpoint = (int(generalObjectPos[0]),int(generalObjectPos[1]))
        self.timeUpdated = time.time()

        self.objectOld = False
        self.tooOldTimer = 8

        #justs gets distance at midpoint.
        #should be adjusted to account for more pixels
        # already processed general infos
        sub_objectInfo = objectInfo[1:]

        #If object has sub-objects, like person has hands
        #means it is the primary object
        if len(objectInfo) > 1:
            self.sub_objects = []
            tagVal = 1
            for i in sub_objectInfo :
                self.sub_objects.append(ObjectFound(i, tag+tagVal))
                tagVal+=1

    #Checks object status, and then deduces a time that it takes for status 
    # to change. If time exceeds status related time allowance,then object is demoted.  
    def tooOld(self) :
        demoteTimer = self.tooOldTimer/4

        if self.objectOld :
            demoteTimer = self.tooOldTimer 
        elif self.isTarget :
            demoteTimer = self.tooOldTimer/7

        return (time.time() > (self.timeUpdated + demoteTimer))
    
    #This is used when comparing recently found objects to known objects. 
    #If the two compared objects have similar sub-objects, then 
    #it increases the similarity value between the objects. 
    #If the objects are similar enough, then some of the attributes of the known, 
    #older object is updated, and the object time related status is renewed. Additionally,
    #the other compared object is deleted and forgotten.  
    def similarSubObjects(self, otherObject) :
        similarValue = 0
        VALUE_FOR_SAME_SUB = 20
        tempVal = 0
        if hasattr(self,"sub_objects") and hasattr(otherObject,"sub_objects") :
            for i in self.sub_objects :
                for j in otherObject.sub_objects :
                    #if same specific name, features are updated
                    # and full similar value given
                    if hasattr(self,"specificName") :
                        if i.specificName == j.specificName :
                            i.updateToOtherObject(j)
                            similarValue += VALUE_FOR_SAME_SUB
                            continue

                    #if just generally similar only gets partial value
                    if i.generalObjectName == j.generalObjectName :
                        sinceUpdated = time.time() - i.timeUpdated
                        tempVal = VALUE_FOR_SAME_SUB - i.difInPos(j) - sinceUpdated
                        # if tempVal > 0 : 
                        similarValue += tempVal
        return similarValue

    #Used to check the similarity of the objects. Similarity is determined by 
    #comparing the attributes of the two obects, looking into :
    #name, specificName, position, sub-objects. Similarity is used in determining
    #to update the object 
    def similarityCheck(self, otherObject) :
        objectDissimilarity = 0
        if not self.generalObjectName == otherObject.generalObjectName : 
            objectDissimilarity = 100
        
        if hasattr(self,"specificName") and hasattr(otherObject,"specificName") :
            if self.specificName == otherObject.specificName : 
                objectDissimilarity = -100
        
        percentDifInPos = self.difInPos(otherObject)
        objectDissimilarity += percentDifInPos + (time.time() - self.timeUpdated) - (self.similarSubObjects(otherObject))
        return objectDissimilarity
    
    def difInPos(self, otherObject) :
        return (percentDif(self.midpoint[0],otherObject.midpoint[0]) + 
                    percentDif(self.midpoint[1],otherObject.midpoint[1]))/2
    
    #If the objects are similar, and are the most similar of all the 
    #similar objects, then this object, the known object, is updated.
    def updateToOtherObject(self, otherObject) :
        self.timeUpdated = time.time()
        self.midpoint = otherObject.midpoint
        self.lastFoundRotation = otherObject.lastFoundRotation
        self.objectOld = False
        
        if hasattr(self, "targetTime") :
            del self.targetTime

        return self

    # Get's most similar object from the group of given objects
    #then updates this object respectivly to the
    #most similar. 
    def updateObject(self, otherObjects, threshold = 60) :
        lowestValue = threshold
        lowestObj = None
        objectsThatAreTooSimilar = []
        for i in otherObjects :
            difValue = self.similarityCheck(i)

            if difValue < threshold :
                objectsThatAreTooSimilar.append(i)

            if difValue < lowestValue :
                lowestObj = i
                lowestValue = difValue
        
        if lowestObj != None :
            self.updateToOtherObject(lowestObj)

            for i in objectsThatAreTooSimilar :
                otherObjects.remove(i)
                del i

            return lowestObj, otherObjects
        return None, otherObjects
    

    #Describes object in natural language, which is used in providing
    #context to the LLM worker.
    def naturalExport(self, matrix, target = None, tellPosition = True) :
        output = str(self.generalObjectName)

        if tellPosition :
            output = ("Object {} : {} is postitioned {} ".
                    format(self.tag, self.generalObjectName, 
                            self.whereInView(matrix, target)))
        
        if hasattr(self,"specificName") :
            output += "that is {}".format(self.specificName)
        if hasattr(self,"sub_objects") :
            if not self.sub_objects == [] :
                addAnd = False
                output += " with "
                for i in self.sub_objects :
                    output += i.naturalExport(matrix)
                    if addAnd : output += " and "
                    else : addAnd = True
        return output
    
    #Utilized in naturalExport to add further detail regarding the position.
    def whereInView(self, matrix, target = None) :
        #getting decompressed matrix

        #Matrix needs to be ready because using data in 
        #that object.
        if (not matrix.ready) or self.objectOld : 
            return "somewhere"

        dimensions = matrix.getImageShape()
        initx = int(dimensions[0]/2)
        inity = int(dimensions[1]/2)

        if target is None :
            relx = (self.midpoint[0]/initx) - 1
            rely = (self.midpoint[1]/inity) - 1
        
        #Just checking before
        elif hasattr(target, "midpoint"):
            relx = (target.midpoint[0]/initx) - 1
            rely = (target.midpoint[1]/inity) - 1
        else : return "somewhere"
        
        output = ""

        descriptionOfX = None
        if abs(relx) > float(1/3) : 
            sign = relx/abs(relx)
            descriptionOfX = ("left" if sign == -1 
                              else "right")
        descriptionOfY = None
        if abs(rely) > float(1/3) : 
            sign = rely/abs(rely)
            descriptionOfY = ("top" if sign == -1 
                              else "bottom")
        
        if descriptionOfY != None:
            output += descriptionOfY
        
        if descriptionOfX != None :
            if output != "" :
                output += ' '
            output += descriptionOfX
            
        output += ("center" if output == "" 
                   else " side")

        return "in the {} of your vision".format(output)

def percentDif(x, y) :
            return abs((x - y)/((x+y)/2))