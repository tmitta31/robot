const express = require('express');
const router = express.Router();
const sharp = require('sharp');

module.exports = function (io) {
  let objectImage = null;
  let depthImage = null;

  router.post('/image', (req, res) => {
    const img_base64 = req.body.image;
    if (img_base64) {
      objectImage = img_base64;
      depthImage = img_base64;
      
      io.emit('image_updated', 'A new image has been uploaded.');
      res.status(200).json({ status: 'success', message: 'Image uploaded and saved to a variable.' });
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }

  });

  // Gets image right then to ensure old image is not used 
  // that may have different dimensions
  router.get('/imageDimensions', async (req, res) => {
    imageToUse = objectImage;
    if (!objectImage) {
      if (depthImage) {
        imageToUse = depthImage
      } else {
        return res.status(404).json({ status: 'error', message: 'No image found' });
      }
    }

    try {
      const imgBuffer = Buffer.from(imageToUse, 'base64');
      const metadata = await sharp(imgBuffer).metadata();
      
      return res.status(200).json({
        status: 'success',
        width: metadata.width,
        height: metadata.height
      });
    } catch (error) {
      return res.status(500).json({
        status: 'error',
        message: 'Error processing image dimensions',
        details: error.message
      });
    }
  });

  router.get('/objectImage', (req, res) => {
    let tempImage = objectImage
    objectImage = null;
    if (tempImage) {
      const imgBuffer = Buffer.from(tempImage, 'base64');
      res.type('image/webp').send(imgBuffer); // Changed the response type to 'image/webp'
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
  });

  router.get('/depthImage', (req, res) => {
    let tempImage = depthImage
    depthImage = null;
    if (tempImage) {
      const imgBuffer = Buffer.from(tempImage, 'base64');
      res.type('image/webp').send(imgBuffer);
    } else {
      res.status(404).json({ status: 'error', message: 'No image found' });
    }
  });

  return router;
};
