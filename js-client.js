const firebase = require('firebase/compat/app');
require('firebase/compat/auth');
require('firebase/compat/firestore');
const fs = require('fs');
let tempData = {};
const config = {
  EMAIL: 'd@d.com',
  PASS: '11111111',
  DEVICE_ID: 'Jcbl1aVnecA3n64oNPFO',
  pipe: 'pipe.json',
  firebaseConfig: {
    apiKey: "AIzaSyCrL7BWWC_vI3nqvTLjOFYjLlJunHAoM5E",
    authDomain: "solar-charger-controller.firebaseapp.com",
    databaseURL: "https://solar-charger-controller-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "solar-charger-controller",
    storageBucket: "solar-charger-controller.appspot.com",
    messagingSenderId: "633961483971",
    appId: "1:633961483971:web:ec581cd65c99c1772b9c76"
  }
};

firebase.initializeApp(config.firebaseConfig);
const db = firebase.firestore();
const auth = firebase.auth();

function isEqual(obj1, obj2) {
  if (obj1 === obj2) return true;
  if (typeof obj1 !== 'object' || typeof obj2 !== 'object' || obj1 == null || obj2 == null) return false;
  
  const keys1 = Object.keys(obj1), keys2 = Object.keys(obj2);
  if (keys1.length !== keys2.length) return false;

  for (let key of keys1) {
    if (typeof obj1[key] === 'object' && typeof obj2[key] === 'object') {
      if (!isEqual(obj1[key], obj2[key])) return false;
    } else if (obj1[key] !== obj2[key]) return false;
  }
  return true;
}

auth.signInWithEmailAndPassword(config.EMAIL, config.PASS).then(userCredential => {
  const userID = userCredential.user.uid;
  let isUpdating = false;
  const docRef = db.collection('user').doc(userID).collection('nodes').doc(config.DEVICE_ID);

  function sendToPipe(data) {
    isUpdating = true;
    fs.writeFile(config.pipe, JSON.stringify(data), { flag: 'w' }, err => {
      if (err) console.error('An error occurred:', err);
      else {
        console.log('Data sent to pipe.json');
        isUpdating = false;
      }
    });
  }

  docRef.onSnapshot(doc => {
    if (doc.exists) {
      const deviceData = doc.data();
      if (!isEqual(deviceData.settings, tempData['settings'])) {
        sendToPipe(deviceData);
        tempData = deviceData;
      }
    } else console.log('No such document!');
  });

  fs.watch(config.pipe, (eventType, filename) => {
    if (eventType === 'change' && !isUpdating) {
      fs.readFile(config.pipe, (err, data) => {
        if (err) throw err;
        if (data.toString().trim()) {
          try {
            const tempJSON = JSON.parse(data.toString());
            let updateObject = {};
            let hasChanges = false;
  
            // Check for changes in 'readings'
            for (let key in tempJSON.readings) {
              if (!isEqual(tempJSON.readings[key], tempData['readings'][key])) {
                hasChanges = true;
                updateObject[`readings.${key}`] = tempJSON.readings[key];
              }
            }
  
            // Check for changes in 'stats'
            for (let key in tempJSON.stats) {
              if (!isEqual(tempJSON.stats[key], tempData['stats'][key])) {
                hasChanges = true;
                updateObject[`stats.${key}`] = tempJSON.stats[key];
              }
            }
  
            if (hasChanges) {
              isUpdating = true;
              console.log(updateObject);
              docRef.update(updateObject).then(() => {
                isUpdating = false;
                console.log("Document updated with changes in 'readings' and 'stats'");
              });
            }
          } catch (parseError) {
            console.error('Error parsing JSON:', parseError);
          }
        } else console.log('No data to update');
      });
    }
  });  
}).catch(error => {
  console.error('Authentication failed:', error.code, error.message);
});
