// lib/firestore.ts
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore'
import app from './firebase'

// Initialize Firestore
export const db = getFirestore(app)

// Connect to Firestore emulator in development (optional)
if (process.env.NODE_ENV === 'development') {
  // Only connect to emulator if not already connected
  try {
    connectFirestoreEmulator(db, 'localhost', 8080)
  } catch (error) {
    // Emulator already connected or not available
    console.log('Firestore emulator connection skipped')
  }
}

export default db
