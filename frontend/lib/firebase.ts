// lib/firebase.ts
import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, setPersistence, browserLocalPersistence } from 'firebase/auth'

// Replace these with your actual Firebase config values
const firebaseConfig = {
  apiKey: "AIzaSyDjUAJg-Tv9cUJOvBN2_MK77y-nczeukmA",
  authDomain: "tracelens-c206b.firebaseapp.com",
  projectId: "tracelens-c206b",
  storageBucket: "tracelens-c206b.firebasestorage.app",
  messagingSenderId: "403957118926",
  appId: "1:403957118926:web:defa4fa342e3c100c75d9f"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase Authentication
export const auth = getAuth(app)

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider()

// Set authentication persistence to LOCAL (persists after browser close)
setPersistence(auth, browserLocalPersistence).catch((error) => {
  console.error('Error setting auth persistence:', error)
})

export default app
