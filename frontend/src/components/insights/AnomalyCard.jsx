import React from 'react'
import { AlertTriangle, AlertCircle, Package } from 'lucide-react'

export const AnomalyCard = ({ anomaly }) => {
  const isStock = anomaly.type === 'stock'
  const isDrop = anomaly.type === 'drop'

  const bgColor = isStock ? 'bg-warning-bg border-[#F2DDA0]' : 'bg-danger-bg border-[#F3C7BD]'
  const iconColor = isStock ? 'text-warning' : 'text-danger'
  const titleColor = isStock ? 'text-[#8a6a07]' : 'text-danger'
  const descColor = isStock ? 'text-[#7d6109]' : 'text-[#7a3026]'

  return (
    <div className={`border rounded-xl p-4 flex items-start gap-3.5 mb-3 ${bgColor}`}>
      <div className={`mt-0.5 flex-shrink-0 ${iconColor}`}>
        {isStock ? (
          <Package className="w-4 h-4" />
        ) : isDrop ? (
          <AlertTriangle className="w-4 h-4" />
        ) : (
          <AlertCircle className="w-4 h-4" />
        )}
      </div>
      <div className="flex-1">
        <strong className={`block text-xs sm:text-[13px] font-bold ${titleColor} mb-1`}>
          {anomaly.title}
        </strong>
        <p className={`text-xs sm:text-[12.5px] leading-relaxed ${descColor}`}>
          {anomaly.description}
        </p>
      </div>
    </div>
  )
}
