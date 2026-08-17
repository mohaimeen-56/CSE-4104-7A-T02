import React, { useState, useEffect } from 'react'
import { aiApi } from '../services/api'
import { AnomalyCard } from '../components/insights/AnomalyCard'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export const AnomaliesPage = () => {
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetch = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await aiApi.getAnomalies()
      setAnomalies(res.data || [])
    } catch (err) {
      setError(err.message || 'Failed to load anomalies.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetch() }, [])

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight">Anomaly Detection</h1>
          <p className="text-xs text-text-dim mt-0.5">
            Statistical outliers in sales data detected via z-score analysis
          </p>
        </div>
        <button onClick={fetch} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-text-muted border border-border rounded hover:bg-sunken transition-colors">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="p-3.5 bg-danger-bg border border-red-200 text-danger rounded-lg text-xs font-semibold">{error}</div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="skeleton h-20 rounded-lg" />)}
        </div>
      ) : anomalies.length === 0 ? (
        <div className="card p-10 text-center">
          <AlertTriangle className="w-10 h-10 text-text-dim mx-auto mb-3" />
          <div className="text-sm font-medium text-text">No anomalies detected</div>
          <div className="text-xs text-text-muted mt-1">Your sales data is within normal statistical bounds.</div>
          <div className="text-2xs text-text-dim mt-2">Requires at least 30 records for reliable detection.</div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs text-text-muted font-medium">{anomalies.length} anomalies detected</div>
          {anomalies.map(a => <AnomalyCard key={a.id} anomaly={a} />)}
        </div>
      )}
    </div>
  )
}
