// lib/firestore.ts

import {
  getFirestore,
  enableNetwork,
  enableIndexedDbPersistence,
  CACHE_SIZE_UNLIMITED
} from 'firebase/firestore'
import app from './firebase'

// Initialize Firestore
export const db = getFirestore(app)

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

