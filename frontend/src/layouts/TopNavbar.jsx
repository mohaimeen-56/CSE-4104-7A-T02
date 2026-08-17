import React from 'react'
import { Menu, Search, Bell } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useNotifications } from '../context/NotificationContext'
import { NotificationPanel } from '../components/common/NotificationPanel'
import { useNavigate, useLocation } from 'react-router-dom'

const PAGE_TITLES = {
  '/dashboard': ['Dashboard', 'Executive overview'],
  '/explorer': ['Data Explorer', 'Flexible analytics workspace'],
  '/insights': ['AI Insights', 'Intelligent pattern discovery'],
  '/forecast': ['Forecasts', 'Revenue & order prediction'],
  '/anomalies': ['Anomalies', 'Unusual activity detection'],
  '/chatbot': ['AI Assistant', 'Conversational analytics'],
  '/scenarios': ['Scenario Lab', 'What-if simulations'],
  '/intelligence': ['Intelligence Center', 'Decision support hub'],
  '/reports': ['Reports', 'Export and schedule reports'],
  '/sales': ['Sales Records', 'Transaction history'],
  '/sales/upload': ['CSV Import', 'Bulk data upload'],
  '/settings': ['Settings', 'Account and system configuration'],
  '/notifications': ['Notifications', 'System alerts'],
}

export const TopNavbar = ({ onToggleSidebar, onOpenCommand }) => {
  const { user } = useAuth()
  const { unreadCount, togglePanel } = useNotifications()
  const navigate = useNavigate()
  const location = useLocation()

  const pageInfo = PAGE_TITLES[location.pathname] || ['SalesIQ', '']

  return (
    <header className="h-[52px] bg-surface border-b border-border flex items-center justify-between px-4 sm:px-5 flex-shrink-0 relative z-30">
      {/* Left */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="md:hidden text-text-muted hover:text-text p-1.5 rounded hover:bg-sunken transition-colors flex-shrink-0"
          aria-label="Toggle menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        {/* Page title — desktop */}
        <div className="hidden md:flex items-baseline gap-2.5 min-w-0">
          <span className="text-sm font-semibold text-text truncate">{pageInfo[0]}</span>
          {pageInfo[1] && (
            <span className="text-xs text-text-dim hidden lg:block truncate">{pageInfo[1]}</span>
          )}
        </div>
      </div>

      {/* Center: Command bar trigger */}
      <div className="flex-1 max-w-xs mx-4 hidden sm:block">
        <button
          onClick={onOpenCommand}
          className="w-full flex items-center gap-2 px-3 py-1.5 bg-sunken border border-border rounded hover:border-border-strong transition-colors text-left group"
        >
          <Search className="w-3.5 h-3.5 text-text-muted flex-shrink-0" />
          <span className="flex-1 text-xs text-text-muted">Search or command…</span>
          <kbd className="text-[10px] font-mono text-text-dim bg-surface border border-border px-1.5 py-0.5 rounded hidden lg:block">Ctrl K</kbd>
        </button>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <div className="relative">
          <button
            onClick={togglePanel}
            className="relative p-2 text-text-muted hover:text-text hover:bg-sunken rounded transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full ring-2 ring-white" />
            )}
          </button>
          <NotificationPanel />
        </div>

        <button
          onClick={() => navigate('/settings')}
          className="w-7 h-7 rounded-full bg-gradient-to-br from-secondary to-accent flex items-center justify-center text-white font-bold text-[11px] hover:opacity-90 transition-opacity flex-shrink-0"
          title={user?.name}
        >
          {user?.name?.[0]?.toUpperCase() || 'U'}
        </button>
      </div>
    </header>
  )
}
