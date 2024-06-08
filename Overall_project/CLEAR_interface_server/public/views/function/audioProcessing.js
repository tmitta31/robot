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

//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream;                      //stream from getUserMedia()
var rec;                            //Recorder.js object
var input;                          //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //audio context to help us record

let shoudAppend = false;
let processInterupted = false;


let userThatStartedAudio;

var toggleButton = document.getElementById("toggleMic");
var isRecording = false; // A flag variable to track the recording status

// Add an event to the button
toggleButton.addEventListener("click", function() {
    if(!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
    isRecording = !isRecording; // Toggle the recording status
});

// Interval variable to send audio data every 3 seconds
var sendAudioDataInterval;

function createRecorder(stream) {
    /* use the stream */
    input = audioContext.createMediaStreamSource(stream);

    /* 
        Create the Recorder object and configure to record mono sound (1 channel)
        Recording 2 channels  will double the file size
    */
    rec = new Recorder(input,{numChannels:1});

    //start the recording process
    rec.record();
}

function startRecording() {
    shoudAppend = false;
    
    // toggleButton.src = "./resources/microphoneRed.png"; 

    toggleButton.style.color = "red";
    console.log("recordButton clicked");

    // toggleButton.textContent = "Stop Recording";

    var constraints = { audio: true, video:false }

    toggleButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        audioContext = new AudioContext();

        gumStream = stream;

        // create the recorder
        createRecorder(stream);

        console.log("Recording started");

        // Start sending audio data every 2 seconds
        sendAudioDataInterval = setInterval(function(){
            // create the wav blob and send to server
            rec.exportWAV(sendDataToFlaskServer);

            // stop the recording
            rec.stop();

            // create a new recorder
            createRecorder(gumStream);
        }, 5000);

    }).catch(function(err) {
        toggleButton.disabled = false;
    });
}

function stopRecording() {

    console.log("stopButton clicked");
    toggleButton.style.color = "black";


    // toggleButton.textContent = "Start Recording";

    toggleButton.disabled = false;

    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    // Stop sending audio data
    clearInterval(sendAudioDataInterval);

    //create the wav blob and send it to server one last time
    processInterupted = true;
    rec.exportWAV(sendDataToFlaskServer);
    // shoudAppend = false;
}

function sendDataToFlaskServer(blob) {
    let data = new FormData();
    data.append('file', blob, 'record.wav');
    
    let notNewMess = processInterupted;

    if (processInterupted) {
        processInterupted = false;
    }

    // Currently only works when the client and server are the same machine :-(
    fetch("https://localhost:2020/chat", {
        method: 'POST',
        body: data
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }) 
    .then(response => {
        console.log('Successfully sent the file to the server!', response);
        // Assuming the response contains a 'user' and 'message' field
        if(response.user && response.message){
            if (shoudAppend) {
                changeLastMessage(usersName, response.message);
            } else {
                shoudAppend = true;
                addMessage(usersName, response.message, "fromAudio");
            }
        } else {
            if (shoudAppend) {
                // Post feedback posts last message in chat
                postFeedback("fromAudio");
                shoudAppend = false;
            }
        }
    })
    .catch(e => {
        console.error('An error occurred while sending the file to the server:', e);
    });
}