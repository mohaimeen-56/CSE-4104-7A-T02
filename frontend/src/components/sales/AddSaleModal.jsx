import React, { useState, useEffect } from 'react'
import { Modal } from '../common/Modal'
import { productsApi, regionsApi, salesApi } from '../../services/api'
import { formatCurrency } from '../../utils/formatters'

export const AddSaleModal = ({ isOpen, onClose, onSuccess, initialData = null }) => {
  const isEditing = !!initialData
  const [products, setProducts] = useState([])
  const [regions, setRegions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const nowTimeInDhaka = () =>
    new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Dhaka', hour: '2-digit', minute: '2-digit', hour12: false })

  const [formData, setFormData] = useState({
    product_id: '',
    region_id: '',
    quantity: 1,
    unit_price: 0,
    sale_date: new Date().toISOString().split('T')[0],
    sale_time: nowTimeInDhaka(),
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [prodRes, regRes] = await Promise.all([
          productsApi.list(),
          regionsApi.list(),
        ])
        setProducts(prodRes.data || [])
        setRegions(regRes.data || [])

        if (initialData) {
          const existingTime = initialData.sale_datetime
            ? new Date(initialData.sale_datetime).toLocaleTimeString('en-GB', {
                timeZone: 'Asia/Dhaka', hour: '2-digit', minute: '2-digit', hour12: false,
              })
            : nowTimeInDhaka()
          setFormData({
            product_id: String(initialData.product_id),
            region_id: String(initialData.region_id),
            quantity: initialData.quantity,
            unit_price: Number(initialData.unit_price),
            sale_date: initialData.sale_date,
            sale_time: existingTime,
          })
        } else if (prodRes.data?.length > 0 && regRes.data?.length > 0) {
          setFormData((prev) => ({
            ...prev,
            product_id: String(prodRes.data[0].id),
            region_id: String(regRes.data[0].id),
            unit_price: 50000,
          }))
        }
      } catch (e) {
        setError('Failed to load products or regions')
      }
    }

    if (isOpen) {
      setError('')
      fetchData()
    }
  }, [isOpen, initialData])

  const handleProductChange = (e) => {
    const pId = e.target.value
    setFormData((prev) => ({
      ...prev,
      product_id: pId,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        product_id: Number(formData.product_id),
        region_id: Number(formData.region_id),
        quantity: Number(formData.quantity),
        unit_price: Number(formData.unit_price),
        sale_date: formData.sale_date,
        sale_time: formData.sale_time || null,
      }

      if (isEditing) {
        await salesApi.update(initialData.id, payload)
      } else {
        await salesApi.create(payload)
      }

      onSuccess()
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to save sales record')
    } finally {
      setLoading(false)
    }
  }

  const estimatedTotal = (Number(formData.quantity) || 0) * (Number(formData.unit_price) || 0)

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? 'Edit Sales Record' : 'Record New Sale'}
      maxWidth="max-w-md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs sm:text-sm">
        {error && (
          <div className="p-3 bg-danger-bg border border-[#F3C7BD] text-danger rounded-lg text-xs font-semibold">
            {error}
          </div>
        )}

        <div>
          <label className="block font-semibold text-text mb-1">Select Product</label>
          <select
            value={formData.product_id}
            onChange={handleProductChange}
            required
            className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
          >
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.category || 'General'}) — Stock: {p.stock}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-semibold text-text mb-1">Select Region</label>
          <select
            value={formData.region_id}
            onChange={(e) => setFormData({ ...formData, region_id: e.target.value })}
            required
            className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
          >
            {regions.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}, {r.country}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block font-semibold text-text mb-1">Quantity</label>
            <input
              type="number"
              min="1"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: Math.max(1, parseInt(e.target.value) || 1) })}
              required
              className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
            />
          </div>

          <div>
            <label className="block font-semibold text-text mb-1">Unit Price (৳)</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.unit_price}
              onChange={(e) => setFormData({ ...formData, unit_price: parseFloat(e.target.value) || 0 })}
              required
              className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block font-semibold text-text mb-1">Sale Date</label>
            <input
              type="date"
              value={formData.sale_date}
              onChange={(e) => setFormData({ ...formData, sale_date: e.target.value })}
              required
              className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
            />
          </div>
          <div>
            <label className="block font-semibold text-text mb-1">Sale Time</label>
            <input
              type="time"
              value={formData.sale_time}
              onChange={(e) => setFormData({ ...formData, sale_time: e.target.value })}
              className="w-full bg-slate-50 border border-border rounded-lg px-3 py-2 text-xs sm:text-sm focus:outline-none focus:border-secondary"
            />
            <span className="text-[10.5px] text-text-muted mt-1 block">Leave blank to use the server's current time.</span>
          </div>
        </div>

        <div className="p-3 bg-[#F8FAFC] border border-border rounded-lg flex items-center justify-between">
          <span className="font-semibold text-text-muted text-xs uppercase tracking-wider">
            Total Price:
          </span>
          <span className="font-mono font-bold text-primary text-base">
            {formatCurrency(estimatedTotal)}
          </span>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-border rounded-lg font-semibold text-xs text-text-muted hover:bg-slate-100 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2 bg-primary hover:bg-primary-light text-white rounded-lg font-bold text-xs shadow-sm transition-colors disabled:opacity-50"
          >
            {loading ? 'Saving…' : isEditing ? 'Update Sale' : 'Add Sale'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
