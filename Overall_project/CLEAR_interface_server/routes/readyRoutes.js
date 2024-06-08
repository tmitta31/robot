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

const express = require('express');
const bodyParser = require('body-parser');
const router = express.Router();

// parse application/x-www-form-urlencoded
router.use(bodyParser.urlencoded({ extended: true }));

// parse application/json
router.use(bodyParser.json());

module.exports = function (io) {
  let coordinatorReady = null;
  let nameOfCoordinator = null; 

  let droneReady = null;
  let thereIsAnActiveUser = true;
  let activeUserReplied = false;
  let allowTimeOuts = false;
  let activeUsers = [];

  // helps save costs of running server and use of llm api calls.
  // timer that occurs every durationInMinutes, that will ask frontend
  // if a user is interacting with the site. If not, will stall services such
  // as the coordinator and the robot being used.
  determiningStall = function(durationInMinutes = 10) {
    // This outer interval checks for client activity repeatedly at specified intervals.
    setInterval(() => {
      io.emit('are_clients_active', 'Clients are you there?');
      activeUserReplied = false;
  
      // We use a setTimeout instead of setInterval to create a single delayed check
      // after the duration has passed, rather than creating repeated checks.
        if (thereIsAnActiveUser) {
            setTimeout(() => {
              // removes all users that have not been updated recently
              removeInactiveUsers((durationInMinutes * 60 * 1000) / 2);
              if (!activeUserReplied && allowTimeOuts) {
                  thereIsAnActiveUser = false;
                  resetReadiness();
                  io.emit('web_stall', 'stall?');
                  console.log("I am stalling");
              }
            }, (durationInMinutes * 60 * 1000) / 2);
        }
    }, durationInMinutes * 60 * 1000);
  }

  determiningStall();

  addActiveUser = function(username) {
    // Check if the user already exists in the activeUsers list
    const existingUser = activeUsers.find(user => user.name === username);

    console.log("active user is ", username);

    if (existingUser) {
        // Update the timestamp of the existing user
        existingUser.timestamp = new Date();
    } else {
        // Add the new user's name and the current timestamp to the activeUsers list
        io.emit('active_user_update', username);
        activeUsers.push({
          name: username,
          timestamp: new Date()
        });
    }
  }

  removeInactiveUsers = function(duration) {
    const currentTime = new Date();
    let currentUsers = [];

    currentUsers = activeUsers.filter(user => {
        const timeDifference = currentTime - new Date(user.timestamp);
        return timeDifference <= duration;
    });

    // If any users are too old
    if (currentUsers.length != activeUsers.length) {
      activeUsers = currentUsers;
      io.emit('active_user_update', "delete");
      console.log("change to the users");
    } else {
      console.log("no change to users");
    }
  }

  router.get('/activeUsers', (req, res) => {
    // Create an array of user names from the activeUsers array
    const activeUserNames = activeUsers.map(user => user.name);

    // Check if there are any active users
    if (activeUserNames.length > 0) {
      res.status(200).json({ status: 'success', activeUsers: activeUserNames });
    } else {
      res.status(404).json({ status: 'error', message: "No active users" });
    }
  })

  router.post('/readyInfo', (req, res) => {
      const coordinator = req.body.coordinator;
      const drone = req.body.drone;
      nameOfCoordinator = req.body.name;

      if (nameOfCoordinator)
        console.log("coordName: ", nameOfCoordinator);

      if (drone) {
          droneReady = drone;
      }

      if (coordinator) {
        coordinatorReady = coordinator;
      }

      if (droneReady && coordinatorReady && thereIsAnActiveUser) {
          io.emit('system_ready', 'READY!');
      }

      res.status(200).json({ status: 'success', 
      message: 'readiness made known' });
  });

  router.post('/stalling', (req, res) => {
    io.emit('web_stall', 'stall?');
    res.status(200).json({ status: 'success', message: "epic win" });
  });

  // called when a user is active on the site.
  router.post('/wakeup', (req, res) => {
    if (droneReady && coordinatorReady && !(thereIsAnActiveUser)) {
        io.emit('system_ready', 'READY!');
    }
    
    io.emit('readiness_requested', 'uReady?');

    thereIsAnActiveUser = true;
    activeUserReplied = true;

    // logs user's active status
    addActiveUser(req.body.name);

    console.log("waking up");
    res.status(200).json({ status: 'success', 
      message: "epic win", 
      user: req.body.name});
  });

  router.post('/readyrequest', (req, res) => {
      io.emit('readiness_requested', 'uReady?');
      res.status(200).json({ status: 'success', message: "epic win" });
  });

  function resetReadiness(){
    coordinatorReady = false;
    droneReady = false;
  }

  router.post('/readyreset', (req, res) => {
    resetReadiness()
    res.status(200).json({ status: 'success', message: "epic win" });
  });

  router.get('/coordinatorClassName', (req, res) => {
    if (nameOfCoordinator) {
      res.status(200).json({ status: 'success', message: nameOfCoordinator});
    } else {
      res.status(404).json({ status: 'error', message: "name not set :d" });
    }
  })

  router.get('/readyInfo', (req, res) => {
    let output = "";
    let ready = true;
    const projectName = "CLEAR";

    if (droneReady) {
        output += projectName+"_robot is READY ";
    } else {
        output += projectName+"_robot is NOT ready ";
        ready = false;
    }

    if (coordinatorReady) {
        output += projectName+"_coordinator is READY ";
    } else {
        output += projectName+"_coordinator is NOT ready ";
        ready = false;
    }

    if (thereIsAnActiveUser) {
        output += projectName+"_interface has active users" ;
    } else {
        output += projectName+"_interface does NOT has active users ";
        ready = false;
    }

    if (ready) {
      res.status(200).json({ status: 'success', message: output });
    } else {
        res.status(400).json({ status: 'error', message: output });
    }
  });
  
  return router;
};