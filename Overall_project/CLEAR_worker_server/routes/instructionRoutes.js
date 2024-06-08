const express = require('express');
const router = express.Router();

module.exports = function (io) {
  let instructionData = null;
  let modelName = null;

  // POST route to receive JSON file from the client
  router.post('/instruction', (req, res) => {
    const data = req.body;

    if (data.string == "want") {
      io.emit('instruction_requested', 'Client is requesting instructions.');
      res.status(200).json({ status: 'success', message: 'Client request made' });

    } else {
      instructionData = data;  // Store the instruction data
      io.emit('instruction_updated', 'New instruction data has been received.');
      res.status(200).json({ status: 'success', message: 'Instruction data received and saved to a variable.' });
    }
  });

  router.post('/resetChat', (req, res) => {
    io.emit('chat_reset_requested', 'Client is requesting reset.');
    res.status(200).json({ status: 'success', message: 'Client request made' });
  });

  // GET route to serve the JSON file to the client
  router.get('/instruction', (req, res) => {
    let tempData = instructionData
    instructionData = null;
    if (tempData) {
      res.json(tempData);  // Send the instruction data as a JSON file
    } else {
      res.status(404).json({ status: 'error', message: 'No instruction data found' });
    }
  });

  router.get('/llmModel', (req, res) => {
    if (modelName) {
      res.json({model : modelName});  
      modelName = null;
    } else {
      io.emit('model_name_requested', 'controller asks which model to anticipate');
      res.status(404).json({ status: 'error', message: 'model type currently unknown' });
    }
  });

  router.post('/llmModel', (req, res) => {
    const nameForModel = req.body.model;
    modelName = nameForModel; 

    if (modelName) {
      io.emit('model_name_posted', 'The model name has been posted.');
      res.status(200).json({ status: 'success', message: 'Model name uploaded and saved to a variable.' });
    } else {
      res.status(400).json({ status: 'error', message: 'error occured' });
    }
  });

  // Function to request instructions from the client
  const requestInstructions = () => {
    io.emit('instruction_requested', 'Server is requesting instructions.');
  };

  // You can call this function whenever you need to request instructions from the client
  requestInstructions();

  return router;
};
