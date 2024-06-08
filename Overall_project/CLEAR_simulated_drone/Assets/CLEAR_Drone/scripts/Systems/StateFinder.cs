﻿// DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

// This material is based upon work supported by the Under Secretary of Defense for 
// Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions,
// findings, conclusions or recommendations expressed in this material are those 
// of the author(s) and do not necessarily reflect the views of the Under 
// Secretary of Defense for Research and Engineering.

// © 2023 Massachusetts Institute of Technology.

// Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

// The software/firmware is provided to you on an As-Is basis

// Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS Part 
// 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, 
// U.S. Government rights in this work are defined by DFARS 252.227-7013 or 
// DFARS 252.227-7014 as detailed above. Use of this work other than as specifically
// authorized by the U.S. Government may violate any copyrights that exist in this work.

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// The StateFinder class appears to be responsible for tracking and 
// providing the current state of the drone in terms of physical properties 
// such as position, orientation, velocities, inertia, and mass.
[System.Serializable]
public class StateFinder : MonoBehaviour {
	public float Altitude; // The current altitude from the zero position
	public Vector3 Angles;
	public Vector3 VelocityVector; // Velocity vector
	public Vector3 AngularVelocityVector; // Angular Velocity
	public Vector3 Inertia;
	public float Mass;

	private bool flag = true; // Only get mass and inertia once 

	public VelocityControl vc; // linked externally

	// Fetches the state of the drone including its current orientation, position, and velocities
	public void GetState() {
		Vector3 worldDown = vc.transform.InverseTransformDirection (Vector3.down);
		float Pitch = worldDown.z; // Small angle approximation
		float Roll = -worldDown.x; // Small angle approximation
		float Yaw = vc.transform.eulerAngles.y;

		Angles = new Vector3 (Pitch, Yaw, Roll);

		Altitude = vc.transform.position.y;

		VelocityVector = vc.transform.GetComponent<Rigidbody> ().velocity;
		VelocityVector = vc.transform.InverseTransformDirection (VelocityVector);

		AngularVelocityVector = vc.transform.GetComponent<Rigidbody> ().angularVelocity;
		AngularVelocityVector = vc.transform.InverseTransformDirection (AngularVelocityVector);

		if (flag) {
			Inertia = vc.transform.GetComponent<Rigidbody> ().inertiaTensor;
			Mass = vc.transform.GetComponent<Rigidbody> ().mass;
			flag = false;
		}
	}
	
    // Reset the state information
	public void Reset() {
		flag = true;
		VelocityVector = Vector3.zero;
		AngularVelocityVector = Vector3.zero;
		Angles = Vector3.zero;
		Altitude = 0.0f;

		enabled = true;
	}
}
