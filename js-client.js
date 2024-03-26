// Import the Firebase compat libraries
const firebase = require('firebase/compat/app');
require('firebase/compat/auth');
require('firebase/compat/firestore');
const fs = require('fs');

const express = require('express');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const http = require('http');
const ngrok = require('ngrok');
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', function connection(ws) {
  console.log('Client connected');
  const ffmpeg = spawn('ffmpeg', [
    '-f', 'v4l2',
    '-i', '/dev/video0',
    '-f', 'mpegts',
    '-codec:v', 'mpeg1video',
    '-s', '640x480',
    '-b:v', '800k',
    '-bf', '0',
    '-',
  ]);

  ffmpeg.stdout.on('data', (data) => {
    ws.send(data);
  });

  ffmpeg.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  ffmpeg.on('close', (code) => {
    console.log(`ffmpeg process exited with code ${code}`);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    ffmpeg.kill('SIGINT');
  });
});

const startServer = async () => {
  server.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
  });

  const url = await ngrok.connect(3000);
  console.log(`ngrok tunnel set up: ${url}`);
};

startServer(); 

const EMAIL = 'd@d.com';
const PASS = '11111111';
const DEVICE_ID = 'NunbVVo0MO1HScoDir60';

const pipe = 'pipe.json';

let tempData = {};

function isEqual(object1, object2) {
  if (object1 === object2) {
    return true;
  }

  if (object1 == null || object2 == null || typeof object1 !== 'object' || typeof object2 !== 'object') {
    return false;
  }
  
  const keys1 = Object.keys(object1);
  const keys2 = Object.keys(object2);

  if (keys1.length !== keys2.length) {
    return false;
  }

  for (const key of keys1) {
    const val1 = object1[key];
    const val2 = object2[key];
    const areObjects = isObject(val1) && isObject(val2);
    if (
      areObjects && !isEqual(val1, val2) ||
      !areObjects && val1 !== val2
    ) {
      return false;
    }
  }

  return true;
}

function isObject(object) {
  return object != null && typeof object === 'object';
}


// Initialize Firebase
const firebaseConfig = {
  // Your Firebase configuration object
  apiKey: "AIzaSyCrL7BWWC_vI3nqvTLjOFYjLlJunHAoM5E",
  authDomain: "solar-charger-controller.firebaseapp.com",
  databaseURL: "https://solar-charger-controller-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "solar-charger-controller",
  storageBucket: "solar-charger-controller.appspot.com",
  messagingSenderId: "633961483971",
  appId: "1:633961483971:web:ec581cd65c99c1772b9c76"
};
firebase.initializeApp(firebaseConfig);

// Reference to Firestore and Auth
const db = firebase.firestore();
const auth = firebase.auth();

// Authenticate using email and password
auth.signInWithEmailAndPassword(EMAIL, PASS)
  .then((userCredential) => {
    // User is signed in
    const userID = userCredential.user.uid;
    // Path to the named pipe
    const pipePath =  pipe;
    // Flag to prevent the update loop
    let isUpdating = false;

    // Function to send data to the pipe.json
    function sendToPipe(data) {
      isUpdating = true;
      fs.writeFile(pipePath, JSON.stringify(data), { flag: 'w' }, (err) => {
        if (err) {
          console.error('An error occurred:', err);
        } else {
          console.log('Data sent to pipe.json');
          isUpdating = false;
          // You can perform other operations here knowing writeFile is done
        }
      });
    }

    // Subscribe to changes in the 'settings' field inside the 'nodes' document
    const docRef = db.collection('user').doc(userID).collection('nodes').doc(DEVICE_ID);
    docRef.onSnapshot((doc) => {
      if (doc.exists) {
        const deviceData = doc.data();
        const changed = !isEqual(deviceData.settings, tempData['settings']);
        console.log('tempData is changed :', changed)
        if (deviceData && changed) {
          // Send the updated settings data to the pipe.json
          sendToPipe(deviceData);
        }
        tempData = deviceData;
      } else {
        console.log('No such document!');
      }
    });

    // IPC to receive data from the pipe.json
    fs.watch(pipePath, (eventType, filename) => {
      if (eventType === 'change' && !isUpdating) {
        fs.readFile(pipePath, (err, data) => {
          if (err) throw err;
          // Check if data is not empty and is a valid JSON string
          if (data.toString().trim()) {
            try {
              const tempJSON = JSON.parse(data.toString());
              // Update the Firestore 'readings' field with the new data
              const changed = !isEqual(tempJSON.readings, tempData['readings']);
              console.log('reading changed : ', changed);
              if (changed) {
                isUpdating = true;
                docRef.update({
                  [`readings`]: tempJSON.readings
                }).then(() => {
                  isUpdating = false;
                  console.log("docUpdated");
                });
              }
            } catch (parseError) {
              console.error('Error parsing JSON:', parseError);
            }
          } else {
            console.log('No data to update');
          }
        });
      }
    });
  })
  .catch((error) => {
    // Handle Errors here
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error('Authentication failed:', errorCode, errorMessage);
  });
