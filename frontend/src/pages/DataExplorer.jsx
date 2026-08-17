import React, { useState, useEffect, useCallback } from 'react'
import { analyticsApi, productsApi, regionsApi } from '../services/api'
import { formatCurrency, formatNumber } from '../utils/formatters'
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { BarChart3, TrendingUp, PieChart as PieIcon, Table2, Play, RefreshCw } from 'lucide-react'

const DIMENSIONS = [
  { value: 'product', label: 'Product' },
  { value: 'category', label: 'Category' },
  { value: 'region', label: 'Region' },
  { value: 'month', label: 'Month' },
  { value: 'week', label: 'Week' },
  { value: 'day', label: 'Day' },
]

const METRICS = [
  { value: 'revenue', label: 'Revenue (৳)', fmt: v => `৳${Number(v).toLocaleString()}` },
  { value: 'orders', label: 'Orders', fmt: v => Number(v).toLocaleString() },
  { value: 'aov', label: 'Avg. Order Value', fmt: v => `৳${Number(v).toLocaleString()}` },
  { value: 'quantity', label: 'Units Sold', fmt: v => Number(v).toLocaleString() },
]

const CHART_TYPES = [
  { value: 'bar', label: 'Bar', Icon: BarChart3 },
  { value: 'line', label: 'Line', Icon: TrendingUp },
  { value: 'area', label: 'Area', Icon: TrendingUp },
  { value: 'pie', label: 'Donut', Icon: PieIcon },
  { value: 'table', label: 'Table', Icon: Table2 },
]

const DATE_PRESETS = [
  { value: '', label: 'All Time' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'this_week', label: 'This Week' },
]

const CHART_COLORS = ['#2E86AB', '#1F3864', '#5B9BD5', '#2E7D32', '#E0A800', '#C0392B', '#6C3483', '#0E6655']

