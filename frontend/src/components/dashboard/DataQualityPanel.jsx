import React from 'react'
import { ShieldCheck, AlertTriangle } from 'lucide-react'
import { formatNumber } from '../../utils/formatters'

export const DataQualityPanel = ({ quality }) => {
  if (!quality) return null

  const coverage = quality.timestamp_coverage_pct
  const isHealthy = coverage >= 95
  const anomalyTotal = quality.future_dated_count + quality.duplicate_exact_timestamp_count + quality.null_or_invalid_count

  return (
    <div className="bg-surface border border-border rounded-xl p-4 sm:p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-bold text-xs sm:text-[13px] text-text flex items-center gap-1.5">
          {isHealthy ? <ShieldCheck className="w-4 h-4 text-success" /> : <AlertTriangle className="w-4 h-4 text-warning" />}
          <span>Data Quality</span>
        </h4>
        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${isHealthy ? 'bg-success-bg text-success' : 'bg-[#FFF6E5] text-warning'}`}>
          {coverage}% complete
        </span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
        <div className="p-2.5 bg-slate-50 border border-border rounded-lg">
          <div className="text-[10.5px] font-bold text-text-muted uppercase">Records</div>
          <div className="font-mono font-bold text-text mt-0.5">{formatNumber(quality.total_records)}</div>
        </div>
        <div className="p-2.5 bg-slate-50 border border-border rounded-lg">
          <div className="text-[10.5px] font-bold text-text-muted uppercase">Timestamp Coverage</div>
          <div className="font-mono font-bold text-text mt-0.5">{coverage}%</div>
        </div>
        <div className="p-2.5 bg-slate-50 border border-border rounded-lg">
          <div className="text-[10.5px] font-bold text-text-muted uppercase">Estimated Times</div>
          <div className="font-mono font-bold text-text mt-0.5">{formatNumber(quality.estimated_timestamps)}</div>
        </div>
        <div className="p-2.5 bg-slate-50 border border-border rounded-lg">
          <div className="text-[10.5px] font-bold text-text-muted uppercase">Anomalies</div>
          <div className={`font-mono font-bold mt-0.5 ${anomalyTotal > 0 ? 'text-warning' : 'text-text'}`}>{formatNumber(anomalyTotal)}</div>
        </div>
      </div>
      {!isHealthy && (
        <p className="text-[11px] text-warning font-semibold mt-2.5">
          Timestamp coverage is below 95% — some sales records are missing a captured time and use an estimated fallback.
        </p>
      )}
    </div>
  )
}
