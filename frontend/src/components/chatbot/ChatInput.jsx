import React, { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'

export const ChatInput = ({ onSend, loading, suggestions = [] }) => {
  const [text, setText] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() || loading) return
    onSend(text)
    setText('')
  }

  const handleSuggestionClick = (query) => {
    if (loading) return
    onSend(query)
  }

  return (
    <div className="flex flex-col gap-2">
      {suggestions.length > 0 && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="text-[11px] font-semibold text-text-muted flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-secondary" /> Suggestions:
          </span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestionClick(s)}
              className="bg-slate-100 hover:bg-slate-200 text-text text-[11px] font-medium px-2.5 py-1 rounded-full whitespace-nowrap border border-border transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask about your sales, top products, or regional performance…"
          disabled={loading}
          className="flex-1 bg-surface border border-border rounded-xl px-4 py-3 text-xs sm:text-[13px] text-text placeholder-text-muted focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary disabled:opacity-60 shadow-sm"
        />
        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs sm:text-[13px] px-5 py-3 rounded-xl flex items-center gap-1.5 shadow-sm transition-colors"
        >
          <span>Send</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  )
}
