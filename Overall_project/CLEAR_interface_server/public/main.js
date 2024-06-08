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

const socket = io();

const userConnections = document.getElementById('user-connections');
const requestLog = document.getElementById('request-log');
const connectedUsersElement = document.getElementById('connectedUsers');

let connectedUsers = parseInt(localStorage.getItem('connectedUsers')) || 0;

connectedUsersElement.textContent = `Connected Users: ${connectedUsers}`;

socket.on('connection', (msg) => {
    userConnections.textContent = msg;
    connectedUsers++;
    localStorage.setItem('connectedUsers', connectedUsers);
    connectedUsersElement.textContent = `Connected Users: ${connectedUsers}`;
    socket.emit('keepAlive', 'new user logged on');
});

socket.on('disconnection', (msg) => {
    userConnections.textContent = msg;
    connectedUsers--;
});

socket.on('feedback_updated', (msg) => {
    const li = document.createElement('li');
    li.textContent = msg;
    requestLog.appendChild(li);
});

socket.on('instruction_updated', (msg) => {
    const li = document.createElement('li');
    li.textContent = msg;
    requestLog.appendChild(li);
});

socket.on('unity_image_updated', (msg) => {
    const li = document.createElement('li');
    li.textContent = msg;
    requestLog.appendChild(li);
});

socket.on('readiness_requested', (msg) => {
    const li = document.createElement('li');
    li.textContent = msg;
    requestLog.appendChild(li);
});
