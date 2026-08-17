import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, LayoutDashboard, BarChart3, Sparkles, TrendingUp,
  AlertTriangle, MessageSquare, FlaskConical, Lightbulb, FileDown,
  Settings, TableProperties, ArrowRight, Clock,
} from 'lucide-react'
import { analyticsApi, productsApi } from '../../services/api'

const STATIC_COMMANDS = [
  { id: 'nav-dashboard', type: 'navigation', label: 'Dashboard', description: 'Executive overview', icon: LayoutDashboard, path: '/dashboard' },
  { id: 'nav-explorer', type: 'navigation', label: 'Data Explorer', description: 'Flexible analytics workspace', icon: BarChart3, path: '/explorer' },
  { id: 'nav-insights', type: 'navigation', label: 'AI Insights', description: 'AI-powered analysis', icon: Sparkles, path: '/insights' },
  { id: 'nav-forecast', type: 'navigation', label: 'Forecasts', description: 'Revenue and order prediction', icon: TrendingUp, path: '/forecast' },
  { id: 'nav-anomalies', type: 'navigation', label: 'Anomalies', description: 'Unusual sales activity', icon: AlertTriangle, path: '/anomalies' },
  { id: 'nav-chatbot', type: 'navigation', label: 'AI Assistant', description: 'Conversational analytics', icon: MessageSquare, path: '/chatbot' },
  { id: 'nav-scenarios', type: 'navigation', label: 'Scenario Lab', description: 'What-if simulations', icon: FlaskConical, path: '/scenarios' },
  { id: 'nav-intelligence', type: 'navigation', label: 'Intelligence Center', description: 'Opportunities, risks, and recommendations', icon: Lightbulb, path: '/intelligence' },
  { id: 'nav-reports', type: 'navigation', label: 'Reports', description: 'Export and schedule reports', icon: FileDown, path: '/reports' },
  { id: 'nav-sales', type: 'navigation', label: 'Sales Records', description: 'Browse individual transactions', icon: TableProperties, path: '/sales' },
  { id: 'nav-settings', type: 'navigation', label: 'Settings', description: 'Account and system settings', icon: Settings, path: '/settings' },
  // Filter shortcuts
  { id: 'filter-this-month', type: 'action', label: 'Dashboard — This Month', description: 'Filter dashboard to current month', icon: LayoutDashboard, path: '/dashboard?preset=this_month' },
  { id: 'filter-last-month', type: 'action', label: 'Dashboard — Last Month', description: 'Filter dashboard to previous month', icon: LayoutDashboard, path: '/dashboard?preset=last_month' },
  { id: 'chat-revenue', type: 'action', label: 'Ask: How is revenue doing?', description: 'Open AI Assistant with this question', icon: MessageSquare, path: '/chatbot', chat: 'How is revenue doing this month?' },
  { id: 'chat-forecast', type: 'action', label: 'Ask: Generate forecast', description: 'Open AI Assistant with this question', icon: MessageSquare, path: '/chatbot', chat: 'Generate a sales forecast' },
  { id: 'chat-risk', type: 'action', label: 'Ask: What are the main risks?', description: 'Open AI Assistant with this question', icon: MessageSquare, path: '/chatbot', chat: 'What are the main risks right now?' },
]

const RECENT_KEY = 'salesiq_cmd_recent'

function getRecent() {
  try { return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]') } catch { return [] }
}

function saveRecent(cmd) {
  const recent = getRecent().filter(r => r.id !== cmd.id).slice(0, 4)
  localStorage.setItem(RECENT_KEY, JSON.stringify([{ id: cmd.id, label: cmd.label, path: cmd.path, icon: null }, ...recent]))
}

const TYPE_COLORS = {
  navigation: 'text-secondary',
  action: 'text-warning',
  product: 'text-success',
}

