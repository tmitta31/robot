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
const sharp = require('sharp');
const router = express.Router();
const bodyParser = require('body-parser');
const ImageBuffer = require('../VisualSupport/ImageBuffer');

module.exports = function (io) {
  let image = null;
  const jsonParser = bodyParser.json();
  const urlencodedParser = bodyParser.urlencoded({ extended: true });

  const processImage = async (imgBuffer, req, res) => {
    try {
        const imageBufferInstance = new ImageBuffer(imgBuffer);
        
        const width = imageBufferInstance.width;
        const height = imageBufferInstance.height;
        // Since the image data is now in a matrix, if you need the flat RGB array, 
        // you'd have to reconstruct it from the matrix. 
        // For the purpose of this example, I'm still using the sliced buffer.

        const rgbData = imgBuffer.slice(8);

        // Convert the byte stream to webp format
        const webpBuffer = await sharp(rgbData, {
            raw: {
                width: width,
                height: height,
                channels: 3
            }
        })
        .webp()
        .toBuffer();

        image = webpBuffer; // Saving the converted image to the global variable.

        io.emit('image_updated', 'A new image has been uploaded.');
        res.status(200).json({ status: 'success', message: 'Image uploaded and converted to WebP format.' });
    } catch (err) {
        console.error("Error converting to WebP:", err);
        res.status(500).json({ status: 'error', message: 'Error processing the image.' });
    }
  };

  router.post('/unityimage', (req, res) => {
      let chunks = [];
      req.on('data', chunk => {
          chunks.push(chunk);
      });
      req.on('end', async () => {
          // Now we have the raw bytes of the image
          const imgData = Buffer.concat(chunks);
          await processImage(imgData, req, res);
      });
  });

  router.post('/image', jsonParser, (req, res) => {
    const img_base64 = req.body.image;
    processImage(img_base64, req, res);
  });
  
  router.get('/image', (req, res) => {
    if (image) {
      res.type('image/webp').send(image);
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
});


  router.get('/webImage', (req, res) => {
    if (image) {
      res.status(200).json({ status: 'success', image: image.toString('base64') });
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
  });


  return router;
};
