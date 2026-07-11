import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, signup as apiSignup, verifyEmail as apiVerifyEmail, getMe, forgotPassword as apiForgotPassword, resetPassword as apiResetPassword } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem('zoom_scheduler_token')
      if (token) {
        try {
          const userData = await getMe()
          setUser(userData)
        } catch (err) {
          console.error('Failed to verify token on load:', err)
          localStorage.removeItem('zoom_scheduler_token')
          setUser(null)
        }
      }
      setLoading(false)
    }
    checkAuth()
  }, [])

  async function login(email, password) {
    setError(null)
    try {
      const resp = await apiLogin({ email, password })
      localStorage.setItem('zoom_scheduler_token', resp.access_token)
      const userData = await getMe()
      setUser(userData)
      return userData;
    } catch (err) {
      setError(err.message || 'Login failed')
      throw err
    }
  }

  async function signup(email, password, role = 'admin') {
    setError(null)
    try {
      const resp = await apiSignup({ email, password, role })
      return resp
    } catch (err) {
      setError(err.message || 'Signup failed')
      throw err
    }
  }

  function logout() {
    localStorage.removeItem('zoom_scheduler_token')
    setUser(null)
    setError(null)
  }

  async function verifyEmail(token) {
    setError(null)
    try {
      const resp = await apiVerifyEmail(token)
      return resp
    } catch (err) {
      setError(err.message || 'Verification failed')
      throw err
    }
  }

  async function forgotPassword(email) {
    setError(null)
    try {
      const resp = await apiForgotPassword({ email })
      return resp
    } catch (err) {
      setError(err.message || 'Forgot password request failed')
      throw err
    }
  }

  async function resetPassword(token, newPassword) {
    setError(null)
    try {
      const resp = await apiResetPassword({ token, new_password: newPassword })
      return resp
    } catch (err) {
      setError(err.message || 'Password reset failed')
      throw err
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, setError, login, signup, logout, verifyEmail, forgotPassword, resetPassword }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
