import React from 'react'
import { Wrench, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export const MaintenanceScreen = ({ status }) => {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-bg">
      <div className="text-center space-y-5 max-w-lg bg-surface p-10 rounded-2xl border border-border shadow-sm">
        <div className="mx-auto w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
          <Wrench className="w-8 h-8 text-primary" />
        </div>
        <h1 className="font-bold text-xl text-text">SalesIQ is currently under maintenance</h1>
        <p className="text-sm text-text-muted leading-relaxed">
          {status?.message || 'The system is temporarily unavailable while maintenance work is being performed.'}
        </p>
        {status?.started_at && (
          <div className="text-xs font-mono text-text-muted bg-bg rounded-lg p-3 border border-border space-y-1 text-left">
            {status.enabled_by_name && <div>Enabled by: <span className="font-bold text-text">{status.enabled_by_name}</span></div>}
            <div>Started: <span className="font-bold text-text">{new Date(status.started_at).toLocaleString()}</span></div>
            {status.reason && <div>Reason: <span className="font-bold text-text">{status.reason}</span></div>}
          </div>
        )}
        <p className="text-xs text-text-muted">Please check back shortly.</p>
        <button
          onClick={logout}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-bg hover:bg-border text-text font-bold text-xs rounded-lg border border-border transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Log out</span>
        </button>
      </div>
    </div>
  )
}
