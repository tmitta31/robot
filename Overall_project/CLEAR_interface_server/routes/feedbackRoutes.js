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
const bodyParser = require('body-parser');

module.exports = function (io) {
  let info = null;
  const jsonParser = bodyParser.json();
  const urlencodedParser = bodyParser.urlencoded({ extended: true });

  const processFeedback = (feedback, req, res) => {
    console.log("Feedback: ", feedback);
    info = feedback;
    io.emit('feedback_updated', 'New information has been uploaded.');
    res.status(200).json({ status: 'success', message: 'Information uploaded and saved to a variable.' });
  };

  router.post('/feedbackUnity', [jsonParser, urlencodedParser], (req, res) => {
    console.log("hello we are here")
    const feedback = req.body.feedback;
    processFeedback(feedback, req, res);
  });

  router.post('/feedbackInfo', jsonParser, (req, res) => {
    const feedback = req.body.feedback;
    processFeedback(feedback, req, res);
  });

  router.get('/feedbackInfo', (req, res) => {
    if (info) {
      res.json(info);
    } else {
      res.status(404).json({ status: 'error', message: 'No information found' });
    }
  });

  return router;
};
