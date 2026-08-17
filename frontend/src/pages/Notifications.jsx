import React from 'react'
import { Bell, CheckCheck, Check } from 'lucide-react'
import { useNotifications } from '../context/NotificationContext'
import { formatDate } from '../utils/formatters'

export const Notifications = () => {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications()

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight">Notifications</h1>
          <p className="text-xs text-text-muted mt-0.5">System alerts and activity updates</p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="flex-shrink-0 flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-secondary border border-secondary/30 rounded-lg hover:bg-secondary/5 transition-colors"
          >
            <CheckCheck className="w-3.5 h-3.5" />
            Mark all read
          </button>
        )}
      </div>

      <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-sm">
        {notifications.length === 0 ? (
          <div className="py-16 flex flex-col items-center gap-3 text-text-muted">
            <Bell className="w-8 h-8 opacity-30" />
            <p className="text-sm font-semibold">No notifications yet</p>
            <p className="text-xs">System alerts and activity updates will appear here.</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {notifications.map((n) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && markAsRead(n.id)}
                className={`flex items-start gap-4 px-5 py-4 transition-colors ${
                  !n.is_read
                    ? 'bg-secondary/5 hover:bg-secondary/10 cursor-pointer'
                    : 'hover:bg-slate-50 opacity-75'
                }`}
              >
                <span
                  className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${
                    !n.is_read ? 'bg-secondary' : 'bg-transparent border border-border'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text leading-relaxed">{n.message}</p>
                  <span className="text-[11px] text-text-muted mt-1 block">
                    {formatDate(n.created_at)}
                  </span>
                </div>
                {!n.is_read && (
                  <button
                    onClick={(e) => { e.stopPropagation(); markAsRead(n.id) }}
                    className="flex-shrink-0 p-1.5 rounded text-text-muted hover:text-secondary hover:bg-secondary/10 transition-colors"
                    title="Mark as read"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
