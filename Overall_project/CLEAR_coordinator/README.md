# CLEAR_coordinator

The CLEAR coordinator serves as the system middleman, collecting, analyzing, and sending data between the interface and worker server while dictating robot behavior. One such process occurs with handling image data: images are captured by the drone and then sent to the interface server; from here, it is provided to the coordinator, which then shares it with the worker server. The computer vision services then turns this visual data into contextual information. Following this, the computer vision gives the worker server this context, which the coordinator collects. The coordinator then uses this context to create a robotic response command, which is then shared with the interface server and redistributed to the robot for execution. Further, the coordinator controls the robot through a layer of abstraction, yielding high-level robot instructions regarding movement and specific commands that will be interpreted by the services directly attached to the robot.
 
Run CLEAR coordinator on a Windows or Unix system in a Python 3.8 interpreter accompanied by the packages expressed in setup/requirements.txt. To run the service, use
 
``python main.py --worker_address <web address> --interface_address < web address > --platform <UnityDrone||SpotDrone>``
 
Alternatively, you can run the script through the CLEAR_setup services.
 
Also, do ensure you run this system only after starting the interface server, worker server, and llm chat services.
 
-----

DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
 
This material is based upon work supported by the Under Secretary of Defense for Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Under Secretary of Defense for Research and Engineering.

© 2023 Massachusetts Institute of Technology.

Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

The software/firmware is provided to you on an As-Is basis

SPDX-License-Identifier: MIT
