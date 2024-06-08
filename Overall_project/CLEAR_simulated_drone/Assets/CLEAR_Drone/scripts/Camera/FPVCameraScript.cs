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
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

public class MyCertificateHandler : CertificateHandler
{
    protected override bool ValidateCertificate(byte[] certificateData)
    {
        // Your logic here. For example, always return true to bypass certificate validation:
        return true;
    }
}

//FPVCameraScript is responsible for capturing and then sending images to the
//interface server.
public class FPVCameraScript : MonoBehaviour
{
    public Transform droneTransform;  // Reference to the drone's Transform component
    public Vector3 offset;  // The offset from the drone's position
    public string interfaceUrl = "https://localhost:7070";

    // URL for the remote server, localhost URL commented out for local testing
    [Range(0, 1)] public float temp;  // Interpolation factor for Slerp operation
    [Range(0, 1)] public float rpLimitRatio;  // Ratio for roll and pitch limits
    private bool serverReady = false;  // Indicates if the server is ready
    private bool takingPicture = false;  // Flag for whether a picture is being taken
    private bool sendingReady = false;
    private float imageTimer = 0;  // Timer for checking server status
    private float readyTimer = 0;  // Timer for checking server status

    Camera cam;  
    
    // Name of the class defined in the Coordinator service
    public string nameOfControllerClass = "UnityDrone";

    private Texture2D lastSentImage;

    void Start() {
        ServicePointManager.ServerCertificateValidationCallback = MyRemoteCertificateValidationCallback;
        cam = GetComponent<Camera>();  // Get the Camera component at the start

        Debug.Log(webUrl);

        if (webUrl == null)
        {
            Debug.LogError("Could not find or read the web URL from the config. Using a default value.");
        }
    }

    public bool MyRemoteCertificateValidationCallback(System.Object sender, X509Certificate certificate, 
                                                    X509Chain chain, SslPolicyErrors sslPolicyErrors)
    {
        return true;
    }

    void Update() {
        CheckServerStatus();  // Check server status in each frame

        // Update the camera's position based on the drone's position and rotation
        transform.position = droneTransform.position + droneTransform.rotation * offset;

        // Fetch the drone's rotation in Euler angles
        Vector3 euler = droneTransform.rotation.eulerAngles;

        // Normalize the x and z (roll and pitch) values using the ratio provided
        float x = (euler.x > 180.0f ? euler.x - 360.0f : euler.x) * rpLimitRatio;
        float z = (euler.z > 180.0f ? euler.z - 360.0f : euler.z) * rpLimitRatio;

        float nx = (x > 0 ? x : 360.0f + x);
        float nz = (z > 0 ? z : 360.0f + z);

        // Form a new Euler angle using the normalized values
        Vector3 newEuler = new Vector3(nx, euler.y, nz);

        // Calculate the target rotation
        Quaternion target = Quaternion.Euler(newEuler);

        // Interpolate current rotation to the target rotation
        transform.rotation = Quaternion.Slerp(transform.rotation, target, temp);
    }

    //Takes snapshot from drone camera for the purpose of sending 
    //it to the interface server
    public void CamCapture() {
        // Prevent capturing multiple images at once
        if (takingPicture) {
            return;
        }

        takingPicture = true;
        // Capture the current image from the camera
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
        cam.Render();

        // Convert the rendered image to Texture2D
        Texture2D Image = new Texture2D(cam.targetTexture.width, cam.targetTexture.height); 
        Image.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0);
        Image.Apply();
        RenderTexture.active = currentRT;

        int compression = 75;
        byte[] Bytes = Image.EncodeToJPG(compression);
        string base64Image = Convert.ToBase64String(Bytes);

        StartCoroutine(PostImage(base64Image));

        takingPicture = false;
    }

    // Coroutine to post the drone's status to the server
    IEnumerator PostDroneStatus(bool droneStatus) {
        string url = webUrl + "/readyInfo";
        WWWForm form = new WWWForm();
        
        form.AddField("drone", droneStatus.ToString());
        form.AddField("name", nameOfControllerClass);

        UnityWebRequest www = UnityWebRequest.Post(url, form);
        www.certificateHandler = new MyCertificateHandler();

        yield return www.SendWebRequest();

        // Handle the server response
        if (www.isNetworkError || www.isHttpError)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Drone status posted successfully");
        }
    }

// Coroutine to post the captured image to the server
    IEnumerator PostImage(string base64Image)
    {
        string url = (webUrl + "/unityimage");
        WWWForm form = new WWWForm();
        form.AddField("image", base64Image);

        UnityWebRequest www = UnityWebRequest.Post(url, form);
        www.certificateHandler = new MyCertificateHandler();

        yield return www.SendWebRequest();

        // Handle the server response
        if (www.isNetworkError || www.isHttpError)
        {
            Debug.LogError(www.error);
            Debug.LogError("did not send an image");
        }
        else
        {
            Debug.Log("Image uploaded successfully");
        }
    }

    // Coroutine to check the server's readiness status
    IEnumerator checkingReadiness() {

        sendingReady = true;
        StartCoroutine(PostDroneStatus(true));

        string url = webUrl + "/readyInfo";
        UnityWebRequest www = UnityWebRequest.Get(url);
        www.certificateHandler = new MyCertificateHandler();

        yield return www.SendWebRequest();

        // Handle the server response
        if (www.isNetworkError || www.isHttpError)
        {
            Debug.LogError(www.error);
        }
        else if (www.downloadHandler.text.Contains("success")) 
        {
            serverReady = true;  // Server is ready to accept the image
        }

        sendingReady = false;
    }

    // Periodically check the server's status and 
    //capture an image if the server is ready
    private void CheckServerStatus() {
        imageTimer -= Time.deltaTime;
        readyTimer -= Time.deltaTime;

        if (serverReady) {
            if (readyTimer < 0) {
                serverReady = false;
            } else if (imageTimer < 0) {
                CamCapture();
                imageTimer = 0.5f;
            } 
        } else if (!sendingReady && readyTimer < 0)  {
            StartCoroutine(checkingReadiness());
            readyTimer = 10;
        }
    }
}
