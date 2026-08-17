import React from 'react'
import { Lightbulb, ArrowRight } from 'lucide-react'

export const RecommendationCard = ({ recommendation }) => {
  const priorityStyles = {
    high: 'border-l-4 border-l-danger',
    medium: 'border-l-4 border-l-secondary',
    low: 'border-l-4 border-l-slate-400',
  }

  return (
    <div
      className={`bg-surface border border-border rounded-xl p-4.5 p-4 shadow-sm hover:shadow transition-shadow ${
        priorityStyles[recommendation.priority] || priorityStyles.medium
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-warning" />
          <h4 className="font-bold text-xs sm:text-[13px] text-text">
            {recommendation.title}
          </h4>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-text-muted px-2 py-0.5 rounded">
          {recommendation.category}
        </span>
      </div>

      <p className="text-xs sm:text-[12.5px] text-text-muted leading-relaxed mb-2">
        {recommendation.action}
      </p>

      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-secondary">
        <ArrowRight className="w-3 h-3" />
        <span>Impact: {recommendation.impact}</span>
      </div>
    </div>
  )
}
