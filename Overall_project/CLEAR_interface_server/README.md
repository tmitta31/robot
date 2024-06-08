# CLEAR_interface_server
The CLEAR interface server integrates human input into the CLEAR system, and also connects the CLEAR coordinator with the robot. The interface server offers a web UI that hosts conversations between users and the robot. This UI supports a two-way messaging service, a view of the robot’s vision, a robot action approval system, and a means for the user to control the robot manually. This screen can be accessed at ``https://<hostname>:7070/views/controller.html``. The interface server also offers API services that connect the robot to the coordinator.
 
Run the interface server on a Windows or Unix-based systems with Node.js 18
Installed. Also, perform the following commands:
``openssl genpkey -algorithm RSA -out key.pem``
``openssl req -new -x509 -key key.pem -out cert.pem -days 365``
 
Following this, place the resulting files into the security directory.
 
To run the service, use
``node serverSecure.js``

-----

DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
 
This material is based upon work supported by the Under Secretary of Defense for Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Under Secretary of Defense for Research and Engineering.

© 2023 Massachusetts Institute of Technology.

Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

The software/firmware is provided to you on an As-Is basis

SPDX-License-Identifier: MIT
