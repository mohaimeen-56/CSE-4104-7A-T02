import React, { useRef, useEffect } from 'react'
import { useNotifications } from '../../context/NotificationContext'
import { Bell, Check, CheckCheck, X } from 'lucide-react'
import { formatDate } from '../../utils/formatters'

export const NotificationPanel = () => {
  const { notifications, unreadCount, isOpen, closePanel, markAsRead, markAllAsRead } =
    useNotifications()
  const panelRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        closePanel()
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, closePanel])

  if (!isOpen) return null

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-12 w-80 sm:w-96 bg-surface border border-border rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150"
    >
      <div className="p-3.5 px-4 bg-slate-50 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-primary" />
          <span className="font-bold text-sm text-text">Notifications</span>
          {unreadCount > 0 && (
            <span className="bg-danger text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
              {unreadCount} new
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-[11px] font-semibold text-secondary hover:underline flex items-center gap-1"
              title="Mark all as read"
            >
              <CheckCheck className="w-3.5 h-3.5" /> Mark all read
            </button>
          )}
          <button
            onClick={closePanel}
            className="text-text-muted hover:text-text p-1 rounded hover:bg-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="max-h-80 overflow-y-auto divide-y divide-border">
        {notifications.length === 0 ? (
          <div className="p-8 text-center text-text-muted text-xs">
            No notifications yet
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markAsRead(n.id)}
              className={`p-3.5 px-4 hover:bg-slate-50 transition-colors cursor-pointer flex items-start gap-3 ${
                !n.is_read ? 'bg-secondary/5 font-medium' : 'opacity-80'
              }`}
            >
              <span
                className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                  !n.is_read ? 'bg-secondary' : 'bg-transparent'
                }`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-text leading-relaxed">{n.message}</p>
                <span className="text-[10px] text-text-muted mt-1 block">
                  {formatDate(n.created_at)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
