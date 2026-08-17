import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

// Minimal inline sparkline — no external library needed
const Sparkline = ({ data, color, height = 28 }) => {
  if (!data || data.length < 2) return null
  const values = data.map(d => (typeof d === 'number' ? d : d.value ?? d.revenue ?? 0))
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const w = 72
  const h = height
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w
    const y = h - ((v - min) / range) * (h - 4) - 2
    return `${x},${y}`
  })
  const pathD = `M ${pts.join(' L ')}`
  // Area fill path
  const areaD = `M ${pts[0]} L ${pts.join(' L ')} L ${w},${h} L 0,${h} Z`

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      <defs>
        <linearGradient id={`sg-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.2" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaD} fill={`url(#sg-${color.replace('#', '')})`} />
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

const STATUS_DOT = {
  good: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  neutral: 'bg-text-dim',
}

export const KpiCard = ({
  label,
  value,
  delta,
  isUp,
  periodText = 'vs prev period',
  prefix = '',
  suffix = '',
  sparklineData = null,
  status = null,   // good | warning | danger | neutral
  statusLabel = null,
  accent = false,
}) => {
  const deltaColor = delta === 0 || delta === null || delta === undefined
    ? 'text-text-muted'
    : isUp ? 'text-success' : 'text-danger'

  const sparkColor = delta === 0 || delta === null || delta === undefined
    ? '#95AABB'
    : isUp ? '#2E7D32' : '#C0392B'

  return (
    <div className={`bg-surface border rounded-lg p-4 shadow-xs hover-lift group ${
      accent ? 'border-secondary/30 bg-gradient-to-br from-surface to-primary-50' : 'border-border'
    }`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-2">
            <span className="section-label">{label}</span>
            {status && (
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${STATUS_DOT[status] || STATUS_DOT.neutral}`} />
            )}
          </div>
          <div className="kpi-value text-2xl font-bold text-text tracking-tight">
            {prefix}{value}{suffix}
          </div>
          {(delta !== undefined && delta !== null) && (
            <div className={`flex items-center gap-1 mt-1.5 ${deltaColor}`}>
              {delta === 0
                ? <Minus className="w-3 h-3" />
                : isUp
                  ? <TrendingUp className="w-3 h-3" />
                  : <TrendingDown className="w-3 h-3" />
              }
              <span className="text-xs font-semibold tabular-nums">
                {delta > 0 ? '+' : ''}{typeof delta === 'number' ? delta.toFixed(1) : delta}%
              </span>
              <span className="text-2xs text-text-dim font-normal">{periodText}</span>
            </div>
          )}
          {statusLabel && (
            <div className="mt-1 text-2xs text-text-dim font-medium">{statusLabel}</div>
          )}
        </div>
        {sparklineData && (
          <div className="flex-shrink-0 opacity-70 group-hover:opacity-100 transition-opacity">
            <Sparkline data={sparklineData} color={sparkColor} />
          </div>
        )}
      </div>
    </div>
  )
}

export { Sparkline }
