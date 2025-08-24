import { initializeApp, getApps } from 'firebase/app';
import { getFirestore, connectFirestoreEmulator, enableNetwork, disableNetwork } from 'firebase/firestore';

// Firebase configuration (same as in firebase.ts)
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase app if not already initialized
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// Initialize Firestore
const db = getFirestore(app);

// Force enable network connection
enableNetwork(db).catch((error) => {
  console.warn('Failed to enable Firestore network:', error);
});

// For development with emulator (optional)
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  try {
    // Only connect to emulator if running locally and not already connected
    if (window.location.hostname === 'localhost') {
      // Uncomment the line below if you want to use Firestore emulator
      // connectFirestoreEmulator(db, 'localhost', 8080);
    }
  } catch (error) {
    console.warn('Firestore emulator connection failed:', error);
  }
}

export { db };
export default db;
