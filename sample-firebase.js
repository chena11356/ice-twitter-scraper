// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAr6vkUSl02WF0Rttg9Bx1_7y25O78raw8",
  authDomain: "whereisicerightnow2025.firebaseapp.com",
  projectId: "whereisicerightnow2025",
  storageBucket: "whereisicerightnow2025.firebasestorage.app",
  messagingSenderId: "402966237582",
  appId: "1:402966237582:web:27e56823e0ebf095ad14df",
  measurementId: "G-MX1K04FE6M"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);