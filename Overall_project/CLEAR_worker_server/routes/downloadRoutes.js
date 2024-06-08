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
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const router = express.Router();

// Create the storage folder if it doesn't exist
const storageFolder = path.join(__dirname, '../storage');
if (!fs.existsSync(storageFolder)) {
  fs.mkdirSync(storageFolder);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, storageFolder);
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 1024 * 1024 * 1024 * 10 // Limited to 10GB
  }
});

module.exports = function(io) {
  // Check if a file exists
  router.get('/exists/:filename', (req, res) => {
    const fileName = req.params.filename;
    const filePath = path.join(storageFolder, fileName);

    fs.access(filePath, fs.constants.F_OK, (err) => {
      if (err) {
        res.status(404).send('File not found');
        return;
      }
      res.status(200).send('File exists');
    });
  });

  // For downloading a file
  router.get('/download/:filename', (req, res) => {
    const fileName = req.params.filename;
    const filePath = path.join(storageFolder, fileName);

    fs.access(filePath, fs.constants.F_OK, (err) => {
      if (err) {
        res.status(404).send('File not found');
        return;
      }

      const stat = fs.statSync(filePath);

      res.writeHead(200, {
        'Content-Type': 'application/octet-stream',
        'Content-Length': stat.size,
        'Content-Disposition': `attachment; filename=${path.basename(filePath)}`
      });

      const readStream = fs.createReadStream(filePath);
      readStream.pipe(res);
    });
  });

  // Upload file
  router.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
      return res.status(400).send('No file uploaded');
    }

    const filePath = req.file.path;

    res.status(200).send(`File uploaded to ${filePath}`);
  });

  return router;
};
