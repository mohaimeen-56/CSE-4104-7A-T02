import React, { useState, useEffect, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { salesApi, regionsApi } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { AddSaleModal } from '../components/sales/AddSaleModal'
import { formatCurrency, formatDate, formatNumber } from '../utils/formatters'
import {
  Plus,
  Upload,
  Search,
  ChevronLeft,
  ChevronRight,
  Filter,
  Trash2,
  Edit2,
  Calendar,
} from 'lucide-react'

export const SalesRecords = () => {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const canMutate = user?.role === 'admin' || user?.role === 'manager'
  const isAdmin = user?.role === 'admin'

  const [sales, setSales] = useState([])
  const [regions, setRegions] = useState([])
  const [pagination, setPagination] = useState({ page: 1, total_pages: 1, total: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Filters state
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '')
  const [selectedRegion, setSelectedRegion] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingSale, setEditingSale] = useState(null)

  const fetchSales = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const params = {
        page,
        page_size: 10,
        search: searchTerm || undefined,
        region_id: selectedRegion || undefined,
        category: selectedCategory || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      }
      const res = await salesApi.list(params)
      if (res.data) {
        setSales(res.data)
        setPagination(res.pagination)
      }
    } catch (err) {
      setError(err.message || 'Failed to load sales records')
    } finally {
      setLoading(false)
    }
  }, [page, searchTerm, selectedRegion, selectedCategory, startDate, endDate])

  useEffect(() => {
    fetchSales()
  }, [fetchSales])

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const res = await regionsApi.list()
        setRegions(res.data || [])
      } catch (e) {}
    }
    fetchRegions()
  }, [])

  const handleDelete = async (id, productName) => {
    if (!window.confirm(`Are you sure you want to delete this sale record for "${productName}"?`)) return
    try {
      await salesApi.delete(id)
      fetchSales()
    } catch (err) {
      alert(err.message || 'Failed to delete sale record')
    }
  }

  const getRegionBadgeClass = (regionName) => {
    const r = (regionName || '').toLowerCase()
    if (r.includes('dhaka')) return 'bg-[#E3EEFB] text-primary'
    if (r.includes('chittagong')) return 'bg-[#FDEDE3] text-[#A2541D]'
    if (r.includes('khulna')) return 'bg-[#E9F5EC] text-success'
    if (r.includes('sylhet')) return 'bg-[#F3E8FF] text-purple-800'
    return 'bg-slate-100 text-slate-700'
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-text tracking-tight">
            Sales Records
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Manage, filter, and inspect detailed sales transactions
          </p>
        </div>

        {canMutate && (
          <div className="flex items-center gap-2">
            <Link
              to="/sales/upload"
              className="flex items-center gap-1.5 px-3.5 py-2 bg-surface border border-border hover:bg-slate-50 text-text font-bold text-xs rounded-lg shadow-xs transition-colors"
            >
              <Upload className="w-3.5 h-3.5 text-secondary" />
              <span>Upload CSV</span>
            </Link>
            <button
              onClick={() => {
                setEditingSale(null)
                setIsModalOpen(true)
              }}
              className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-light text-white font-bold text-xs rounded-lg shadow-xs transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Sale</span>
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-danger-bg border border-[#F3C7BD] text-danger rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Filter Row directly above table matching mockup */}
      <div className="flex flex-wrap items-center gap-2.5">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value)
              setPage(1)
            }}
            placeholder="Search records…"
            className="w-full bg-surface border border-border rounded-lg pl-8 pr-3 py-2 text-xs text-text placeholder-text-muted focus:outline-none focus:border-secondary shadow-xs"
          />
        </div>

        {/* Region Filter */}
        <select
          value={selectedRegion}
          onChange={(e) => {
            setSelectedRegion(e.target.value)
            setPage(1)
          }}
          className="bg-surface border border-border rounded-lg px-3 py-2 text-xs font-semibold text-text-muted focus:outline-none focus:border-secondary shadow-xs"
        >
          <option value="">📍 All Regions</option>
          {regions.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>

        {/* Category Filter */}
        <select
          value={selectedCategory}
          onChange={(e) => {
            setSelectedCategory(e.target.value)
            setPage(1)
          }}
          className="bg-surface border border-border rounded-lg px-3 py-2 text-xs font-semibold text-text-muted focus:outline-none focus:border-secondary shadow-xs"
        >
          <option value="">🏷 All Categories</option>
          <option value="Phone">Phone</option>
          <option value="Laptop">Laptop</option>
          <option value="Tablet">Tablet</option>
          <option value="Audio">Audio</option>
          <option value="Electronics">Electronics</option>
          <option value="Furniture">Furniture</option>
        </select>

        {/* Date Filters */}
        <div className="flex items-center gap-1.5 bg-surface border border-border rounded-lg px-2.5 py-2 text-xs shadow-xs text-text-muted">
          <Calendar className="w-3.5 h-3.5" />
          <input
            type="date"
            value={startDate}
            onChange={(e) => {
              setStartDate(e.target.value)
              setPage(1)
            }}
            className="bg-transparent text-text focus:outline-none"
          />
          <span>to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => {
              setEndDate(e.target.value)
              setPage(1)
            }}
            className="bg-transparent text-text focus:outline-none"
          />
        </div>
      </div>

      {/* Sales Table Card */}
      <div className="bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50/75 border-b border-border text-[10.5px] uppercase tracking-wider text-text-muted font-bold">
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Product</th>
                <th className="py-3 px-4">Region</th>
                <th className="py-3 px-4 text-center">Qty</th>
                <th className="py-3 px-4 text-right">Unit Price</th>
                <th className="py-3 px-4 text-right">Total</th>
                {canMutate && <th className="py-3 px-4 text-center">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-medium">
              {loading ? (
                <tr>
                  <td colSpan={canMutate ? 7 : 6} className="py-12 text-center text-text-muted">
                    Loading sales records…
                  </td>
                </tr>
              ) : sales.length === 0 ? (
                <tr>
                  <td colSpan={canMutate ? 7 : 6} className="py-12 text-center text-text-muted">
                    No sales records matched your criteria.
                  </td>
                </tr>
              ) : (
                sales.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 text-text-muted whitespace-nowrap">
                      {formatDate(s.sale_date)}
                      {s.sale_datetime && (
                        <span className="text-[10px] text-text-muted/80 font-mono block">
                          {new Date(s.sale_datetime).toLocaleTimeString('en-GB', { timeZone: 'Asia/Dhaka', hour: '2-digit', minute: '2-digit' })}
                          {s.is_estimated_time && <span className="ml-1 text-warning" title="Estimated time (not captured)">~</span>}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-text whitespace-nowrap">
                      {s.product?.name || `Product #${s.product_id}`}
                      <span className="text-[10px] text-text-muted font-normal block">
                        {s.product?.category || 'General'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`text-[11px] font-bold px-2.5 py-1 rounded-full ${getRegionBadgeClass(
                          s.region?.name
                        )}`}
                      >
                        {s.region?.name || `Region #${s.region_id}`}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono font-semibold text-text">
                      {s.quantity}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-semibold text-text-muted whitespace-nowrap">
                      {formatCurrency(s.unit_price)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-primary whitespace-nowrap">
                      {formatCurrency(s.total_price)}
                    </td>
                    {canMutate && (
                      <td className="py-3.5 px-4 text-center whitespace-nowrap">
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            onClick={() => {
                              setEditingSale(s)
                              setIsModalOpen(true)
                            }}
                            className="p-1 text-text-muted hover:text-secondary rounded hover:bg-slate-100 transition-colors"
                            title="Edit sale"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                          {isAdmin && (
                            <button
                              onClick={() => handleDelete(s.id, s.product?.name || 'Item')}
                              className="p-1 text-text-muted hover:text-danger rounded hover:bg-slate-100 transition-colors"
                              title="Delete sale"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-3.5 px-4 border-t border-border flex items-center justify-between text-xs bg-slate-50/50">
          <div className="text-text-muted">
            Showing {sales.length} of {pagination.total} records
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || loading}
              className="flex items-center gap-1 px-3 py-1.5 border border-border rounded-md font-semibold text-text-muted hover:text-text hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Prev
            </button>
            <span className="font-semibold px-2 text-text">
              {page} / {pagination.total_pages || 1}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
              disabled={page >= pagination.total_pages || loading}
              className="flex items-center gap-1 px-3 py-1.5 border border-border rounded-md font-semibold text-text-muted hover:text-text hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Next <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Add / Edit Sale Modal */}
      <AddSaleModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchSales}
        initialData={editingSale}
      />
    </div>
  )
}
