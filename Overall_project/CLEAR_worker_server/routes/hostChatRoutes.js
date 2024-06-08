const express = require('express');
const router = express.Router();

module.exports = function (io) {
  let hostChatInfo = null;
  let responseReplacement = null;


  router.post('/hostChatInfo', (req, res) => {
    const pR = req.body.fixResponse;
    const inputString = req.body.prompt;
    hostChatInfo = inputString;
    responseReplacement = pR;

    console.log("host chat ", hostChatInfo, " fixRespo ", responseReplacement, '\n');
    // console.log('POST /hostChatInfo, hostChatInfo is now:', hostChatInfo);
    io.emit('host_chat_updated', 'A new string has been uploaded.');
    res.status(200).json({ status: 'success', message: 'String uploaded and saved to a variable.' });
  });

  router.get('/hostChatInfo', (req, res) => {
    // console.log('GET /hostChatInfo, hostChatInfo is:', hostChatInfo);
    let response = {};
  
    if (hostChatInfo) {
      response.prompt = hostChatInfo;
      hostChatInfo = null;
    }
  
    if (responseReplacement) {
      response.fixResponse = responseReplacement;
      responseReplacement = null;
    }
  
    if (Object.keys(response).length > 0) {
      res.json(response);
    } else {
      res.status(404).json({ status: 'error', message: 'No string found' });
    }
  });

  return router;
};

