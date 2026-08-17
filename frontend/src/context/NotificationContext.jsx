import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { notificationsApi } from '../services/api'
import { useAuth } from './AuthContext'

const NotificationContext = createContext(null)

export const NotificationProvider = ({ children }) => {
  const { isAuthenticated } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      setLoading(true)
      const res = await notificationsApi.list({ limit: 15 })
      if (res.data) {
        setNotifications(res.data)
      }
      const countRes = await notificationsApi.getUnreadCount()
      if (countRes.data) {
        setUnreadCount(countRes.data.unread_count)
      }
    } catch (e) {
      // ignore silently
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications()
      const interval = setInterval(fetchNotifications, 30000) // Poll every 30s
      return () => clearInterval(interval)
    }
  }, [isAuthenticated, fetchNotifications])

  const markAsRead = async (id) => {
    try {
      await notificationsApi.markAsRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (e) {
      console.error(e)
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (e) {
      console.error(e)
    }
  }

  const togglePanel = () => setIsOpen((prev) => !prev)
  const closePanel = () => setIsOpen(false)

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        isOpen,
        loading,
        togglePanel,
        closePanel,
        markAsRead,
        markAllAsRead,
        refresh: fetchNotifications,
      }}
    >
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}
