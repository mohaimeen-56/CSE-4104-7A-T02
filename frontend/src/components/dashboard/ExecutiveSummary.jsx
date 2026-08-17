import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, TrendingUp, AlertTriangle, ArrowRight, ChevronRight } from 'lucide-react'

export const ExecutiveSummary = ({ summary, loading }) => {
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="border border-border rounded-lg p-4 space-y-3">
        <div className="skeleton h-4 w-32 rounded" />
        <div className="skeleton h-5 w-full rounded" />
        <div className="skeleton h-4 w-3/4 rounded" />
        <div className="skeleton h-4 w-1/2 rounded" />
      </div>
    )
  }

  if (!summary) return null

  const confidence = summary.confidence_pct || 0

  return (
    <div className="border border-border rounded-lg overflow-hidden bg-surface">
      {/* Header bar */}
      <div className="flex items-center gap-2.5 px-4 py-2.5 border-b border-border bg-primary-50">
        <Sparkles className="w-3.5 h-3.5 text-secondary flex-shrink-0" />
        <span className="text-xs font-bold text-primary uppercase tracking-wider">AI Business Summary</span>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-2xs text-text-dim">Confidence</span>
          <span className="kpi-value text-xs font-bold text-text">{confidence}%</span>
          <div className="confidence-bar w-16">
            <div className="confidence-bar-fill" style={{ width: `${confidence}%` }} />
          </div>
        </div>
      </div>

      <div className="px-4 py-3.5 space-y-3">
        {/* Headline */}
        <p className="text-base font-semibold text-text leading-snug">{summary.headline}</p>

        {/* Body */}
        <p className="text-sm text-text-muted leading-relaxed">{summary.body}</p>

        {/* Key opportunity / risk */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {summary.key_opportunity && (
            <div className="flex items-start gap-2 p-2.5 rounded bg-signal-opportunityBg border border-blue-100">
              <TrendingUp className="w-3.5 h-3.5 text-signal-opportunity flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-[10px] font-bold text-signal-opportunity uppercase tracking-wider mb-0.5">Key Opportunity</div>
                <div className="text-xs text-text leading-relaxed">{summary.key_opportunity}</div>
              </div>
            </div>
          )}
          {summary.key_risk && (
            <div className="flex items-start gap-2 p-2.5 rounded bg-signal-riskBg border border-red-100">
              <AlertTriangle className="w-3.5 h-3.5 text-signal-risk flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-[10px] font-bold text-signal-risk uppercase tracking-wider mb-0.5">Key Risk</div>
                <div className="text-xs text-text leading-relaxed">{summary.key_risk}</div>
              </div>
            </div>
          )}
        </div>

        {/* Footer: disclaimer + link */}
        <div className="flex items-center justify-between pt-1 border-t border-border">
          <span className="text-2xs text-text-dim">
            Computed from last 30 days · Fact-based · No hallucination
          </span>
          <button
            onClick={() => navigate('/insights')}
            className="flex items-center gap-1 text-xs font-semibold text-secondary hover:text-secondary-dark transition-colors"
          >
            Full Analysis
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}
