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
    origin: "*",  // Allows all origins
    methods: ["GET", "POST", "PUT", "DELETE"],  // Allows all HTTP methods
    allowedHeaders: "*",  // Allows all headers
    credentials: true
  }
});

app.use(cors());
app.disable('x-powered-by');
app.use((req, res, next) => {
  res.removeHeader("X-Frame-Options"); // Disable X-Frame-Options
  next();
});

const imageRoutes = require('./routes/imageRoutes');
const depthRoutes = require('./routes/depthRoutes');
const contextRoutes = require('./routes/contextRoutes');
const hostChatRoutes = require('./routes/hostChatRoutes');
const clientChatRoutes = require('./routes/clientChatRoutes');
const instructionRoutes = require('./routes/instructionRoutes');
// const gptRoutes = require('./routes/gptRoutes');
const downloadRoutes = require('./routes/downloadRoutes');
const readyRoutes = require('./routes/readyRoutes');

app.use(express.json({ limit: '1000mb' }));
app.use(express.static('public'));
app.use(imageRoutes(io));
app.use(depthRoutes(io));
app.use(contextRoutes(io));
app.use(hostChatRoutes(io));
app.use(clientChatRoutes(io));
app.use(instructionRoutes(io));
// app.use(gptRoutes(io));
app.use(downloadRoutes(io));
app.use(readyRoutes(io));

io.on('connection', (socket) => {
  console.log('A user connected');
  io.emit('connection', 'A user connected');

  // socket.on('chat-message', 'hello world' )
  // socket.on('send-chat-message', message => {
  //   socket.broadcast.emit('chat-message', message)
  // })

  socket.on('disconnect', () => {
    console.log('A user disconnected');
    io.emit('disconnection', 'A user disconnected');
  });
});

const port = process.env.PORT || 9999;
server.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});