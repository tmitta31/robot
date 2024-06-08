# CLEAR_virtual_drone
The CLEAR virtual drone service is a CLEAR robot implementation directly interfaces with a simulated quadcopter in Unity. The virtual drone service controls the robot according to the coordinator's instructions. The virtual drone service receives various commands from the coordinator, such as velocities, throw, and reset position.
 
Run the CLEAR virtual drone service on a Windows or Unix system. Install Unity and then create a project. Once a scene is ready, import the virtual drone into your project. Additionally, ensure that the address file in launch is in a higher directory from the virtual drone. Further, ensure that the value in address matches the address of the interface server.
 
With Unity, you may either run it from the editor or build the project and then run the build.


It should be noted that since our default object detection model (YOLO v8) is trained on real-world objects, simulated assets in the scene where the quadcopter is placed should be sufficiently realistic that the model would recognize them. Attempts to use the quadcopter in more stylized scenes have shown poor recognition performance.

-----

DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
 
This material is based upon work supported by the Under Secretary of Defense for Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Under Secretary of Defense for Research and Engineering.

© 2023 Massachusetts Institute of Technology.

Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

The software/firmware is provided to you on an As-Is basis

SPDX-License-Identifier: MIT
