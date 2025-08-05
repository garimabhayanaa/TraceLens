import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useRouter } from 'next/router'
import api from '../utils/api'

export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true)
  const { register, handleSubmit, formState: { errors } } = useForm()
  const router = useRouter()

  // Configure axios to use the Flask backend
  axios.defaults.baseURL = 'http://localhost:5000'
  axios.defaults.withCredentials = true

  const onSubmit = async (data: any) => {
    try {
      const url = isLogin ? '/api/login' : '/api/register'
      const response = await api.post(url, data)
      toast.success(response.data.message || 'Success')

      if (isLogin) {
        // Redirect to dashboard after successful login
        router.push('/dashboard')
      } else {
        // After successful registration, switch to login
        setIsLogin(true)
        toast.success('Registration successful! Please login.')
      }
    } catch (error: any) {
      const msg = error?.response?.data?.error || 'An error occurred'
      toast.error(msg)
    }
  }

  return (
    <div className="max-w-md mx-auto p-8 bg-white rounded-lg shadow-lg">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-blue-600">LeakPeek</h1>
        <h2 className="text-xl font-semibold mt-2 text-gray-800">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {!isLogin && (
          <div>
            <input
              type="text"
              placeholder="Full Name"
              {...register('name', { required: !isLogin })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">Name is required</p>}
          </div>
        )}

        <div>
          <input
            type="email"
            placeholder="Email Address"
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[^@]+@[^@]+\.[^@]+$/,
                message: 'Invalid email format'
              }
            })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <input
            type="password"
            placeholder="Password"
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters'
              }
            })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          {isLogin ? 'Login' : 'Create Account'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-gray-600">
          {isLogin ? 'New to LeakPeek?' : 'Already have an account?'}{' '}
          <button
            className="text-blue-600 hover:text-blue-800 font-semibold"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? 'Create an account' : 'Login here'}
          </button>
        </p>
      </div>
    </div>
  )
}
