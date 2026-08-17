import React from 'react'
import { Sparkles } from 'lucide-react'

export const AIInsightCard = ({ summaryText, generatedAt }) => {
  return (
    <div className="relative bg-gradient-to-br from-[#EAF2FB] to-[#F4F8FD] border border-[#D6E4F5] rounded-xl p-5 sm:p-6 mb-4 shadow-sm">
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 text-primary font-bold text-sm">
          <Sparkles className="w-4 h-4 text-secondary" />
          <span>Executive Intelligence Summary</span>
        </div>
        <span className="bg-secondary text-white text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full uppercase">
          AI Generated
        </span>
      </div>
      <p className="text-[13.5px] leading-relaxed text-[#23344f] pr-2 sm:pr-8">
        {summaryText}
      </p>
    </div>
  )
}
