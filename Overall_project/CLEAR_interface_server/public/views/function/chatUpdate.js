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

// Select the chat input field and the chat submit button
let chatField = document.getElementById('textInput');
let chatBox = document.getElementById('chat-content');
let mostRecentMessage;
let mostRecentUser;

let audioMessageInProgressBody;

// Add an event listener for 'Enter' key press in the chat input field
chatField.addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); // to prevent a newline from being entered in the chat box

    // Check if there's text to send
    if (this.value) {
      mostRecentUser = 'person'
      mostRecentMessage = this.value;
      // sending it to llm
      postFeedback();
      // Clear the input field
      this.value = '';
    }
  }
});

let addMessage = (user, message, fromAudio) => {
  let newMessage = document.createElement('p');

  newMessage.innerHTML = `<strong>${user}:</strong> ${message}`;
  chatBox.appendChild(newMessage);

  if (fromAudio)
    audioMessageInProgressBody = newMessage;

  chatBox.scrollTop = chatBox.scrollHeight; // To auto-scroll to the latest message
  console.log("add mess");

  // Store the message content as a string
  mostRecentUser = user
  mostRecentMessage = message;
};

// Function to append text to the latest message in the chatBox
let appendToLastMessage = (user, textToAppend) => {
  // Get the last message in the chat
  let lastMessageElement = chatBox.lastElementChild;

  // Check if there's at least one message in the chat
  if (lastMessageElement) {
    // Append the new text to the last message
    lastMessageElement.innerHTML += ` ${textToAppend}`;
  } else {
    // If there are no messages in the chat, add a new one
    let newMessageElement = document.createElement('p');
    newMessageElement.innerHTML = `<strong>${user}:</strong> ${textToAppend}`;
    chatBox.appendChild(newMessageElement);
  }

  // To auto-scroll to the latest message
  chatBox.scrollTop = chatBox.scrollHeight;
};

// Function to append text to the latest message in the chatBox
let changeLastMessage = (user, textToAppend) => {
  // Check if there's at least one message in the chat

  // If a new element has been created in front of the audio generating, swap them.
  // The audio message should be in the front.
  if (audioMessageInProgressBody !== chatBox.lastElementChild){
    chatBox.insertBefore(chatBox.lastElementChild, audioMessageInProgressBody);
  }

  if (audioMessageInProgressBody) {
    // Append the new text to the last message
    audioMessageInProgressBody.innerHTML = `<strong>${user}:</strong> ${textToAppend}`;
    console.log("if in change");
  } else {
    // If there are no messages in the chat, add a new one
    audioMessageInProgressBody = document.createElement('p');
    audioMessageInProgressBody = `<strong>${user}:</strong> ${textToAppend}`;
    chatBox.appendChild(audioMessageInProgressBody);
    console.log("else in change");
  }

  mostRecentUser = user
  mostRecentMessage = textToAppend;

  // To auto-scroll to the latest message
  chatBox.scrollTop = chatBox.scrollHeight;
};

// Post feedback to the feedbackRoutes.js script
let postFeedback = (fromAudio) => {
  console.log(mostRecentMessage);
  // Text provided through the text field is posted, and then emitted back to the body.
  // Since audio is process of multiple steps, instead of a single event, it is built up.
  // Once the audio stream has concluded, it will go back here.
  
  if (fromAudio) {
    contentToBeSent = JSON.stringify({"user" : usersName, 
      "message" : mostRecentMessage, "fromHuman" : "true", 
        "createdFromAudio" : "true"});
  } else {
    contentToBeSent = JSON.stringify({"user" : usersName, 
      "message" : mostRecentMessage, "fromHuman" : "true"});
  }

  fetch('/userMessage', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: contentToBeSent,
  })
  .then(response => response.json())
  .then(data => {
    console.log('Feedback posted:', data); 
  })
  .catch((error) => {
    console.error('Error:', error);
  });
};

// Listen for the 'chat_update' event
socket.on('chat_update', (data) => {
  console.log("data.fromAudio ", data.fromAudio);
  console.log("user is ", data.user);

  if (!data.fromAudio || data.user != usersName)
    addMessage(data.user, data.message);
});


// socket.on('are_clients_active', (data) => {
//   shouldSendActivity = true;
// });


// function postActivity() {
//   fetch('/wakeup', {
//       method: 'POST',
//       headers: {
//           'Content-Type': 'application/json'
//       },
//   })
//   .then(response => response.json())
//   .then(data => console.log(data.message))
//   .catch(error => console.log(error));
// }