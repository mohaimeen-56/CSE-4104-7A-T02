import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { reportsApi, productsApi, regionsApi } from '../../services/api'
import { formatCurrency, formatNumber } from '../../utils/formatters'
import { SlidersHorizontal, FileSpreadsheet, FileDown, Loader2 } from 'lucide-react'

const DATE_PRESETS = [
  { value: '', label: 'All time' },
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'this_week', label: 'This Week' },
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'custom', label: 'Custom Range' },
]

const GROUP_BY_OPTIONS = [
  { value: 'month', label: 'Month' },
  { value: 'hour', label: 'Hour' },
  { value: 'day', label: 'Day' },
  { value: 'week', label: 'Week' },
  { value: 'quarter', label: 'Quarter' },
  { value: 'year', label: 'Year' },
  { value: 'category', label: 'Category' },
  { value: 'subcategory', label: 'Subcategory' },
  { value: 'brand', label: 'Brand' },
  { value: 'product', label: 'Product' },
  { value: 'region', label: 'Region' },
]

const defaultFilters = {
  preset: '', start_date: '', end_date: '', region_id: '', category: '', product_id: '',
  min_price: '', max_price: '', quantity_level: '', min_quantity: '', max_quantity: '', group_by: 'month',
}

export const ReportBuilderPanel = () => {
  const [filters, setFilters] = useState(defaultFilters)
  const [products, setProducts] = useState([])
  const [regions, setRegions] = useState([])
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [exporting, setExporting] = useState(null)

  useEffect(() => {
    productsApi.list().then((res) => setProducts(res.data || [])).catch(() => {})
    regionsApi.list().then((res) => setRegions(res.data || [])).catch(() => {})
  }, [])

  const categories = useMemo(
    () => [...new Set(products.map((p) => p.category).filter(Boolean))].sort(),
    [products]
  )

  const buildParams = useCallback(() => {
    const params = { group_by: filters.group_by }
    if (filters.preset === 'custom') {
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
    } else if (filters.preset) {
      params.preset = filters.preset
    }
    if (filters.region_id) params.region_id = filters.region_id
    if (filters.category) params.category = filters.category
    if (filters.product_id) params.product_id = filters.product_id
    if (filters.min_price) params.min_price = filters.min_price
    if (filters.max_price) params.max_price = filters.max_price
    if (filters.quantity_level) {
      params.quantity_level = filters.quantity_level
      if (filters.quantity_level === 'custom') {
        if (filters.min_quantity) params.min_quantity = filters.min_quantity
        if (filters.max_quantity) params.max_quantity = filters.max_quantity
      }
    }
    return params
  }, [filters])

  const runReport = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await reportsApi.buildReport(buildParams())
      setReport(res.data)
    } catch (err) {
      setError(err.message || 'Failed to build report')
    } finally {
      setLoading(false)
    }
  }, [buildParams])

  useEffect(() => {
    runReport()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const update = (key, value) => setFilters((prev) => ({ ...prev, [key]: value }))

  const handleExport = async (kind) => {
    setExporting(kind)
    try {
      if (kind === 'csv') await reportsApi.downloadBuilderCsv(buildParams())
      else await reportsApi.downloadBuilderPdf(buildParams())
    } catch (err) {
      alert(err.message || 'Export failed')
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center gap-2">
        <SlidersHorizontal className="w-4 h-4 text-secondary" />
        <h4 className="font-bold text-xs sm:text-[13px] text-text">Report Builder</h4>
      </div>

      {/* Filter Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5 text-xs">
        <div>
          <label className="block font-semibold text-text-muted mb-1">Date</label>
          <select value={filters.preset} onChange={(e) => update('preset', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            {DATE_PRESETS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>
        {filters.preset === 'custom' && (
          <>
            <div>
              <label className="block font-semibold text-text-muted mb-1">Start</label>
              <input type="date" value={filters.start_date} onChange={(e) => update('start_date', e.target.value)}
                className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
            </div>
            <div>
              <label className="block font-semibold text-text-muted mb-1">End</label>
              <input type="date" value={filters.end_date} onChange={(e) => update('end_date', e.target.value)}
                className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
            </div>
          </>
        )}
        <div>
          <label className="block font-semibold text-text-muted mb-1">Region</label>
          <select value={filters.region_id} onChange={(e) => update('region_id', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            <option value="">All regions</option>
            {regions.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block font-semibold text-text-muted mb-1">Category</label>
          <select value={filters.category} onChange={(e) => update('category', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            <option value="">All categories</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="block font-semibold text-text-muted mb-1">Product</label>
          <select value={filters.product_id} onChange={(e) => update('product_id', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            <option value="">All products</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block font-semibold text-text-muted mb-1">Min Price (৳)</label>
          <input type="number" min="0" value={filters.min_price} onChange={(e) => update('min_price', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
        </div>
        <div>
          <label className="block font-semibold text-text-muted mb-1">Max Price (৳)</label>
          <input type="number" min="0" value={filters.max_price} onChange={(e) => update('max_price', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
        </div>
        <div>
          <label className="block font-semibold text-text-muted mb-1">Quantity Level</label>
          <select value={filters.quantity_level} onChange={(e) => update('quantity_level', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            <option value="">All</option>
            <option value="low">Low (1-2 units)</option>
            <option value="medium">Medium (3-5 units)</option>
            <option value="high">High (6+ units)</option>
            <option value="custom">Custom range</option>
          </select>
        </div>
        {filters.quantity_level === 'custom' && (
          <>
            <div>
              <label className="block font-semibold text-text-muted mb-1">Min Qty</label>
              <input type="number" min="0" value={filters.min_quantity} onChange={(e) => update('min_quantity', e.target.value)}
                className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
            </div>
            <div>
              <label className="block font-semibold text-text-muted mb-1">Max Qty</label>
              <input type="number" min="0" value={filters.max_quantity} onChange={(e) => update('max_quantity', e.target.value)}
                className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary" />
            </div>
          </>
        )}
        <div>
          <label className="block font-semibold text-text-muted mb-1">Group By</label>
          <select value={filters.group_by} onChange={(e) => update('group_by', e.target.value)}
            className="w-full bg-slate-50 border border-border rounded-lg px-2.5 py-2 focus:outline-none focus:border-secondary">
            {GROUP_BY_OPTIONS.map((g) => <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between flex-wrap gap-2">
        <button
          onClick={runReport}
          disabled={loading}
          className="px-4 py-2 bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
        >
          {loading ? 'Building…' : 'Preview Report'}
        </button>
        <div className="flex items-center gap-2">
          <button onClick={() => handleExport('csv')} disabled={!!exporting}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-surface border border-border hover:bg-slate-50 text-text font-bold text-xs rounded-lg shadow-xs transition-colors disabled:opacity-50">
            {exporting === 'csv' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileSpreadsheet className="w-3.5 h-3.5 text-success" />}
            <span>Export CSV</span>
          </button>
          <button onClick={() => handleExport('pdf')} disabled={!!exporting}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-surface border border-border hover:bg-slate-50 text-text font-bold text-xs rounded-lg shadow-xs transition-colors disabled:opacity-50">
            {exporting === 'pdf' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileDown className="w-3.5 h-3.5 text-primary" />}
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {error && <div className="p-3 bg-danger-bg border border-[#F3C7BD] text-danger rounded-lg text-xs font-semibold">{error}</div>}

      {report && (
        <div className="space-y-4">
          {/* Filter Summary (auditability) */}
          <div className="bg-slate-50 border border-border rounded-lg p-3.5 text-[11px] grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-1.5">
            {Object.entries({
              Date: report.filter_summary.date_label, Category: report.filter_summary.category_label,
              Region: report.filter_summary.region_label, Product: report.filter_summary.product_label,
              Price: report.filter_summary.price_label, Quantity: report.filter_summary.quantity_label,
              Grouping: report.filter_summary.grouping_label, Generated: report.filter_summary.generated_at,
            }).map(([k, v]) => (
              <div key={k}><span className="text-text-muted font-bold">{k}: </span><span className="text-text">{v}</span></div>
            ))}
          </div>

          {/* Totals */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {[
              ['Revenue', formatCurrency(report.totals.revenue)],
              ['Orders', formatNumber(report.totals.orders)],
              ['Units', formatNumber(report.totals.units)],
              ['Avg Order Value', formatCurrency(report.totals.avg_order_value)],
            ].map(([label, val]) => (
              <div key={label} className="p-3 bg-slate-50 border border-border rounded-lg">
                <div className="text-[10.5px] font-bold text-text-muted uppercase">{label}</div>
                <div className="font-mono text-sm font-bold text-primary mt-0.5">{val}</div>
              </div>
            ))}
          </div>

          {/* Grouped rows table */}
          <div className="overflow-x-auto border border-border rounded-lg">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-border text-[10.5px] uppercase tracking-wider text-text-muted font-bold">
                  <th className="py-2.5 px-3">{report.filter_summary.grouping_label}</th>
                  <th className="py-2.5 px-3 text-right">Units</th>
                  <th className="py-2.5 px-3 text-right">Orders</th>
                  <th className="py-2.5 px-3 text-right">Revenue</th>
                  <th className="py-2.5 px-3 text-right">Avg Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {report.rows.length === 0 ? (
                  <tr><td colSpan={5} className="py-8 text-center text-text-muted">No matching sales records.</td></tr>
                ) : report.rows.map((r) => (
                  <tr key={r.group_key} className="hover:bg-slate-50/80">
                    <td className="py-2.5 px-3 font-semibold text-text">{r.group_key}</td>
                    <td className="py-2.5 px-3 text-right font-mono">{formatNumber(r.units)}</td>
                    <td className="py-2.5 px-3 text-right font-mono">{formatNumber(r.orders)}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-primary">{formatCurrency(r.revenue)}</td>
                    <td className="py-2.5 px-3 text-right font-mono text-text-muted">{formatCurrency(r.avg_price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Price range breakdown */}
          <div>
            <h5 className="font-bold text-xs text-text mb-2">Revenue by Price Range</h5>
            <div className="overflow-x-auto border border-border rounded-lg">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/75 border-b border-border text-[10.5px] uppercase tracking-wider text-text-muted font-bold">
                    <th className="py-2.5 px-3">Price Range</th>
                    <th className="py-2.5 px-3 text-right">Units</th>
                    <th className="py-2.5 px-3 text-right">Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {report.price_range_rows.map((pr) => (
                    <tr key={pr.range_label} className="hover:bg-slate-50/80">
                      <td className="py-2.5 px-3 font-semibold text-text">{pr.range_label}</td>
                      <td className="py-2.5 px-3 text-right font-mono">{formatNumber(pr.units)}</td>
                      <td className="py-2.5 px-3 text-right font-mono font-bold text-primary">{formatCurrency(pr.revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
