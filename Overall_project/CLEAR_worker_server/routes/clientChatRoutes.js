const express = require('express');
const router = express.Router();

module.exports = function (io) {
  let clientChatInfo = null;

  router.post('/clientChatInfo', (req, res) => {
      const inputString = req.body.response;
      clientChatInfo = inputString;
      // console.log('POST /clientChatInfo, clientChatInfo is now:', clientChatInfo);
      io.emit('client_chat_updated', 'A new string has been uploaded.');
      res.status(200).json({ status: 'success', message: 'String uploaded and saved to a variable.' });
  });

  router.get('/clientChatInfo', (req, res) => {
    // console.log('GET /clientChatInfo, clientChatInfo is:', clientChatInfo);
    if (clientChatInfo) {
      res.json({ response: clientChatInfo });
      clientChatInfo = null;
    } else {
      res.status(404).json({ status: 'error', message: 'No string found' });
    }
  });

  return router;
};

