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
  const services = ["coordinator", "llmHandler", "objectDetection", "depthEstimation"];
  let servicesTurnedOff = [];
  let servicesThatShutdown = [];

  let sequenceTurnOnId;
  let sequenceTurnOffId;

  function turnOnSequence(durationInMinutes = 0.5) {
    // This outer interval checks for client activity repeatedly at specified intervals.
    sequenceTurnOnId = setInterval(() => {
      io.emit('turnon', servicesThatShut[downservicesThatShutdown.size()]);
    }, durationInMinutes * 60 * 1000);
  }

  function turnOffSequence(durationInMinutes = 0.5) {
    // This outer interval checks for client activity repeatedly at specified intervals.
    sequenceTurnOffId = setInterval(() => {
        console.log("trying to turn off");
      io.emit('turnoff', "turn off");
    }, durationInMinutes * 60 * 1000);
  }

  function removeElementsWithValue(arr, value) {
    return arr.filter(item => item !== value);
  }

  router.post('/all_services_turnon', (req, res) => {
    turnOnSequence()
    res.status(200).json({ status: 'success', message: "turning on services" });
  });

  router.post('/all_services_shutdown', (req, res) => {
    io.emit('turnoff', "turn off");
    turnOffSequence()
    res.status(200).json({ status: 'success', message: "epic win" });
  });

  // Service turning on and reporting to the server
  router.post('/service_turnon', (req, res) => {
    const serviceName = req.body.service;
    if (servicesThatShutdown.includes(serviceName)) {
      removeElementsWithValue(servicesThatShutdown, serviceName);

      //If there are no more elements in the turn off list, stops
      //trying to turn off services
      if (!servicesThatShut.size()) {
        clearInterval(sequenceTurnOnId);
      }
      res.status(200).json({ status: 'success', message: "epic win" });
    } else {
      res.status(400).json({ status: 'error', message: "service given is not known" });
    }
  });

  // Services turnoff and tell server that they turned off
  router.post('/service_turnoff', (req, res) => {
      const serviceName = req.body.service;
      console.log("service turning off ", serviceName);
      if (serviceName) {
        if (services.includes(serviceName)) {
          if (!servicesTurnedOff.includes(serviceName)) {
            servicesThatShutdown.add(serviceName)

            if (servicesThatShutdown.size() === services.size()) {
              clearInterval(sequenceTurnOffId);
            }
            res.status(200).json({ status: 'success', message: "service added" });
          } else {
            res.status(200).json({ status: 'success', message: "service already given" });
          }
        } else {
          res.status(400).json({ status: 'error', message: "service given is not known" });
        }
      } else {
        res.status(400).json({ status: 'error', message: "no service given" });
      }
   });


  return router;
};