import React, { useState, useEffect } from 'react'
import { aiApi } from '../services/api'
import { RefreshCw, AlertTriangle, TrendingUp, Calendar, BarChart2, Info } from 'lucide-react'
import { formatCurrency } from '../utils/formatters'

const KPICard = ({ label, value, sub, accent }) => (
  <div className="card p-4 flex flex-col gap-1">
    <span className="section-label">{label}</span>
    <span className={`text-xl font-bold tabular-nums ${accent || 'text-text'}`}>{value}</span>
    {sub && <span className="text-xs text-text-dim">{sub}</span>}
  </div>
)

export const ForecastPage = () => {
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchForecast = async () => {
    setLoading(true)
    setError('')
    try {
      // axios interceptor unwraps: res = {success, data, message}
      const res = await aiApi.getForecast()
      if (res.data) setForecast(res.data)
      else setError('No forecast data returned.')
    } catch (err) {
      setError(err.message || 'Failed to load forecast data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchForecast() }, [])

  const predicted = forecast ? Number(forecast.predicted_revenue) : 0
  const historical = forecast?.historical_months || []
  const curveFull = forecast?.forecast_curve || []
  const lastHistorical = historical.length ? Number(historical[historical.length - 1].revenue) : 0
  const forecastChange = lastHistorical ? ((predicted - lastHistorical) / lastHistorical * 100).toFixed(1) : null
  const r2 = forecast?.r2_score != null ? Number(forecast.r2_score).toFixed(3) : '—'

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-secondary" />
            Revenue Forecast
          </h1>
          <p className="text-xs text-text-dim mt-0.5">
            ML-based prediction for {forecast?.next_month || 'next month'} using scikit-learn linear regression
          </p>
        </div>
        <button
          onClick={fetchForecast}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-surface border border-border rounded text-xs font-semibold text-text-muted hover:text-text hover:border-secondary transition-colors press-effect"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Recalculate
        </button>
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-2.5 px-3.5 py-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
        <Info className="w-3.5 h-3.5 mt-0.5 shrink-0 text-amber-500" />
        <span>Forecast is based on historical sales patterns. Past performance does not guarantee future results.</span>
      </div>

      {error && (
        <div className="flex items-center gap-2.5 p-3.5 bg-danger-bg border border-red-200 rounded-lg text-xs text-danger font-semibold">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            {[1, 2, 3].map(i => <div key={i} className="skeleton h-24 rounded-lg" />)}
          </div>
          <div className="skeleton h-64 rounded-lg" />
        </div>
      ) : forecast ? (
        <div className="space-y-4">
          {/* KPI strip */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <KPICard
              label={`Predicted Revenue · ${forecast.next_month}`}
              value={formatCurrency(predicted)}
              sub={forecastChange !== null
                ? `${Number(forecastChange) >= 0 ? '+' : ''}${forecastChange}% vs last recorded month`
                : undefined}
              accent="text-secondary"
            />
            <KPICard
              label="Model Accuracy (R²)"
              value={r2}
              sub={forecast.model_name || 'Linear Regression'}
            />
            <KPICard
              label="Growth Estimate"
              value={forecast.growth_estimate_pct != null
                ? `${Number(forecast.growth_estimate_pct) >= 0 ? '+' : ''}${Number(forecast.growth_estimate_pct).toFixed(1)}%`
                : '—'}
              sub="vs same period last year"
              accent={forecast.growth_estimate_pct >= 0 ? 'text-success' : 'text-danger'}
            />
          </div>

          {/* Historical data table */}
          {historical.length > 0 && (
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-3">
                <Calendar className="w-4 h-4 text-text-dim" />
                <span className="section-label">Historical Sales Data ({historical.length} months)</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 section-label">Month</th>
                      <th className="text-right py-2 px-3 section-label">Revenue</th>
                      <th className="text-right py-2 px-3 section-label">Orders</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historical.map((m, i) => (
                      <tr key={i} className="border-b border-border hover:bg-sunken">
                        <td className="py-2 px-3 font-medium text-text">{m.month}</td>
                        <td className="py-2 px-3 tabular text-right text-text">{formatCurrency(Number(m.revenue))}</td>
                        <td className="py-2 px-3 tabular text-right text-text-muted">{m.orders}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Forecast curve */}
          {curveFull.length > 0 && (
            <div className="card p-4">
              <div className="flex items-center gap-2 mb-3">
                <BarChart2 className="w-4 h-4 text-text-dim" />
                <span className="section-label">Forecast Projection</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 px-3 section-label">Month</th>
                      <th className="text-right py-2 px-3 section-label">Predicted</th>
                      <th className="text-right py-2 px-3 section-label">Lower Bound</th>
                      <th className="text-right py-2 px-3 section-label">Upper Bound</th>
                    </tr>
                  </thead>
                  <tbody>
                    {curveFull.map((m, i) => (
                      <tr key={i} className="border-b border-border hover:bg-sunken">
                        <td className="py-2 px-3 font-semibold text-secondary">{m.month} ← forecast</td>
                        <td className="py-2 px-3 tabular text-right font-semibold text-text">{formatCurrency(Number(m.predicted_revenue))}</td>
                        <td className="py-2 px-3 tabular text-right text-text-muted">{formatCurrency(Number(m.lower_bound))}</td>
                        <td className="py-2 px-3 tabular text-right text-text-muted">{formatCurrency(Number(m.upper_bound))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Model note */}
          <p className="text-[10px] text-text-dim text-center pb-2">
            {forecast.message || 'Forecast generated using scikit-learn linear regression'}
          </p>
        </div>
      ) : null}
    </div>
  )
}
