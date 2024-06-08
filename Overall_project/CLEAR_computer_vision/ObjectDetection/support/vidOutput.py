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

from moviepy.editor import *
from pathlib import Path
import cv2
import numpy as np
  

# since moviepy.editor using RGB channels, while 
# openCV uses BGR, we need to need to shift things
def shiftChannels(images) :
    for i in range(len(images)) :
        images[i] = cv2.cvtColor(images[i],cv2.COLOR_BGR2RGB)
    return images

def makeVideo(images):

    images = shiftChannels(images)
    img_clips = []

    fps = 24

    for i in images :
        slide = ImageClip(i,duration=1/fps)
        img_clips.append(slide)

    #concatenating slides
    video_slides = concatenate_videoclips(img_clips, method='compose', )
    #exporting final video
    video_slides.write_videofile("output_video.mp4", fps)

def makeMedia(media) :
    if type(media) == "List" :
        makeVideo(media)
        return
    cv2.imwrite("output/" + "output" + ".jpg", media)
    cv2.imshow("Result", media)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
