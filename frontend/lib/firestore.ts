<<<<<<< Updated upstream
// lib/firestore.ts

import {
  getFirestore,
  enableNetwork,
  enableIndexedDbPersistence,
  CACHE_SIZE_UNLIMITED
} from 'firebase/firestore'
import app from './firebase'
=======
import { initializeApp, getApps } from 'firebase/app';
import { getFirestore, connectFirestoreEmulator, enableNetwork, disableNetwork } from 'firebase/firestore';

// Firebase configuration (same as in firebase.ts)
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
>>>>>>> Stashed changes

// Initialize Firestore
const db = getFirestore(app);

<<<<<<< Updated upstream
// Configure Firestore for production use
const configureFirestore = async () => {
  try {
    // Enable offline persistence for better UX
    await enableIndexedDbPersistence(db, {
      cacheSizeBytes: CACHE_SIZE_UNLIMITED
    })
    console.log('✅ Firestore offline persistence enabled')

    // Ensure network is enabled (this is crucial)
    await enableNetwork(db)
    console.log('✅ Firestore network connection enabled')

  } catch (err: any) {
    if (err.code === 'failed-precondition') {
      console.warn('⚠️ Multiple tabs open - persistence enabled in another tab')
    } else if (err.code === 'unimplemented') {
      console.warn('⚠️ Browser does not support persistence')
    } else {
      console.error('❌ Firestore configuration error:', err)
      // Force network connection even if persistence fails
      try {
        await enableNetwork(db)
        console.log('✅ Network enabled after persistence failure')
      } catch (netErr) {
        console.error('❌ Network enable failed:', netErr)
      }
    }
  }
}

// Initialize configuration immediately
configureFirestore()

export default db

=======
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
>>>>>>> Stashed changes
