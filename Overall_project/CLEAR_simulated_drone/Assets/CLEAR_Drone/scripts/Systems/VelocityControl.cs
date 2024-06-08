// DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

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

public class VelocityControl : MonoBehaviour {
    // Reference to state finder which is responsible for updating state variables like velocity, altitude, etc.
	public StateFinder state;

    // Physics constants and parameters
	private float gravity = 9.81f;

	public GameObject referenceObject;


    // Time constants that define the response speed for various controls
	private float time_constant_z_velocity = 1.0f; // Z-axis velocity
	private float time_constant_acceleration = 0.5f;
	private float time_constant_omega_xy_rate = 0.1f; // Roll/pitch rate
	private float time_constant_alpha_xy_rate = 0.05f; // Angular acceleration for roll/pitch
	private float time_constant_alpha_z_rate = 0.05f; // Angular acceleration for yaw

    // Limits on pitch and roll to ensure the small-angle approximation remains valid
	private float max_pitch = 0.175f; // 10 degrees in radians
	private float max_roll = 0.175f; // 10 degrees in radians

	private float max_alpha = 10.0f;

	private float initial_height;

    // Desired velocities and orientations
	public float desired_vx = 0.0f;
	public float desired_vy = 0.0f;
	public float desired_yaw = 0.0f;
	public float desired_height;

    // Variable to store the initial height

	void Start () {
		state.GetState();
		Rigidbody rb = GetComponent<Rigidbody> ();
		Vector3 desiredForce = new Vector3 (0.0f, gravity * state.Mass, 0.0f);
		rb.AddForce (desiredForce, ForceMode.Acceleration);

		desired_height = initial_height = referenceObject.transform.position.y;
	}

	// FixedUpdate is called at fixed intervals to handle physics-related code.
	void FixedUpdate() {

		// Retrieve and update the state of the object (e.g., altitude, angles, velocities).
		state.GetState();

		// Initialize variables for desired angles and desired angular velocities.
		Vector3 desiredTheta;
		Vector3 desiredOmega;

		// Calculate the difference between the current altitude and the desired height.
		float heightError = state.Altitude - desired_height;

		// Calculate the desired velocity based on the desired horizontal velocities and the altitude error.
		Vector3 desiredVelocity = new Vector3(desired_vy, -1.0f * heightError / time_constant_z_velocity, desired_vx);

		// Calculate the difference between the current velocity and the desired velocity.
		Vector3 velocityError = state.VelocityVector - desiredVelocity;

		// Calculate the desired acceleration based on the velocity error and a time constant.
		Vector3 desiredAcceleration = velocityError * -1.0f / time_constant_acceleration;

		// Determine the desired pitch and roll angles using desired acceleration and gravity.
		desiredTheta = new Vector3(desiredAcceleration.z / gravity, 0.0f, -desiredAcceleration.x / gravity);

		// Ensure the desired pitch doesn't exceed the maximum allowed pitch.
		if (desiredTheta.x > max_pitch) {
			desiredTheta.x = max_pitch;
		} else if (desiredTheta.x < -1.0f * max_pitch) {
			desiredTheta.x = -1.0f * max_pitch;
		}

		// Ensure the desired roll doesn't exceed the maximum allowed roll.
		if (desiredTheta.z > max_roll) {
			desiredTheta.z = max_roll;
		} else if (desiredTheta.z < -1.0f * max_roll) {
			desiredTheta.z = -1.0f * max_roll;
		}

		// Calculate the difference between the current angles and the desired angles.
		Vector3 thetaError = state.Angles - desiredTheta;

		// Calculate desired angular velocities based on angle error and a time constant.
		desiredOmega = thetaError * -1.0f / time_constant_omega_xy_rate;
		desiredOmega.y = desired_yaw;

		// Calculate the error in the angular velocity.
		Vector3 omegaError = state.AngularVelocityVector - desiredOmega;

		// Determine desired angular acceleration based on the angular velocity error and time constants.
		Vector3 desiredAlpha = Vector3.Scale(omegaError, new Vector3(-1.0f / time_constant_alpha_xy_rate, -1.0f / time_constant_alpha_z_rate, -1.0f / time_constant_alpha_xy_rate));

		// Ensure the desired angular acceleration doesn't exceed the maximum value.
		desiredAlpha = Vector3.Min(desiredAlpha, Vector3.one * max_alpha);
		desiredAlpha = Vector3.Max(desiredAlpha, Vector3.one * max_alpha * -1.0f);

		// Calculate the desired thrust based on gravity, desired acceleration, and the current angles.
		float desiredThrust = (gravity + desiredAcceleration.y) / (Mathf.Cos(state.Angles.z) * Mathf.Cos(state.Angles.x));
		desiredThrust = Mathf.Min(desiredThrust, 2.0f * gravity);
		desiredThrust = Mathf.Max(desiredThrust, 0.0f);

		// Calculate the desired torque and force based on the desired angular acceleration and inertia.
		Vector3 desiredTorque = Vector3.Scale(desiredAlpha, state.Inertia);
		Vector3 desiredForce = new Vector3(0.0f, desiredThrust * state.Mass, 0.0f);

		// Apply the desired torque and force to the object's rigidbody.
		Rigidbody rb = GetComponent<Rigidbody>();
		rb.AddRelativeTorque(desiredTorque, ForceMode.Acceleration);
		rb.AddRelativeForce(desiredForce, ForceMode.Acceleration);
	}



	// Resets the state and velocities
	public void Reset() {

		state.VelocityVector = Vector3.zero;
		state.AngularVelocityVector = Vector3.zero;

		desired_vx = 0.0f;
		desired_vy = 0.0f;
		desired_yaw = 0.0f;
		desired_height = initial_height;
		state.Reset ();
	}

}
