import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { adminApi } from '../services/api'
import { useAuth } from './AuthContext'

const MaintenanceContext = createContext(null)

export const MaintenanceProvider = ({ children }) => {
  const { isAuthenticated } = useAuth()
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    if (!isAuthenticated) {
      setStatus(null)
      setLoading(false)
      return
    }
    try {
      const res = await adminApi.getMaintenanceStatus()
      setStatus(res.data)
    } catch (err) {
      // If even the status check fails, don't block the app on a network hiccup
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 20000)
    const onMaintenanceEvent = () => refresh()
    window.addEventListener('salesiq:maintenance', onMaintenanceEvent)
    return () => {
      clearInterval(interval)
      window.removeEventListener('salesiq:maintenance', onMaintenanceEvent)
    }
  }, [refresh])

  return (
    <MaintenanceContext.Provider value={{ status, loading, refresh }}>
      {children}
    </MaintenanceContext.Provider>
  )
}

export const useMaintenance = () => {
  const context = useContext(MaintenanceContext)
  if (!context) {
    throw new Error('useMaintenance must be used within a MaintenanceProvider')
  }
  return context
}
