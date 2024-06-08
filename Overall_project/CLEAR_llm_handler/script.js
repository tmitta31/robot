// // server.js
// const express = require('express');
// const bodyParser = require('body-parser');
// const { spawn } = require('child_process');
// const path = require('path');

// const app = express();
// app.use(bodyParser.json());

// app.post('/ask', (req, res) => {
//     const gptAsk = req.body.gpt_ask;

//     if (!gptAsk) {
//         return res.status(400).json({ error: 'No gpt_ask provided' });
//     }

//     const pythonProcess = spawn('python', ['main.py']);

//     pythonProcess.stdin.write(JSON.stringify({ gpt_ask: gptAsk }));
//     pythonProcess.stdin.end();

//     pythonProcess.stdout.on('data', (data) => {
//         const result = JSON.parse(data.toString());
//         res.json(result);
//     });

//     pythonProcess.stderr.on('data', (data) => {
//         console.error(`stderr: ${data}`);
//         res.status(500).json({ error: 'Internal Server Error' });
//     });

//     pythonProcess.on('close', (code) => {
//         if (code !== 0) {
//             console.error(`child process exited with code ${code}`);
//             res.status(500).json({ error: 'Internal Server Error' });
//         }
//     });
// });

// // Serve the HTML file
// app.get('/', (req, res) => {
//     res.sendFile(path.join(__dirname, 'index.html'));
// });

// const port = 3000;
// app.listen(port, () => {
//     console.log(`Server running on http://localhost:${port}`);
// });






// // const socket = io('http://localhost:9999')
// // const messageForm = document.getElementById('send-container')
// // const messageInput = document.getElementById('message-input')

// // socket.on('chat-message', data =>{
// //     console.log(data)
// // })

// // messageForm.addEventListener('submit', e =>{
// //     e.preventDefault()
// //     const message = messageInput.value
// //     socket.emit('send-chat-message', message)
// //     messageInput.value = ''

// // })


// // // const express = require('express');
// // // const https = require('https');  
// // // const fs = require('fs');  
// // // const cors = require('cors');
// // // const { Server } = require('socket.io');
// // // const app = express();

// // // // Read the key and certificate
// // // // const privateKey = fs.readFileSync('security/key.pem', 'utf8');
// // // // const certificate = fs.readFileSync('security/cert.pem', 'utf8');

// // // // const credentials = { 
// // // //   key: privateKey, 
// // // //   cert: certificate,
// // // //   passphrase: 'spot'
// // // // };
// // // const server = https.createServer(app); 

// // // const io = new Server(server, {
// // //   cors: {
// // //     origin: "*",
// // //     methods: ["GET", "POST", "PUT", "DELETE"],
// // //     allowedHeaders: "*",
// // //     credentials: false
// // //   }
// // // });

// // // app.use(cors());
// // // app.disable('x-powered-by');
// // // app.use((req, res, next) => {
// // //   res.removeHeader("X-Frame-Options"); 
// // //   next();
// // // });

// // // // const imageRoutes = require('./routes/imageRoutes');
// // // // const feedbackRoutes = require('./routes/feedbackRoutes');
// // // // const instructionRoutes = require('./routes/instructionRoutes');
// // // // const readyRoutes = require('./routes/readyRoutes');
// // // // const controllerRoutes = require('./routes/controllerRoutes');

// // // // app.use(express.json({ limit: '10000mb' }));
// // // // app.use(express.static('public'));
// // // // app.use(imageRoutes(io));
// // // // app.use(feedbackRoutes(io));
// // // // app.use(instructionRoutes(io));
// // // // app.use(readyRoutes(io));
// // // // app.use(controllerRoutes(io));

// // // io.on('connection', (socket) => {
// // //   console.log('A user connected');
// // //   io.emit('connection', 'A user connected');

// // //   socket.on('stream', (buffer) => {
// // //     // broadcast the audio data to all clients
// // //     socket.emit('stream', buffer);
// // //   });

// // //   socket.on('disconnect', () => {
// // //     console.log('A user disconnected');
// // //     io.emit('disconnection', 'A user disconnected');
// // //   });
// // // });

// // // const port = process.env.PORT || 3000;
// // // server.listen(port, () => {
// // //   console.log(`Server is running on port ${port}`);
// // // });