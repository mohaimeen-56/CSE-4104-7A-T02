import React, { useState, useEffect } from 'react'
import { CheckCircle2, AlertCircle, RefreshCw, Server, Database, Globe, Cpu } from 'lucide-react'
import { healthApi } from '../../services/api'

export const SystemConnectivityPanel = () => {
  const [status, setStatus] = useState(null)
  const [latency, setLatency] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const runCheck = async () => {
    setLoading(true)
    setError('')
    const start = performance.now()
    try {
      const res = await healthApi.check()
      const end = performance.now()
      setLatency(Math.round(end - start))
      setStatus(res)
    } catch (err) {
      setError(err.message || 'Failed to connect to backend server')
      setStatus(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    runCheck()
  }, [])

  const isDbHealthy = status?.database === 'healthy'

  return (
    <div className="bg-surface border border-border rounded-xl p-5 sm:p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h4 className="font-bold text-sm text-text flex items-center gap-2">
            <Server className="w-4 h-4 text-primary" />
            <span>System Connectivity & Cloud Health</span>
          </h4>
          <p className="text-xs text-text-muted mt-0.5">
            Real-time status of Frontend, FastAPI Backend, and PostgreSQL / Supabase Database
          </p>
        </div>
        <button
          onClick={runCheck}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sunken hover:bg-slate-200 text-text font-semibold text-xs rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-primary' : ''}`} />
          <span>{loading ? 'Testing…' : 'Test Connection'}</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-danger-bg border border-danger/20 text-danger rounded-lg text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Frontend Card */}
        <div className="p-3.5 bg-slate-50 border border-border rounded-lg space-y-1.5">
          <div className="flex items-center justify-between text-xs text-text-muted">
            <span className="flex items-center gap-1.5 font-medium">
              <Globe className="w-3.5 h-3.5 text-secondary" />
              Frontend
            </span>
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-success-bg text-success">
              Active
            </span>
          </div>
          <div className="text-xs font-bold text-text truncate">
            {window.location.hostname || 'Localhost'}
          </div>
          <div className="text-[11px] text-text-dim">
            {window.location.protocol.replace(':', '')?.toUpperCase()} Client
          </div>
        </div>

        {/* Backend Card */}
        <div className="p-3.5 bg-slate-50 border border-border rounded-lg space-y-1.5">
          <div className="flex items-center justify-between text-xs text-text-muted">
            <span className="flex items-center gap-1.5 font-medium">
              <Server className="w-3.5 h-3.5 text-primary" />
              Backend API
            </span>
            {status ? (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-success-bg text-success">
                Connected
              </span>
            ) : (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-danger-bg text-danger">
                Offline
              </span>
            )}
          </div>
          <div className="text-xs font-bold text-text truncate">
            {status ? `${status.project || 'FastAPI'} (v${status.version || '1.0'})` : 'Connecting…'}
          </div>
          <div className="text-[11px] text-text-dim">
            {latency !== null ? `Roundtrip latency: ${latency} ms` : 'Testing…'}
          </div>
        </div>

        {/* Database Card */}
        <div className="p-3.5 bg-slate-50 border border-border rounded-lg space-y-1.5">
          <div className="flex items-center justify-between text-xs text-text-muted">
            <span className="flex items-center gap-1.5 font-medium">
              <Database className="w-3.5 h-3.5 text-[#5B9BD5]" />
              Database
            </span>
            {isDbHealthy ? (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-success-bg text-success">
                Healthy
              </span>
            ) : (
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-danger-bg text-danger">
                {status ? 'Degraded' : 'Unknown'}
              </span>
            )}
          </div>
          <div className="text-xs font-bold text-text truncate">
            {isDbHealthy ? 'PostgreSQL / Supabase' : (status?.database || 'Pending check')}
          </div>
          <div className="text-[11px] text-text-dim">
            {isDbHealthy ? 'Live SQL query: SELECT 1 ✓' : 'Database query pending'}
          </div>
        </div>
      </div>
    </div>
  )
}
