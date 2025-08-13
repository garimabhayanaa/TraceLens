'use client'
import React, { createContext, useContext, useEffect, useState } from 'react'
import { 
  User, 
  onAuthStateChanged, 
  signInWithPopup, 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut
} from 'firebase/auth'
import { doc, setDoc, getDoc, updateDoc, serverTimestamp } from 'firebase/firestore'
import { auth, googleProvider } from './firebase'
import { db } from './firestore'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface TraceLensUser {
  uid: string
  email: string | null
  displayName: string | null
  photoURL: string | null
  emailVerified: boolean
  createdAt?: any
  lastLoginAt?: any
  subscriptionTier?: 'free' | 'premium'
  dailyUsage?: number
  privacyLevel?: 'standard' | 'enhanced' | 'maximum'
}

interface AuthContextType {
  user: User | null
  traceLensUser: TraceLensUser | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signInWithEmail: (email: string, password: string) => Promise<void>
  signUpWithEmail: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  updateUserProfile: (data: Partial<TraceLensUser>) => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  traceLensUser: null,
  loading: true,
  signInWithGoogle: async () => {},
  signInWithEmail: async () => {},
  signUpWithEmail: async () => {},
  logout: async () => {},
  updateUserProfile: async () => {}
})

export const useAuth = () => {
  return useContext(AuthContext)
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [traceLensUser, setTraceLensUser] = useState<TraceLensUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Create or update user document in Firestore
  const createOrUpdateUserDoc = async (firebaseUser: User) => {
    try {
      const userDocRef = doc(db, 'users', firebaseUser.uid)
      const userDoc = await getDoc(userDocRef)
      
      const userData: TraceLensUser = {
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        displayName: firebaseUser.displayName,
        photoURL: firebaseUser.photoURL,
        emailVerified: firebaseUser.emailVerified,
        lastLoginAt: serverTimestamp()
      }

      if (!userDoc.exists()) {
        // Create new user document
        await setDoc(userDocRef, {
          ...userData,
          createdAt: serverTimestamp(),
          subscriptionTier: 'free',
          dailyUsage: 0,
          privacyLevel: 'standard'
        })
        console.log('✅ New user document created in Firestore')
      } else {
        // Update existing user document
        await updateDoc(userDocRef, {
          lastLoginAt: serverTimestamp(),
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL,
          emailVerified: firebaseUser.emailVerified
        })
        console.log('✅ User document updated in Firestore')
      }

      // Fetch and set the complete user data
      const updatedDoc = await getDoc(userDocRef)
      if (updatedDoc.exists()) {
        setTraceLensUser(updatedDoc.data() as TraceLensUser)
      }
    } catch (error) {
      console.error('❌ Error creating/updating user document:', error)
    }
  }

  // Listen for authentication state changes
  useEffect(() => {
    console.log('🔥 Setting up Firebase auth state listener...')
    
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      console.log('🔥 Auth state changed:', firebaseUser ? 'User signed in' : 'No user')
      
      if (firebaseUser) {
        setUser(firebaseUser)
        await createOrUpdateUserDoc(firebaseUser)
      } else {
        setUser(null)
        setTraceLensUser(null)
      }
      
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const signInWithGoogle = async () => {
    try {
      console.log('🔥 Attempting Google sign-in...')
      const result = await signInWithPopup(auth, googleProvider)
      toast.success(`Welcome ${result.user.displayName || result.user.email}!`)
      router.push('/dashboard')
    } catch (error: any) {
      console.error('❌ Google sign-in error:', error)
      toast.error('Failed to sign in with Google: ' + error.message)
    }
  }

  const signInWithEmail = async (email: string, password: string) => {
    try {
      console.log('🔥 Attempting email sign-in...')
      const result = await signInWithEmailAndPassword(auth, email, password)
      toast.success('Successfully signed in!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('❌ Email sign-in error:', error)
      
      let errorMessage = 'Sign in failed'
      switch (error.code) {
        case 'auth/user-not-found':
          errorMessage = 'No account found with this email. Please sign up first.'
          break
        case 'auth/wrong-password':
          errorMessage = 'Incorrect password. Please try again.'
          break
        case 'auth/invalid-email':
          errorMessage = 'Invalid email address format.'
          break
        case 'auth/too-many-requests':
          errorMessage = 'Too many failed attempts. Please try again later.'
          break
        default:
          errorMessage = error.message
      }
      
      toast.error(errorMessage)
    }
  }

  const signUpWithEmail = async (email: string, password: string) => {
    try {
      console.log('🔥 Attempting email sign-up...')
      const result = await createUserWithEmailAndPassword(auth, email, password)
      toast.success('Account created successfully!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('❌ Email sign-up error:', error)
      
      let errorMessage = 'Account creation failed'
      switch (error.code) {
        case 'auth/email-already-in-use':
          errorMessage = 'An account with this email already exists. Please sign in instead.'
          break
        case 'auth/invalid-email':
          errorMessage = 'Invalid email address format.'
          break
        case 'auth/weak-password':
          errorMessage = 'Password is too weak. Please choose a stronger password.'
          break
        default:
          errorMessage = error.message
      }
      
      toast.error(errorMessage)
    }
  }

  const logout = async () => {
    try {
      await signOut(auth)
      toast.success('Signed out successfully')
      router.push('/')
    } catch (error: any) {
      console.error('❌ Sign out error:', error)
      toast.error('Failed to sign out')
    }
  }

  const updateUserProfile = async (data: Partial<TraceLensUser>) => {
    if (!user) return
    
    try {
      const userDocRef = doc(db, 'users', user.uid)
      await updateDoc(userDocRef, data)
      
      // Update local state
      setTraceLensUser(prev => prev ? { ...prev, ...data } : null)
      toast.success('Profile updated successfully')
    } catch (error: any) {
      console.error('❌ Error updating profile:', error)
      toast.error('Failed to update profile')
    }
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      traceLensUser, 
      loading, 
      signInWithGoogle, 
      signInWithEmail, 
      signUpWithEmail, 
      logout, 
      updateUserProfile 
    }}>
      {children}
    </AuthContext.Provider>
  )
}
