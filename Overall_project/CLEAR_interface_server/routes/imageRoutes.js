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
const axios = require('axios');
const sharp = require('sharp');

const sendToWorker = true;
module.exports = function (io) {
  let image = null;
  const jsonParser = bodyParser.json();
  const urlencodedParser = bodyParser.urlencoded({ extended: true });

  const processImage = (img_base64, req, res) => {
      image = img_base64;

      const buffer = Buffer.from(img_base64, 'base64');

      io.emit('image_updated', 'A new image has been uploaded.');
  
      if (sendToWorker) {
          const workerURL = process.env.WORKER_ADDRESS + '/image';

          // Convert the image to .webp format with a quality of 80 using sharp
        sharp(buffer)
        .webp({ quality: 100 })
        .toBuffer()
        .then(encodedImgBuffer => {
            const encodedImgBase64 = encodedImgBuffer.toString('base64');

            // Post the encoded image data to the second server
            axios.post(workerURL, {
                image: encodedImgBase64
            }).then((response) => {
                if (response.status !== 200) {
                    console.error('Failed to send image to worker:', response.data.message);
                }
            }).catch((error) => {
                console.error('Error sending image to worker:', error.message);
            });
        })
        .catch(err => {
            console.error('Error encoding image:', err.message);
        });
      }
  
      res.status(200).json({ status: 'success', message: 'Image uploaded and saved to a variable.' });
  };

  router.post('/unityimage', [jsonParser, urlencodedParser], (req, res) => {
    const img_base64 = req.body.image;
    processImage(img_base64, req, res);
  });

  router.post('/image', jsonParser, (req, res) => {
    const img_base64 = req.body.image;
    processImage(img_base64, req, res);
  });
  
  router.get('/image', (req, res) => {
    if (image) {
      const imgBuffer = Buffer.from(image, 'base64');
      res.type('image/webp').send(imgBuffer);
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
  });

  router.get('/webImage', (req, res) => {
    if (image) {
      res.status(200).json({ status: 'success', image });
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
  });

  return router;
};
