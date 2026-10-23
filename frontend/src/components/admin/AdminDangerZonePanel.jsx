import React, { useState } from 'react'
import { Trash2, AlertTriangle } from 'lucide-react'
import { adminApi } from '../../services/api'

export const AdminDangerZonePanel = ({ onDataDeleted }) => {
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  // Require the user to type "DELETE ALL" before confirming
  const [confirmText, setConfirmText] = useState('')

  const openConfirm = () => {
    setError('')
    setResult(null)
    setConfirmText('')
    setConfirmOpen(true)
  }

  const handleDeleteAll = async () => {
    if (confirmText !== 'DELETE ALL') {
      setError('Please type DELETE ALL exactly to confirm.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await adminApi.deleteAllSales()
      setResult(res.message || 'All sales deleted.')
      setConfirmOpen(false)
      setConfirmText('')
      if (onDataDeleted) onDataDeleted()
    } catch (err) {
      setError(err.message || 'Failed to delete sales data.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-surface border border-[#F3C7BD] rounded-xl p-5 sm:p-6 shadow-sm space-y-4">
      <h4 className="font-bold text-sm text-danger flex items-center gap-2">
        <AlertTriangle className="w-4 h-4" />
        <span>Danger Zone — Data Management</span>
      </h4>

      <p className="text-xs text-text-muted leading-relaxed">
        These actions are <span className="font-bold text-danger">permanent and irreversible</span>.
        Use with extreme caution. All deletions are final — there is no undo.
      </p>

      {result && (
        <div className="p-3 bg-success-bg border border-success/30 text-success rounded-lg text-xs font-semibold">
          ✓ {result}
        </div>
      )}

      <div className="flex items-start justify-between gap-4 p-4 bg-danger-bg border border-[#F3C7BD] rounded-lg">
        <div>
          <div className="text-xs font-bold text-text">Delete All Data (Sales & Products)</div>
          <div className="text-[11px] text-text-muted mt-0.5">
            Permanently removes all sales transactions and products from the database for a fresh start. User accounts and regions are preserved.
          </div>
        </div>
        <button
          onClick={openConfirm}
          className="flex-shrink-0 flex items-center gap-1.5 px-3.5 py-2 bg-danger hover:opacity-90 text-white font-bold text-xs rounded-lg shadow-xs transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Delete All
        </button>
      </div>

      {/* Confirmation modal */}
      {confirmOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl p-6 max-w-sm w-full space-y-4 shadow-lg border border-[#F3C7BD]">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-danger flex-shrink-0" />
              <h5 className="font-bold text-sm text-danger">Delete All Sales & Products?</h5>
            </div>
            <p className="text-xs text-text-muted leading-relaxed">
              This will <span className="font-bold text-danger">permanently delete all sales records and products</span> in the database.
              This action <span className="font-bold">cannot be undone</span>.
            </p>
            <div>
              <label className="block text-xs font-semibold text-text mb-1.5">
                Type <span className="font-mono text-danger">DELETE ALL</span> to confirm
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE ALL"
                className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs text-text font-mono focus:outline-none focus:border-danger"
                autoFocus
              />
            </div>
            {error && <p className="text-xs text-danger font-semibold">{error}</p>}
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setConfirmOpen(false); setConfirmText(''); setError('') }}
                className="px-4 py-2 text-xs font-bold text-text-muted hover:text-text"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAll}
                disabled={loading || confirmText !== 'DELETE ALL'}
                className="px-4 py-2 bg-danger hover:opacity-90 disabled:opacity-40 text-white font-bold text-xs rounded-lg transition-colors"
              >
                {loading ? 'Deleting…' : 'Confirm Delete All'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
