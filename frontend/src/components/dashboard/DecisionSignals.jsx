import React from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, TrendingDown, AlertTriangle, Lightbulb, Zap, ArrowRight } from 'lucide-react'

const SIGNAL_CONFIG = {
  opportunity: { label: 'Opportunity', Icon: TrendingUp, cls: 'signal-opportunity', border: 'border-l-blue-500' },
  risk:        { label: 'Risk',        Icon: TrendingDown, cls: 'signal-risk',        border: 'border-l-red-500' },
  anomaly:     { label: 'Anomaly',     Icon: AlertTriangle, cls: 'signal-anomaly',    border: 'border-l-orange-500' },
  trend:       { label: 'Trend',       Icon: TrendingUp,  cls: 'signal-trend',        border: 'border-l-green-600' },
  action:      { label: 'Action',      Icon: Zap,         cls: 'signal-action',       border: 'border-l-purple-500' },
}

const SEVERITY_RING = {
  high:   'ring-1 ring-red-200',
  medium: '',
  low:    '',
}

const SignalCard = ({ signal }) => {
  const navigate = useNavigate()
  const cfg = SIGNAL_CONFIG[signal.signal_type] || SIGNAL_CONFIG.trend
  const { Icon } = cfg

  return (
    <div
      onClick={() => signal.link_path && navigate(signal.link_path)}
      className={`border border-border rounded-lg p-3.5 border-l-[3px] ${cfg.border} bg-surface shadow-xs
        ${signal.link_path ? 'cursor-pointer hover:shadow-sm hover:-translate-y-px transition-all duration-150' : ''}
        ${SEVERITY_RING[signal.severity] || ''}`}
    >
      <div className="flex items-start gap-2.5">
        <div className={`w-6 h-6 rounded flex items-center justify-center flex-shrink-0 mt-0.5 ${cfg.cls}`}>
          <Icon className="w-3.5 h-3.5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-1">
            <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${cfg.cls}`}>
              {cfg.label}
            </span>
            {signal.severity === 'high' && (
              <span className="text-[10px] font-bold text-danger uppercase">HIGH</span>
            )}
          </div>
          <div className="text-sm font-semibold text-text leading-snug mb-0.5">{signal.title}</div>
          <div className="text-xs text-text-muted leading-relaxed">{signal.description}</div>
          {signal.metric_value !== null && signal.metric_value !== undefined && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <span className="kpi-value text-sm font-bold text-text">
                {signal.metric_value > 0 ? '+' : ''}{signal.metric_value.toFixed(1)}
              </span>
              <span className="text-xs text-text-muted">{signal.metric_label}</span>
            </div>
          )}
        </div>
        {signal.link_path && (
          <ArrowRight className="w-3.5 h-3.5 text-text-dim flex-shrink-0 mt-1 group-hover:text-text" />
        )}
      </div>
    </div>
  )
}

export const DecisionSignals = ({ signals, counts, loading }) => {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1,2,3].map(i => (
          <div key={i} className="skeleton h-20 rounded-lg" />
        ))}
      </div>
    )
  }

  if (!signals || signals.length === 0) {
    return (
      <div className="border border-border rounded-lg p-6 text-center">
        <Lightbulb className="w-8 h-8 text-text-dim mx-auto mb-2" />
        <div className="text-sm font-medium text-text">No signals detected</div>
        <div className="text-xs text-text-muted mt-1">Add more sales data to enable intelligent signal detection.</div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
      {signals.map((s, i) => (
        <SignalCard key={i} signal={s} />
      ))}
    </div>
  )
}
