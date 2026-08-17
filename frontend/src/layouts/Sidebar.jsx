import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, TableProperties, Sparkles, MessageSquare,
  FileDown, Settings, X, TrendingUp, AlertTriangle,
  BarChart3, FlaskConical, Lightbulb,
  Bell, Search, LogOut,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const NAV_SECTIONS = [
  {
    label: 'Overview',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    ],
  },
  {
    label: 'Analytics',
    items: [
      { name: 'Data Explorer', path: '/explorer', icon: BarChart3 },
      { name: 'Sales Records', path: '/sales', icon: TableProperties },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { name: 'AI Insights',  path: '/insights',  icon: Sparkles },
      { name: 'Forecasts',    path: '/forecast',  icon: TrendingUp },
      { name: 'Anomalies',    path: '/anomalies', icon: AlertTriangle },
      { name: 'AI Assistant', path: '/chatbot',   icon: MessageSquare },
    ],
  },
  {
    label: 'Decision Support',
    items: [
      { name: 'Scenario Lab',        path: '/scenarios',    icon: FlaskConical },
      { name: 'Intelligence Center', path: '/intelligence', icon: Lightbulb },
    ],
  },
  {
    label: 'Reporting',
    items: [
      { name: 'Reports', path: '/reports', icon: FileDown },
    ],
  },
  {
    label: 'System',
    items: [
      { name: 'Notifications', path: '/notifications', icon: Bell,     roles: ['admin', 'manager'] },
      { name: 'Settings',      path: '/settings',      icon: Settings },
    ],
  },
]

const NavItem = ({ item, onClose }) => {
  const { user } = useAuth()
  if (item.roles && !item.roles.includes(user?.role)) return null
  const Icon = item.icon
  return (
    <NavLink
      to={item.path}
      onClick={onClose}
      className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
    >
      {/* Fixed-width icon container so all labels start at the same x */}
      <span className="flex-shrink-0 w-[18px] flex items-center justify-center">
        <Icon size={15} />
      </span>
      <span className="truncate flex-1">{item.name}</span>
    </NavLink>
  )
}

export const Sidebar = ({ isOpen, onClose, onOpenCommand }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : 'U'

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          flex flex-col
          transition-transform duration-200 ease-in-out
          md:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        style={{ width: 'var(--sidebar-width)', background: '#0F1E35', flexShrink: 0 }}
        aria-label="Sidebar navigation"
      >

        {/* ── Brand ───────────────────────────────────── */}
        <div className="flex items-center justify-between px-3 pt-4 pb-3 border-b border-[#1E3455]">
          <div className="flex items-center gap-2.5 min-w-0">
            {/* Logo mark */}
            <div
              className="w-7 h-7 rounded bg-gradient-to-br from-[#5B9BD5] to-[#1F3864] flex items-center justify-center text-white font-extrabold text-[11px] shadow-sm flex-shrink-0"
              aria-hidden="true"
            >
              SQ
            </div>
            <div className="min-w-0">
              <span className="block font-bold text-sm text-white tracking-tight leading-tight truncate">
                SalesIQ
              </span>
              <span className="block text-[10px] text-[#8CA4C8] leading-none mt-0.5 truncate">
                Intelligence Platform
              </span>
            </div>
          </div>

          {/* Mobile close button — hidden on desktop */}
          <button
            onClick={onClose}
            className="md:hidden flex-shrink-0 ml-2 p-1 rounded text-[#8CA4C8] hover:text-white hover:bg-white/10 transition-colors"
            aria-label="Close menu"
          >
            <X size={16} />
          </button>
        </div>

        {/* ── Search / Command shortcut ────────────────── */}
        <div className="px-3 pt-3 pb-1">
          <button
            onClick={onOpenCommand}
            className="w-full flex items-center gap-2 px-3 py-2 rounded bg-[#162845] border border-[#1E3455] text-[#8CA4C8] hover:text-white text-[12px] transition-colors group"
          >
            <Search size={13} className="flex-shrink-0" />
            <span className="flex-1 text-left truncate">Search or command…</span>
            <kbd className="text-[10px] bg-[#1E3455] px-1.5 py-0.5 rounded font-mono text-[#8CA4C8] group-hover:text-white transition-colors flex-shrink-0">
              ⌃K
            </kbd>
          </button>
        </div>

        {/* ── Navigation ──────────────────────────────── */}
        <nav className="flex-1 overflow-y-auto shell-scroll px-2 py-2" aria-label="Main navigation">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label} className="mb-0.5">
              <div className="nav-section-label">{section.label}</div>
              <div className="space-y-0.5">
                {section.items.map((item) => (
                  <NavItem key={item.path} item={item} onClose={onClose} />
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* ── User footer ─────────────────────────────── */}
        <div className="border-t border-[#1E3455] p-3">
          <div className="flex items-center gap-2.5">
            {/* Avatar */}
            <div
              className="w-7 h-7 rounded-full bg-gradient-to-br from-[#5B9BD5] to-[#1F3864] flex items-center justify-center text-white font-bold text-[11px] flex-shrink-0"
              aria-hidden="true"
            >
              {initials}
            </div>

            {/* Name + role */}
            <div className="flex-1 min-w-0">
              <div className="text-[12.5px] font-semibold text-white leading-tight truncate">
                {user?.name || 'User'}
              </div>
              <div className="text-[10px] text-[#8CA4C8] capitalize leading-tight truncate mt-0.5">
                {user?.role}
              </div>
            </div>

            {/* Sign out button */}
            <button
              onClick={handleLogout}
              title="Sign out"
              className="flex-shrink-0 p-1.5 rounded text-[#8CA4C8] hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Sign out"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>

      </aside>
    </>
  )
}
