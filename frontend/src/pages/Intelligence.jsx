import React, { useState, useEffect } from 'react'
import { analyticsApi, aiApi } from '../services/api'
import { DecisionSignals } from '../components/dashboard/DecisionSignals'
import { AnomalyCard } from '../components/insights/AnomalyCard'
import { RecommendationCard } from '../components/insights/RecommendationCard'
import { Lightbulb, TrendingUp, AlertTriangle, Sparkles, BarChart3, RefreshCw } from 'lucide-react'

const TABS = [
  { id: 'overview', label: 'Overview', Icon: Lightbulb },
  { id: 'opportunities', label: 'Opportunities', Icon: TrendingUp },
  { id: 'risks', label: 'Risks', Icon: AlertTriangle },
  { id: 'anomalies', label: 'Anomalies', Icon: AlertTriangle },
  { id: 'recommendations', label: 'Recommendations', Icon: Sparkles },
]

export const Intelligence = () => {
  const [tab, setTab] = useState('overview')
  const [signals, setSignals] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [sigRes, anomRes, recRes, foreRes] = await Promise.allSettled([
        analyticsApi.getDecisionSignals(),
        aiApi.getAnomalies(),
        aiApi.getRecommendations(),
        aiApi.getForecast(),
      ])
      if (sigRes.status === 'fulfilled') setSignals(sigRes.value.data)
      if (anomRes.status === 'fulfilled') setAnomalies(anomRes.value.data || [])
      if (recRes.status === 'fulfilled') setRecommendations(recRes.value.data || [])
      if (foreRes.status === 'fulfilled') setForecast(foreRes.value.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAll() }, [])

  const opportunities = signals?.signals?.filter(s => s.signal_type === 'opportunity') || []
  const risks = signals?.signals?.filter(s => s.signal_type === 'risk') || []

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight">Intelligence Center</h1>
          <p className="text-xs text-text-dim mt-0.5">Decision support hub — opportunities, risks, anomalies, and recommendations</p>
        </div>
        <button onClick={fetchAll} className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-text-muted border border-border rounded hover:bg-sunken transition-colors">
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Signal summary chips */}
      {signals && (
        <div className="flex flex-wrap gap-2">
          {[
            { label: `${signals.opportunities_count} Opportunities`, color: 'signal-opportunity' },
            { label: `${signals.risks_count} Risks`, color: 'signal-risk' },
            { label: `${signals.anomalies_count} Anomalies`, color: 'signal-anomaly' },
            { label: `${signals.trends_count} Trends`, color: 'signal-trend' },
          ].map(chip => (
            <span key={chip.label} className={`text-xs font-semibold px-2.5 py-1 rounded-full ${chip.color}`}>
              {chip.label}
            </span>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-border">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold border-b-2 transition-colors -mb-px ${
              tab === t.id
                ? 'border-secondary text-secondary'
                : 'border-transparent text-text-muted hover:text-text'
            }`}
          >
            <t.Icon className="w-3.5 h-3.5" />
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-20 rounded-lg" />)}
        </div>
      ) : (
        <>
          {tab === 'overview' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-text mb-2">All Signals ({signals?.signals?.length || 0})</h3>
                <DecisionSignals signals={signals?.signals} loading={false} />
              </div>

              {forecast && (
                <div className="card p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-4 h-4 text-secondary" />
                    <h3 className="text-sm font-bold text-text">Revenue Forecast</h3>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div>
                      <div className="section-label mb-1">Predicted Revenue</div>
                      <div className="kpi-value text-lg font-bold text-text">
                        ৳{(forecast.predicted_revenue || 0).toLocaleString('en-BD', { maximumFractionDigits: 0 })}
                      </div>
                    </div>
                    <div>
                      <div className="section-label mb-1">Model</div>
                      <div className="text-sm font-semibold text-text">{forecast.model_name || 'Linear Regression'}</div>
                    </div>
                    {forecast.confidence_lower && (
                      <div>
                        <div className="section-label mb-1">Range</div>
                        <div className="text-sm text-text-muted">
                          ৳{Math.round(forecast.confidence_lower).toLocaleString()} – ৳{Math.round(forecast.confidence_upper || forecast.predicted_revenue).toLocaleString()}
                        </div>
                      </div>
                    )}
                  </div>
                  <p className="text-2xs text-text-dim mt-2 border-t border-border pt-2">
                    PREDICTION — not a guarantee. Based on historical trend extrapolation.
                  </p>
                </div>
              )}
            </div>
          )}

          {tab === 'opportunities' && (
            <div className="space-y-2.5">
              {opportunities.length === 0 ? (
                <div className="text-center py-12 text-text-muted text-sm">
                  No opportunities detected in the current data window.
                  <div className="text-xs mt-1 text-text-dim">Try expanding the date range or adding more data.</div>
                </div>
              ) : (
                <DecisionSignals signals={opportunities} loading={false} />
              )}
            </div>
          )}

          {tab === 'risks' && (
            <div className="space-y-2.5">
              {risks.length === 0 ? (
                <div className="text-center py-12 text-text-muted text-sm">
                  No significant risks detected in the last 30 days.
                </div>
              ) : (
                <DecisionSignals signals={risks} loading={false} />
              )}
            </div>
          )}

          {tab === 'anomalies' && (
            <div className="space-y-2.5">
              {anomalies.length === 0 ? (
                <div className="text-center py-12 text-text-muted text-sm">
                  No anomalies detected in the current period.
                  <div className="text-xs mt-1 text-text-dim">Anomaly detection requires at least 30 sales records.</div>
                </div>
              ) : (
                anomalies.map(a => <AnomalyCard key={a.id} anomaly={a} />)
              )}
            </div>
          )}

          {tab === 'recommendations' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {recommendations.length === 0 ? (
                <div className="col-span-2 text-center py-12 text-text-muted text-sm">
                  No recommendations available. Add more sales data to enable this feature.
                </div>
              ) : (
                recommendations.map(r => <RecommendationCard key={r.id} recommendation={r} />)
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