const CustomTooltip = ({ active, payload, label, metricFmt }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-border rounded-lg shadow-md px-3 py-2.5 text-xs">
      <div className="font-bold text-text mb-1.5">{label}</div>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2 text-text-muted">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span>{metricFmt(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

export const DataExplorer = () => {
  const [dimension, setDimension] = useState('category')
  const [metric, setMetric] = useState('revenue')
  const [chartType, setChartType] = useState('bar')
  const [preset, setPreset] = useState('')
  const [regionFilter, setRegionFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [regions, setRegions] = useState([])
  const [products, setProducts] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const categories = [...new Set(products.map(p => p.category).filter(Boolean))].sort()

  useEffect(() => {
    regionsApi.list().then(r => setRegions(r.data || [])).catch(() => {})
    productsApi.list().then(r => setProducts(r.data || [])).catch(() => {})
  }, [])

  const runQuery = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = { dimension, metric, limit: 30 }
      if (preset) params.preset = preset
      if (regionFilter) params.region_id = regionFilter
      if (categoryFilter) params.category = categoryFilter
      const res = await analyticsApi.dataExplorer(params)
      setResult(res.data)
    } catch (err) {
      setError(err.message || 'Query failed. Try different parameters.')
    } finally {
      setLoading(false)
    }
  }, [dimension, metric, preset, regionFilter, categoryFilter])

  // Auto-run on first load
  useEffect(() => { runQuery() }, [])

  const metricDef = METRICS.find(m => m.value === metric) || METRICS[0]
  const rows = result?.rows || []
  const chartData = rows.map(r => ({ name: r.label, value: r[metric] || r.revenue || 0, ...r }))

  const renderChart = () => {
    if (rows.length === 0) return (
      <div className="flex flex-col items-center justify-center h-48 text-center">
        <BarChart3 className="w-10 h-10 text-text-dim mb-3" />
        <div className="text-sm font-medium text-text-muted">No data matches these filters</div>
        <div className="text-xs text-text-dim mt-1">Try changing the date range, region, or category</div>
      </div>
    )

    if (chartType === 'table') {
      return (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 px-3 section-label">Rank</th>
                <th className="text-left py-2 px-3 section-label">{DIMENSIONS.find(d => d.value === dimension)?.label}</th>
                <th className="text-right py-2 px-3 section-label">Revenue</th>
                <th className="text-right py-2 px-3 section-label">Orders</th>
                <th className="text-right py-2 px-3 section-label">AOV</th>
                <th className="text-right py-2 px-3 section-label">Share %</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i} className="border-b border-border hover:bg-sunken">
                  <td className="py-2 px-3 tabular text-text-muted">{i + 1}</td>
                  <td className="py-2 px-3 font-medium text-text">{row.label}</td>
                  <td className="py-2 px-3 tabular text-right text-text">৳{Number(row.revenue || 0).toLocaleString()}</td>
                  <td className="py-2 px-3 tabular text-right text-text-muted">{Number(row.orders || 0).toLocaleString()}</td>
                  <td className="py-2 px-3 tabular text-right text-text-muted">৳{Number(row.aov || 0).toLocaleString()}</td>
                  <td className="py-2 px-3 tabular text-right text-text-muted">{row.contribution_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    if (chartType === 'pie') {
      return (
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%"
              innerRadius={60} outerRadius={110} paddingAngle={2}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={v => metricDef.fmt(v)} />
            <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
          </PieChart>
        </ResponsiveContainer>
      )
    }

    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#D8E2ED" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} tickFormatter={v => `৳${(v/1000).toFixed(0)}K`} width={52} />
            <Tooltip content={<CustomTooltip metricFmt={metricDef.fmt} />} />
            <Line type="monotone" dataKey="value" stroke="#2E86AB" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )
    }

    if (chartType === 'area') {
      return (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
            <defs>
              <linearGradient id="explorer-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2E86AB" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#2E86AB" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#D8E2ED" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} tickFormatter={v => `৳${(v/1000).toFixed(0)}K`} width={52} />
            <Tooltip content={<CustomTooltip metricFmt={metricDef.fmt} />} />
            <Area type="monotone" dataKey="value" stroke="#2E86AB" strokeWidth={2} fill="url(#explorer-grad)" />
          </AreaChart>
        </ResponsiveContainer>
      )
    }

    // Default: bar
    return (
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#D8E2ED" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#5A7080' }} axisLine={false} tickLine={false} tickFormatter={v => `৳${(v/1000).toFixed(0)}K`} width={52} />
          <Tooltip content={<CustomTooltip metricFmt={metricDef.fmt} />} />
          <Bar dataKey="value" radius={[3, 3, 0, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    )
  }

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-text tracking-tight">Data Explorer</h1>
        <p className="text-xs text-text-dim mt-0.5">Flexible analytics workspace — choose a dimension and metric to explore your data</p>
      </div>

      {/* Controls panel */}
      <div className="card p-4 space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label className="section-label block mb-1.5">Dimension</label>
            <select value={dimension} onChange={e => setDimension(e.target.value)}
              className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text font-medium focus:outline-none focus:border-secondary">
              {DIMENSIONS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>
          <div>
            <label className="section-label block mb-1.5">Metric</label>
            <select value={metric} onChange={e => setMetric(e.target.value)}
              className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text font-medium focus:outline-none focus:border-secondary">
              {METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </div>
          <div>
            <label className="section-label block mb-1.5">Time Period</label>
            <select value={preset} onChange={e => setPreset(e.target.value)}
              className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text font-medium focus:outline-none focus:border-secondary">
              {DATE_PRESETS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
          <div>
            <label className="section-label block mb-1.5">Region</label>
            <select value={regionFilter} onChange={e => setRegionFilter(e.target.value)}
              className="w-full bg-sunken border border-border rounded px-2.5 py-1.5 text-sm text-text font-medium focus:outline-none focus:border-secondary">
              <option value="">All Regions</option>
              {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3 pt-1 border-t border-border">
          {/* Chart type switcher */}
          <div className="flex items-center gap-1">
            {CHART_TYPES.map(ct => (
              <button
                key={ct.value}
                onClick={() => setChartType(ct.value)}
                title={ct.label}
                className={`flex items-center gap-1 px-2.5 py-1.5 rounded text-xs font-semibold transition-colors ${
                  chartType === ct.value
                    ? 'bg-primary text-white'
                    : 'text-text-muted hover:text-text hover:bg-sunken border border-border'
                }`}
              >
                <ct.Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:block">{ct.label}</span>
              </button>
            ))}
          </div>

          <button
            onClick={runQuery}
            disabled={loading}
            className="ml-auto flex items-center gap-2 px-4 py-1.5 bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-semibold text-xs rounded shadow-xs transition-colors press-effect"
          >
            {loading
              ? <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              : <Play className="w-3.5 h-3.5" />
            }
            {loading ? 'Running…' : 'Run Query'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 bg-danger-bg border border-red-200 text-danger rounded-lg text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Summary strip */}
          <div className="flex items-center gap-6 px-4 py-3 card text-xs text-text-muted">
            <div>
              <span className="section-label block">Total Revenue</span>
              <span className="kpi-value font-bold text-text text-base">৳{(result.total_revenue || 0).toLocaleString()}</span>
            </div>
            <div className="border-l border-border pl-6">
              <span className="section-label block">Total Orders</span>
              <span className="kpi-value font-bold text-text text-base">{(result.total_orders || 0).toLocaleString()}</span>
            </div>
            <div className="border-l border-border pl-6">
              <span className="section-label block">Dimension</span>
              <span className="font-semibold text-text">{DIMENSIONS.find(d => d.value === dimension)?.label}</span>
            </div>
            <div className="border-l border-border pl-6">
              <span className="section-label block">Period</span>
              <span className="font-semibold text-text">{result.period_label}</span>
            </div>
            <div className="border-l border-border pl-6">
              <span className="section-label block">Rows</span>
              <span className="kpi-value font-bold text-text">{rows.length}</span>
            </div>
          </div>

          {/* Chart / Table */}
          <div className="card p-4 animate-fade-in">
            {loading
              ? <div className="skeleton h-64 rounded-lg" />
              : renderChart()
            }
          </div>
        </div>
      )}
    </div>
  )
}
