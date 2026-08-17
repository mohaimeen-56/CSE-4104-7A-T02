import React from 'react'
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'

export const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-bg">
      <div className="text-center space-y-4 max-w-md bg-surface p-8 rounded-2xl border border-border shadow-sm">
        <div className="font-mono font-bold text-5xl text-primary">404</div>
        <h2 className="font-bold text-lg text-text">Page Not Found</h2>
        <p className="text-xs text-text-muted">
          The requested page could not be found. Please check the URL or return to the main dashboard.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-light text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
      </div>
    </div>
  )
}
