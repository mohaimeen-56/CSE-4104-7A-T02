import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { analyticsApi, productsApi, regionsApi } from '../services/api'
import { KpiCard } from '../components/common/KpiCard'
import { RevenueTrendChart } from '../components/dashboard/RevenueTrendChart'
import { ProductBarChart } from '../components/dashboard/ProductBarChart'
import { RegionDonutChart } from '../components/dashboard/RegionDonutChart'
import { TopProductsTable } from '../components/dashboard/TopProductsTable'
import { DataQualityPanel } from '../components/dashboard/DataQualityPanel'
import { DecisionSignals } from '../components/dashboard/DecisionSignals'
import { ExecutiveSummary } from '../components/dashboard/ExecutiveSummary'
import { formatCurrency, formatNumber } from '../utils/formatters'
import { useAuth } from '../context/AuthContext'
import {
  RefreshCw, X, Filter, ChevronDown, Lightbulb,
  TrendingUp, AlertTriangle, BarChart3, ArrowRight,
} from 'lucide-react'

const DATE_PRESETS = [
  { value: '', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'this_week', label: 'This Week' },
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
]

const getGreeting = () => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export const Dashboard = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [data, setData] = useState(null)
  const [quality, setQuality] = useState(null)
  const [signals, setSignals] = useState(null)
  const [summary, setSummary] = useState(null)
  const [products, setProducts] = useState([])
  const [regions, setRegions] = useState([])
  const [loading, setLoading] = useState(true)
  const [signalsLoading, setSignalsLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)
  const [filterOpen, setFilterOpen] = useState(false)

  const [preset, setPreset] = useState(searchParams.get('preset') || '')
  const [regionId, setRegionId] = useState(searchParams.get('region') || '')
  const [category, setCategory] = useState(searchParams.get('category') || '')
  const [productId, setProductId] = useState(searchParams.get('product') || '')
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '')
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '')

  useEffect(() => {
    const params = {}
    if (preset) params.preset = preset
    if (regionId) params.region = regionId
    if (category) params.category = category
    if (productId) params.product = productId
    if (minPrice) params.min_price = minPrice
    if (maxPrice) params.max_price = maxPrice
    setSearchParams(params, { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preset, regionId, category, productId, minPrice, maxPrice])

  const filterParams = useMemo(() => ({
    preset: preset || undefined,
    region_id: regionId || undefined,
    category: category || undefined,
    product_id: productId || undefined,
    min_price: minPrice || undefined,
    max_price: maxPrice || undefined,
  }), [preset, regionId, category, productId, minPrice, maxPrice])

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const [overviewRes, qualityRes] = await Promise.all([
        analyticsApi.getOverview(filterParams),
        analyticsApi.getDataQuality(),
      ])
      if (overviewRes.data) setData(overviewRes.data)
      if (qualityRes.data) setQuality(qualityRes.data)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data.')
    } finally {
      setLoading(false)
    }
  }, [filterParams])

  // Decision signals and executive summary load once (not filter-dependent)
  const fetchIntelligence = useCallback(async () => {
    setSignalsLoading(true)
    try {
      const [sigRes, sumRes] = await Promise.all([
        analyticsApi.getDecisionSignals(),
        analyticsApi.getExecutiveSummary(),
      ])
      if (sigRes.data) setSignals(sigRes.data)
      if (sumRes.data) setSummary(sumRes.data)
    } catch {
      // Non-fatal — signals are a bonus feature
    } finally {
      setSignalsLoading(false)
    }
  }, [])

  useEffect(() => { fetchDashboardData() }, [fetchDashboardData])
  useEffect(() => { fetchIntelligence() }, [fetchIntelligence])
  useEffect(() => {
    productsApi.list().then(res => setProducts(res.data || [])).catch(() => {})
    regionsApi.list().then(res => setRegions(res.data || [])).catch(() => {})
  }, [])

  const categories = useMemo(
    () => [...new Set(products.map(p => p.category).filter(Boolean))].sort(),
    [products]
  )

  const clearFilters = () => {
    setPreset(''); setRegionId(''); setCategory('')
    setProductId(''); setMinPrice(''); setMaxPrice('')
  }

  const activeFilterChips = [
    preset && { key: 'preset', label: DATE_PRESETS.find(p => p.value === preset)?.label, clear: () => setPreset('') },
    regionId && { key: 'region', label: regions.find(r => String(r.id) === regionId)?.name || 'Region', clear: () => setRegionId('') },
    category && { key: 'category', label: category, clear: () => setCategory('') },
    productId && { key: 'product', label: products.find(p => String(p.id) === productId)?.name || 'Product', clear: () => setProductId('') },
    (minPrice || maxPrice) && { key: 'price', label: `৳${minPrice || '0'}–${maxPrice || '∞'}`, clear: () => { setMinPrice(''); setMaxPrice('') } },
  ].filter(Boolean)

  const hasFilters = activeFilterChips.length > 0

  const kpis = data?.kpis || { total_revenue: 0, total_orders: 0, average_order_value: 0, revenue_growth_pct: null, orders_growth_pct: null, aov_growth_pct: null }

  // Build sparkline data from revenue trend
  const revenueSparkline = data?.revenue_trend?.slice(-12).map(r => r.revenue) || null
  const ordersSparkline = data?.revenue_trend?.slice(-12).map(r => r.orders) || null

  const signalSummary = signals
    ? [
        signals.opportunities_count > 0 && `${signals.opportunities_count} Opp.`,
        signals.risks_count > 0 && `${signals.risks_count} Risk`,
        signals.anomalies_count > 0 && `${signals.anomalies_count} Anomaly`,
      ].filter(Boolean).join(' · ')
    : null

  return (
    <div className="space-y-5 max-w-[1400px]">
      {/* ── Page Header ───────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div>
          <p className="text-sm text-text-muted mb-0.5">{getGreeting()}, <span className="font-medium text-text">{user?.name?.split(' ')[0] || 'there'}</span></p>
          <h1 className="text-xl font-bold text-text tracking-tight">Business Overview</h1>
          <p className="text-xs text-text-dim mt-0.5">Sales performance across all regions and products</p>
        </div>
        <div className="flex items-center gap-2">
          {lastUpdated && (
            <span className="text-2xs text-text-dim hidden sm:block">
              Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
          <button
            onClick={() => setFilterOpen(f => !f)}
            className={`flex items-center gap-1.5 px-3 py-1.5 border rounded text-xs font-semibold transition-colors shadow-xs ${
              hasFilters || filterOpen
                ? 'bg-primary text-white border-primary'
                : 'bg-surface border-border text-text-muted hover:text-text hover:bg-sunken'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Filters</span>
            {hasFilters && <span className="bg-white/20 rounded-full w-4 h-4 flex items-center justify-center text-[10px] font-bold">{activeFilterChips.length}</span>}
          </button>
          <button
            onClick={fetchDashboardData}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-surface border border-border hover:bg-sunken text-text-muted hover:text-text rounded text-xs font-semibold shadow-xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Filter Bar (collapsible) ──────────────────────────── */}
      {filterOpen && (
        <div className="card p-3.5 space-y-3 animate-slide-down">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <select value={preset} onChange={e => setPreset(e.target.value)}
              className="bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs">
              {DATE_PRESETS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
            <select value={regionId} onChange={e => setRegionId(e.target.value)}
              className="bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs">
              <option value="">All Regions</option>
              {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
            <select value={category} onChange={e => setCategory(e.target.value)}
              className="bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs">
              <option value="">All Categories</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <select value={productId} onChange={e => setProductId(e.target.value)}
              className="bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs">
              <option value="">All Products</option>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <div className="flex items-center gap-1">
              <input type="number" placeholder="Min ৳" value={minPrice} onChange={e => setMinPrice(e.target.value)}
                className="w-20 bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs" />
              <span className="text-text-dim">–</span>
              <input type="number" placeholder="Max ৳" value={maxPrice} onChange={e => setMaxPrice(e.target.value)}
                className="w-20 bg-sunken border border-border rounded px-2.5 py-1.5 text-text-muted font-medium focus:outline-none focus:border-secondary text-xs" />
            </div>
            {hasFilters && (
              <button onClick={clearFilters} className="flex items-center gap-1 text-xs font-bold text-danger hover:underline">
                <X className="w-3 h-3" /> Clear
              </button>
            )}
          </div>
          {hasFilters && (
            <div className="flex flex-wrap gap-1.5 pt-1 border-t border-border">
              {activeFilterChips.map(chip => (
                <span key={chip.key} className="flex items-center gap-1 bg-primary/10 text-primary text-2xs font-bold px-2 py-1 rounded-full">
                  {chip.label}
                  <button onClick={chip.clear}><X className="w-2.5 h-2.5" /></button>
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-danger-bg border border-red-200 text-danger rounded-lg text-xs font-semibold">
          {error}
        </div>
      )}

      {/* ── KPI Strip ─────────────────────────────────────────── */}
      {loading && !data ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-24 rounded-lg" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <KpiCard
            label="Total Revenue"
            value={formatCurrency(kpis.total_revenue).replace('৳', '')}
            prefix="৳"
            delta={kpis.revenue_growth_pct}
            isUp={(kpis.revenue_growth_pct ?? 0) >= 0}
            sparklineData={revenueSparkline}
            status={kpis.revenue_growth_pct > 0 ? 'good' : kpis.revenue_growth_pct < -10 ? 'danger' : 'neutral'}
            accent
          />
          <KpiCard
            label="Total Orders"
            value={formatNumber(kpis.total_orders)}
            delta={kpis.orders_growth_pct}
            isUp={(kpis.orders_growth_pct ?? 0) >= 0}
            sparklineData={ordersSparkline}
          />
          <KpiCard
            label="Avg. Order Value"
            value={formatCurrency(kpis.average_order_value).replace('৳', '')}
            prefix="৳"
            delta={kpis.aov_growth_pct}
            isUp={(kpis.aov_growth_pct ?? 0) >= 0}
          />
          <KpiCard
            label="Data Coverage"
            value={quality ? `${quality.timestamp_coverage_pct?.toFixed(0)}%` : '—'}
            status={quality?.timestamp_coverage_pct >= 95 ? 'good' : quality?.timestamp_coverage_pct >= 75 ? 'warning' : 'danger'}
            statusLabel={quality ? `${quality.total_records.toLocaleString()} records` : ''}
          />
        </div>
      )}

      {/* ── Intelligence Layer: Summary + Signals ─────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Executive Summary (wider) */}
        <div className="lg:col-span-3">
          <ExecutiveSummary summary={summary} loading={signalsLoading} />
        </div>

        {/* Decision Signals sidebar */}
        <div className="lg:col-span-2">
          <div className="border border-border rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-border bg-sunken">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-3.5 h-3.5 text-secondary" />
                <span className="text-xs font-bold text-text">Decision Signals</span>
              </div>
              {signalSummary && (
                <span className="text-2xs text-text-dim font-medium">{signalSummary}</span>
              )}
            </div>
            <div className="p-3">
              <DecisionSignals
                signals={signals?.signals?.slice(0, 4)}
                counts={signals}
                loading={signalsLoading}
              />
              {signals && signals.signals?.length > 4 && (
                <button
                  onClick={() => navigate('/intelligence')}
                  className="w-full mt-2.5 flex items-center justify-center gap-1.5 py-2 text-xs font-semibold text-secondary hover:text-secondary-dark border border-border rounded hover:bg-sunken transition-colors"
                >
                  View all {signals.signals.length} signals
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Revenue Trend Chart ───────────────────────────────── */}
      <div className="card p-4 sm:p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-text">Revenue Trend</h3>
            <p className="text-xs text-text-muted mt-0.5">
              {preset ? DATE_PRESETS.find(p => p.value === preset)?.label : 'All time'} · Monthly
            </p>
          </div>
          <button
            onClick={() => navigate('/explorer')}
            className="flex items-center gap-1 text-xs font-semibold text-secondary hover:underline"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Explore
          </button>
        </div>
        <RevenueTrendChart data={data?.revenue_trend || []} />
      </div>

      {/* ── Product × Region Breakdown ───────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-text">Sales by Product</h3>
            <span className="text-2xs text-text-dim font-medium">Click bar to filter</span>
          </div>
          <ProductBarChart
            data={data?.sales_by_product || []}
            onBarClick={id => setProductId(String(id))}
            activeProductId={productId ? Number(productId) : null}
          />
        </div>
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-text">Sales by Region</h3>
            <span className="text-2xs text-text-dim font-medium">Click slice to filter</span>
          </div>
          <RegionDonutChart
            data={data?.sales_by_region || []}
            onSliceClick={id => setRegionId(String(id))}
            activeRegionId={regionId ? Number(regionId) : null}
          />
        </div>
      </div>

      {/* ── Top Products Table ────────────────────────────────── */}
      <div className="card p-4 sm:p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-text">Top Performing Products</h3>
          <button
            onClick={() => navigate('/sales')}
            className="text-xs font-semibold text-secondary hover:underline flex items-center gap-1"
          >
            All Records <ArrowRight className="w-3 h-3" />
          </button>
        </div>
        <TopProductsTable products={data?.top_products || []} />
      </div>

      {/* ── Data Quality (collapsed by default) ──────────────── */}
      <DataQualityPanel quality={quality} />
    </div>
  )
}
