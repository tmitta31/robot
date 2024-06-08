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
router.use(bodyParser.urlencoded({ extended: true }));


//this script is for use by the setup application
// parse application/json
router.use(bodyParser.json());

module.exports = function (io) {
  let objectDetection = null;
  let depthPerception = null;
  let llmWorker = null;

  router.post('/readyInfo', (req, res) => {
      const ObjectDetection = req.body.object_detection;
      const DepthPerception = req.body.depth_perception;
      const LLM = req.body.llm_chat;

      if (ObjectDetection) {
        objectDetection = ObjectDetection;
      }

      if (DepthPerception) {
        depthPerception = DepthPerception;
      }

      if (LLM) {
        llmWorker = LLM;
      }

      if (objectDetection && depthPerception 
        && llmWorker) {
          io.emit('System_Ready', 'READY!');
      }

      res.status(200).json({ status: 'success', 
      message: 'readiness made known' });
  });

  router.post('/readyrequest', (req, res) => {
      io.emit('readiness_requested', 'uReady?');
      res.status(200).json({ status: 'success', message: "epic win" });
  });

  router.post('/readyreset', (req, res) => {
        objectDetection = false;
        depthPerception = false;
        llmWorker = false;
        res.status(200).json({ status: 'success', message: "epic win" });
  });

  router.get('/readyInfo', (req, res) => {
      let output = "";
      let ready = true;
      const projectName = "CLEAR"

      if (objectDetection) {
          output += projectName+"_object_detection is READY ";
      } else {
          output += projectName+"_object_detection is NOT ready ";
          ready = false;
      }

      if (depthPerception) {
          output += projectName+"_depth_perception is READY ";
      } else {
          output += projectName+"_depth_perception is NOT ready ";
          ready = false;
      }

      if (llmWorker) {
          output += projectName+"_llm_chat is READY ";
      } else {
          output += projectName+"_llm_chat is NOT ready ";
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