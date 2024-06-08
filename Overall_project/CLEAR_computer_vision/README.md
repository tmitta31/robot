# CLEAR_computer_vision
CLEAR computer vision generates system-understandable perceptual awareness utilized by the coordinator in governing robot response. This software defines two services the CLEAR project uses: CLEAR object detection, and CLEAR depth perception.
 
These services connect to the worker server and listen for image uploads. When a new image is uploaded to the worker server, both of the services retrieve the newly uploaded image from their designated depo. Uploaded images are copied into depth perception and object detection depo. Further, there may exist multiple simultaneously running services of both varieties; for example, a CLEAR project may run two object detection services and three depth perception services. In the case of duplicate services, a First Come First Serve schedule will be used.
 
CLEAR object detection transmutes raw visual data into contextual information defined in natural language. This service helps write the prompts provided to the LLM used for controlling the CLEAR system. 
 
Use CLEAR object detection on a UNIX-based system in a Python 3.8 interpreter accompanied by the packages expressed in setup/requirements.txt. Further, download CUDA toolkit 11.4 onto your system: https://developer.nvidia.com/cuda-11-4-0-downloadarchive?target_os=Linux&target_arch=x86_64. To run the service, use
``python main.py --address <address>``
 
CLEAR depth perception transmutes raw visual data into a depth matrix the coordinator uses for basic object avoidance. Use CLEAR depth perception on a UNIX-based system in a Python 3.8 interpreter accompanied by the packages expressed in setup/requirements.txt. To run the service use
``python main.py --address <address> --type dep``
 
Currently defined configuration:
The object detection service employs ultralytics yolov8, https://github.com/ultralytics/ultralytics
 
The depth perception service employs nianticlabs' monodepth2, https://github.com/nianticlabs/monodepth2
 
However, the systems just expressed above can be easily swapped for other similar systems. In the case of changing parts, ensure that the final output provided to the worker server matches the necessary format.

-----

DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
 
This material is based upon work supported by the Under Secretary of Defense for Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Under Secretary of Defense for Research and Engineering.

© 2023 Massachusetts Institute of Technology.

Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

The software/firmware is provided to you on an As-Is basis

SPDX-License-Identifier: MIT
