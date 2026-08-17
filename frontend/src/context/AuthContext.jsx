import React, { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('salesiq_user')
    try {
      return saved ? JSON.parse(saved) : null
    } catch (e) {
      return null
    }
  })
  const [token, setToken] = useState(() => localStorage.getItem('salesiq_token') || null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await authApi.getMe()
          if (res.data) {
            setUser(res.data)
            localStorage.setItem('salesiq_user', JSON.stringify(res.data))
          }
        } catch (err) {
          logout()
        }
      }
      setLoading(false)
    }
    verifyUser()
  }, [token])

  const login = async (email, password) => {
    const res = await authApi.login({ email, password })
    if (res.data && res.data.access_token) {
      const newToken = res.data.access_token
      const newUser = res.data.user
      setToken(newToken)
      setUser(newUser)
      localStorage.setItem('salesiq_token', newToken)
      localStorage.setItem('salesiq_user', JSON.stringify(newUser))
      return newUser
    }
    throw new Error('Login response missing token')
  }

  const register = async (userData) => {
    const res = await authApi.register(userData)
    if (res.data && res.data.access_token) {
      const newToken = res.data.access_token
      const newUser = res.data.user
      setToken(newToken)
      setUser(newUser)
      localStorage.setItem('salesiq_token', newToken)
      localStorage.setItem('salesiq_user', JSON.stringify(newUser))
      return newUser
    }
    throw new Error('Registration response missing token')
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('salesiq_token')
    localStorage.removeItem('salesiq_user')
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    register,
    logout,
    setUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
