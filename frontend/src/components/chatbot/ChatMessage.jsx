import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, RotateCcw, ArrowRight } from 'lucide-react'

// Lightweight inline markdown — bold + bullet lists
const renderInlineMarkdown = (text) => {
  const parts = String(text ?? '').split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx} className="font-semibold">{part.slice(2, -2)}</strong>
    }
    return <React.Fragment key={idx}>{part}</React.Fragment>
  })
}

// Intent-based smart action suggestions
const SMART_ACTIONS = {
  region_performance: [
    { label: 'View Dashboard', path: '/dashboard', icon: '📊' },
    { label: 'Data Explorer', path: '/explorer?dimension=region', icon: '🔍' },
    { label: 'Run Scenario', path: '/scenarios', icon: '⚗️' },
  ],
  best_product: [
    { label: 'Product Analysis', path: '/explorer?dimension=product', icon: '📦' },
    { label: 'Sales Records', path: '/sales', icon: '📋' },
    { label: 'Full Insights', path: '/insights', icon: '💡' },
  ],
  total_revenue: [
    { label: 'Revenue Explorer', path: '/explorer?metric=revenue', icon: '💰' },
    { label: 'Forecast', path: '/forecast', icon: '📈' },
    { label: 'Intelligence Center', path: '/intelligence', icon: '🧠' },
  ],
  forecast: [
    { label: 'Open Forecast Page', path: '/forecast', icon: '📈' },
    { label: 'Scenario Lab', path: '/scenarios', icon: '⚗️' },
  ],
  anomalies: [
    { label: 'View All Anomalies', path: '/anomalies', icon: '⚠️' },
    { label: 'Intelligence Center', path: '/intelligence', icon: '🧠' },
  ],
  recommendations: [
    { label: 'Recommendations', path: '/intelligence?tab=recommendations', icon: '💡' },
    { label: 'Run Scenario', path: '/scenarios', icon: '⚗️' },
  ],
  top_region: [
    { label: 'Regional Analysis', path: '/explorer?dimension=region', icon: '🗺️' },
    { label: 'Intelligence Center', path: '/intelligence', icon: '🧠' },
  ],
  category_growth: [
    { label: 'Category Explorer', path: '/explorer?dimension=category', icon: '📊' },
    { label: 'AI Insights', path: '/insights', icon: '💡' },
  ],
  peak_hours: [
    { label: 'Time Analysis', path: '/explorer', icon: '🕐' },
    { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  ],
}

const GENERAL_ACTIONS = [
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Intelligence Center', path: '/intelligence', icon: '🧠' },
  { label: 'Data Explorer', path: '/explorer', icon: '🔍' },
]

const SmartActions = ({ intent }) => {
  const navigate = useNavigate()
  const actions = (intent && SMART_ACTIONS[intent]) || GENERAL_ACTIONS
  if (!actions) return null

  return (
    <div className="mt-2.5 flex flex-wrap gap-1.5">
      {actions.map(action => (
        <button
          key={action.path}
          onClick={() => navigate(action.path)}
          className="flex items-center gap-1 px-2.5 py-1.5 bg-surface border border-border rounded text-[11px] font-semibold text-secondary hover:bg-primary-50 hover:border-primary/30 transition-colors"
        >
          <span>{action.icon}</span>
          <span>{action.label}</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      ))}
    </div>
  )
}

export const ChatMessage = ({ message, onRetry }) => {
  const isUser = message.sender === 'user'
  const isError = !!message.error
  const showActions = !isUser && !isError && message.route === 'analytics'

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-4`}>
      <div
        className={`max-w-[85%] sm:max-w-[75%] p-3.5 px-4 rounded-2xl text-xs sm:text-[13px] leading-relaxed shadow-xs ${
          isUser
            ? 'bg-primary text-white rounded-br-sm'
            : isError
            ? 'bg-danger-bg text-danger rounded-bl-sm border border-red-200'
            : 'bg-[#EEF2F7] text-text rounded-bl-sm border border-[#E1E7EF]'
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-1.5 text-[10px] font-bold text-secondary uppercase tracking-wider mb-1.5">
            <Sparkles className="w-3 h-3" />
            <span>SalesIQ AI</span>
            {message.route && (
              <span className={`ml-1 px-1.5 py-0.5 rounded text-[9px] font-bold ${
                message.route === 'analytics' ? 'bg-primary/10 text-primary' : 'bg-success/10 text-success'
              }`}>
                {message.route}
              </span>
            )}
          </div>
        )}
        <div className="whitespace-pre-wrap">{renderInlineMarkdown(message.text)}</div>
        {isError && onRetry && (
          <button
            onClick={() => onRetry(message)}
            className="mt-2 flex items-center gap-1 text-[11px] font-bold text-danger hover:underline"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        )}
      </div>

      {/* Smart action buttons for analytics responses */}
      {showActions && (
        <div className="max-w-[85%] sm:max-w-[75%]">
          <SmartActions intent={message.intent} />
        </div>
      )}

      <span className="text-[10px] text-text-muted mt-1 px-1">
        {message.time || 'Just now'}
      </span>
    </div>
  )
}
