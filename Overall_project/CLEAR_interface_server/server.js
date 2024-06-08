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
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*", 
    methods: ["GET", "POST", "PUT", "DELETE"],  
    allowedHeaders: "*",  
    credentials: true
  }
});

app.use(cors());
app.disable('x-powered-by');
app.use((req, res, next) => {
  res.removeHeader("X-Frame-Options"); 
  next();
});

const imageRoutes = require('./routes/imageRoutes');
const unityImageRoutes = require('./routes/unityImageRoutes');
const feedbackRoutes = require('./routes/feedbackRoutes');
const instructionRoutes = require('./routes/instructionRoutes');
const readyRoutes = require('./routes/readyRoutes');
const controllerRoutes = require('./routes/controllerRoutes');
// const audioRoutes = require('./routes/audioRoutes');

app.use(express.json({ limit: '1000mb' }));
app.use(express.static('public'));

app.use(imageRoutes(io));
// app.use(unityImageRoutes(io));
app.use(feedbackRoutes(io));
app.use(instructionRoutes(io));
app.use(readyRoutes(io));
app.use(controllerRoutes(io));
// app.use(audioRoutes(io));

io.on('connection', (socket) => {
  console.log('A user connected');
  io.emit('connection', 'A user connected');

  socket.on('stream', (buffer) => {
    // broadcast the audio data to all clients
    socket.emit('stream', buffer);
  });

  socket.on('disconnect', () => {
    console.log('A user disconnected');
    io.emit('disconnection', 'A user disconnected');
  });
});

const port = process.env.PORT || 7070;
server.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
