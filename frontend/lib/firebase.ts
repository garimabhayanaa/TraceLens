import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, setPersistence, browserLocalPersistence } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDjUAJg-Tv9cUJOvBN2_MK77y-nczeukmA",
  authDomain: "tracelens-c206b.firebaseapp.com",
  projectId: "tracelens-c206b",
  storageBucket: "tracelens-c206b.firebasestorage.app",
  messagingSenderId: "403957118926",
  appId: "1:403957118926:web:defa4fa342e3c100c75d9f"
};

// Initialize Firebase app if not already initialized
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// Initialize Firebase Auth
const auth = getAuth(app);

// Set persistence to local
setPersistence(auth, browserLocalPersistence).catch((error) => {
  console.warn('Failed to set auth persistence:', error);
});

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export { auth, googleProvider };
export default app;
