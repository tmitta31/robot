const express = require('express');
const router = express.Router();

module.exports = function (io) {
  let depthMatrix = null;

  router.post('/depth', (req, res) => {
    const matrix = req.body.matrix;

    depthMatrix = matrix;

    io.emit('depth_updated', 'A new matrix has been uploaded.');

    res.status(200).json({ status: 'success', message: 'Matrix uploaded and saved to a variable.' });
  });

  router.get('/depth', (req, res) => {
    if (depthMatrix) {
      res.json(depthMatrix);
      depthMatrix = null;
    } else {
      res.status(404).json({ status: 'error', message: 'No matrix found' });
    }
  });

  return router;
};
