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

from skimage.transform import resize
import numpy as np

# DepthMatrix is applied to all operations involving to 
# depth perception. Depth data is provided by a depth-perception
# worker, in a heavily compressed form dissimilar to
# the shape of the image data provided by the drone. This
# compressed format lessens bandwidth costs, while preserving
# a general idea of the data. Additionally, it reduces 
# computational burden in processing done within the controller.

class DepthMatrix() :
    def __init__(self, pseudimensions):
        self.matrix = None
        self.ready = False
        self.scaledMatrix = None
        self.displayingMatrix = True
        self.generalDist = 100

        # just dimensions of image, but this sounds cool
        
        self.pseudimensions = pseudimensions

    #Overrides the equallity function
    def __eq__(self, value) :
        return self.matrix == value
    
    def getImageShape(self) :
        return self.pseudimensions
    
    def updateDimensions(self, dimensions):
        self.pseudimensions = dimensions
    
    # sets the matrix value equal to the the value provided,
    # and determines the size ratio of the depth matrix with
    # the raw image of the produced by the drone.
    def setTo(self, value) :
        if not self.ready :
            self.setScaling(value)
        self.matrix = value
        self.ready = True
        self.depthAnalysis()

        if self.displayingMatrix :
            self.scaledMatrix = self.decompressedMatrix()
    
    # Determines the size ration between the depth matrix 
    # and the drone image 
    def setScaling(self, value) :
        self.scaleW = self.pseudimensions[0]/value.shape[0]
        self.scaleH = self.pseudimensions[1]/value.shape[1]
    
    #Returns a matrix shaped akin to the raw drone image input. 
    #Rescales the depth matrix to match image input.
    #Used by functions internal to this object.Should not be called 
    #elsewhere. Would be cool if objects could have private attributes in python
    def decompressedMatrix(self) :
        matrix = self.matrix.astype(np.float32)
        return resize(matrix, self.pseudimensions, 
                      mode='reflect', anti_aliasing=True)
    
    #Returns a matrix shaped akin to the raw drone image input. 
    #Rescales the depth matrix to match image input.
    #Can be called by anything external, or internal to this object.
    def getMatrix(self) :
        if not self.ready :
            return "not ready"
        
        if not self.displayingMatrix :
            self.displayingMatrix = True
        self.scaledMatrix = self.decompressedMatrix()
        
        if type(self.scaledMatrix) == None :
            print("bad news bears there is no matrix")
            return None
        # print ("Matrix generated : \n {}".format(self.scaledMatrix))
        return self.scaledMatrix
    
    #Returns a value from a specified location in the matrix.
    def getElement(self, position) :
        return self.matrix[int(position[0]/self.scaleW)][int(position[1]/self.scaleH)]
    
    #depthAnalysis is used to gauage the genreral distance between the drone 
    #and its surrounding environment. Weighs elements closer to the middle higher than border elements
    #in determining distance. Intended to prevent drone from running into the environment
    def depthAnalysis(self) : 
        midI = int(len(self.matrix)/2)
        midJ = int(len(self.matrix[0])/2)

        total = 0
        lowestVal = 10000
        highestVal = 0

        maxDist = midI + midJ
        summation = 0

        for i in range(len(self.matrix)) :
            for j in range(len(self.matrix[0])) :
                distance = abs(midI - (i+1)) + abs(midJ - (j+1))

                summation += self.matrix[i][j]
                
                # plus two because starting from 0
                total += (self.matrix[i][j]) * abs((distance)/(maxDist) -1) 
                if self.matrix[i][j] < lowestVal :
                    lowestVal = self.matrix[i][j]
                if self.matrix[i][j] > highestVal :
                    highestVal = self.matrix[i][j]
        
        numOfElements = len(self.matrix) * len(self.matrix[0])
        self.generalDist =  total/(numOfElements)
        self.averageDist = summation/(numOfElements)
        
        for i in range(len(self.matrix)) :
            for j in range(len(self.matrix[0])) :
                x = self.matrix[i][j] - self.averageDist
        self.standardDev = pow(x,2)/(numOfElements-1)

        # print("The standard deviation is : {}".format(self.standardDev))

        
        # print ("the general apox value {}".format(self.generalDist))

        #If wanting to print out details
        # print (("highest value {} the lowest value {} the general apox value {}").
        #        format(highestVal, lowestVal, self.generalDist))
