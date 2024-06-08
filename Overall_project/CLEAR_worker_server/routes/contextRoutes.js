const express = require('express');
const router = express.Router();

module.exports = function (io) {
  let contextInfo = null;

  router.post('/contextInfo', (req, res) => {
      const inputString = req.body.string;
      contextInfo = inputString;
      io.emit('context_updated', 'A new string has been uploaded.');
      res.status(200).json({ status: 'success', message: 'String uploaded and saved to a variable.' });
  });

  router.get('/contextInfo', (req, res) => {
    if (contextInfo) {
      res.json({ string: contextInfo });
      contextInfo = null;
    } else {
      res.status(404).json({ status: 'error', message: 'No string found' });
    }
  });

  return router;
};
