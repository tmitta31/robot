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
const router = express.Router();

module.exports = function (io) {
  let velocity = null;
  let command = null

  router.post('/instructionInfo', (req, res) => {
    const inputVelocities = req.body.velocities;
    const inputCommand = req.body.Command;

    velocity = inputVelocities;
    command = inputCommand;

    io.emit('instruction_updated', 'New velocities have been uploaded.');
    res.status(200).json({ status: 'success', message: 'Velocities uploaded and saved to a variable.' });
  });

  router.get('/instructionInfo', (req, res) => {
    let shouldSend = false;
    let data = {}

    if (velocity) {
      data = { ...data, velocities: velocity };
      velocity = null;
      shouldSend = true;
    } 

    if (command) {
      data = { ...data, Command: command }; 
      command = null;
      shouldSend = true;
    } 

    if (shouldSend) {
      res.json(data);
    } else {
      res.status(404).json({ status: 'error', message: 'No velocities found' });
    }
  });

  return router;
};