export const CommandBar = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selected, setSelected] = useState(0)
  const [products, setProducts] = useState([])
  const inputRef = useRef(null)
  const navigate = useNavigate()

  // Load products once for search
  useEffect(() => {
    productsApi.list().then(res => setProducts(res.data || [])).catch(() => {})
  }, [])

  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setSelected(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  useEffect(() => {
    if (!query.trim()) {
      // Show recent + top static commands
      const recent = getRecent()
      const recentIds = new Set(recent.map(r => r.id))
      const top = STATIC_COMMANDS.filter(c => !recentIds.has(c.id)).slice(0, 6)
      setResults([
        ...recent.map(r => ({ ...r, type: 'recent' })),
        ...top,
      ])
      setSelected(0)
      return
    }
    const q = query.toLowerCase()
    const matched = [
      ...STATIC_COMMANDS.filter(c =>
        c.label.toLowerCase().includes(q) || c.description.toLowerCase().includes(q)
      ),
      ...products
        .filter(p => p.name.toLowerCase().includes(q) || (p.category || '').toLowerCase().includes(q))
        .slice(0, 4)
        .map(p => ({
          id: `product-${p.id}`,
          type: 'product',
          label: p.name,
          description: `${p.category || 'Product'} · ${p.stock ?? '?'} in stock`,
          icon: null,
          path: `/sales?search=${encodeURIComponent(p.name)}`,
        }))
    ].slice(0, 10)
    setResults(matched)
    setSelected(0)
  }, [query, products])

  const execute = useCallback((cmd) => {
    if (!cmd) return
    saveRecent(cmd)
    onClose()
    if (cmd.chat) {
      navigate(cmd.path, { state: { initialChat: cmd.chat } })
    } else {
      navigate(cmd.path)
    }
  }, [navigate, onClose])

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') { onClose(); return }
    if (e.key === 'ArrowDown') { e.preventDefault(); setSelected(s => Math.min(s + 1, results.length - 1)) }
    if (e.key === 'ArrowUp') { e.preventDefault(); setSelected(s => Math.max(s - 1, 0)) }
    if (e.key === 'Enter') { e.preventDefault(); execute(results[selected]) }
  }

  if (!isOpen) return null

  const getIcon = (cmd) => {
    if (cmd.icon) return cmd.icon
    if (cmd.type === 'product') return TableProperties
    if (cmd.type === 'recent') return Clock
    return ArrowRight
  }

  return (
    <div className="command-backdrop" onClick={onClose}>
      <div
        className="w-full max-w-lg bg-surface rounded-xl shadow-command border border-border overflow-hidden animate-scale-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
          <Search className="w-4 h-4 text-text-muted flex-shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search pages, data, or type a command…"
            className="flex-1 bg-transparent text-sm text-text placeholder-text-muted focus:outline-none"
          />
          <kbd className="text-2xs font-mono text-text-dim bg-sunken px-1.5 py-0.5 rounded border border-border">Esc</kbd>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto py-1">
          {results.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-text-muted">
              No results for "<span className="text-text font-medium">{query}</span>"
            </div>
          ) : (
            results.map((cmd, i) => {
              const Icon = getIcon(cmd)
              const isActive = i === selected
              return (
                <button
                  key={cmd.id}
                  onClick={() => execute(cmd)}
                  onMouseEnter={() => setSelected(i)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${
                    isActive ? 'bg-primary-50' : 'hover:bg-sunken'
                  }`}
                >
                  <div className={`w-7 h-7 rounded flex items-center justify-center flex-shrink-0 ${
                    isActive ? 'bg-primary/10' : 'bg-sunken'
                  }`}>
                    {Icon && <Icon className={`w-3.5 h-3.5 ${TYPE_COLORS[cmd.type] || 'text-text-muted'}`} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className={`text-sm font-medium truncate ${isActive ? 'text-primary' : 'text-text'}`}>{cmd.label}</div>
                    {cmd.description && (
                      <div className="text-xs text-text-muted truncate">{cmd.description}</div>
                    )}
                  </div>
                  {cmd.type === 'recent' && (
                    <span className="text-2xs text-text-dim font-medium flex-shrink-0">Recent</span>
                  )}
                  {isActive && <ArrowRight className="w-3.5 h-3.5 text-text-muted flex-shrink-0" />}
                </button>
              )
            })
          )}
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-border flex items-center gap-4 text-2xs text-text-dim">
          <span><kbd className="font-mono">↑↓</kbd> navigate</span>
          <span><kbd className="font-mono">↵</kbd> open</span>
          <span><kbd className="font-mono">Esc</kbd> close</span>
        </div>
      </div>
    </div>
  )
}
