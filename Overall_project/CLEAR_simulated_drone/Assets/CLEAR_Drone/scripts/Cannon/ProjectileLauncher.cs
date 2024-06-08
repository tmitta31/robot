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

public class ProjectileLauncher : MonoBehaviour
{
    public GameObject projectilePrefab; // Drag your projectile prefab here in the inspector
    public float launchForce = 20f; // The magnitude of the force applied to the projectile
    public float projectileLifetime = 10f; // Lifetime of the projectile in seconds
    public Camera mainCamera; // The camera used to calculate click positions. Typically your main camera

    public void SimulateClick(Vector2 screenPosition)
    {
        // Convert screen position to a ray
        Ray ray = mainCamera.ScreenPointToRay(screenPosition);
        RaycastHit hit;

        // Perform raycasting
        if (Physics.Raycast(ray, out hit))
        {
            // Calculate direction from the camera's position to the hit point
            Vector3 direction = hit.point - mainCamera.transform.position;

            // Normalize the direction
            direction.Normalize();

            // Launch the projectile in the calculated direction
            LaunchProjectile(direction);
        }
    }

    void LaunchProjectile(Vector3 direction)
    {
        // Instantiate a projectile at the camera's position
        GameObject projectile = Instantiate(projectilePrefab, mainCamera.transform.position, Quaternion.identity);

        // Set the projectile to the Projectile layer (Optional: see previous scripts for setup)
        projectile.layer = 2;
        // LayerMask.NameToLayer("Projectile");

        // Check if the projectile has a Rigidbody component
        Rigidbody rb = projectile.GetComponent<Rigidbody>();
        if (rb != null)
        {
            // Apply force to move the projectile
            rb.AddForce(direction * launchForce, ForceMode.Impulse);
            Destroy(projectile, projectileLifetime);

        }
        else
        {
            Debug.LogError("Projectile does not have a Rigidbody component.");
        }
    }
}
