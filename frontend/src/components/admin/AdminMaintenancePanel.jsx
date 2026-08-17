import React, { useState, useEffect } from 'react'
import { ShieldAlert, Power, History } from 'lucide-react'
import { adminApi } from '../../services/api'
import { useMaintenance } from '../../context/MaintenanceContext'

export const AdminMaintenancePanel = () => {
  const { status, refresh } = useMaintenance()
  const [reason, setReason] = useState('')
  const [message, setMessage] = useState('')
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pendingAction, setPendingAction] = useState(null) // 'enable' | 'disable'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [auditLog, setAuditLog] = useState([])
  const [showAudit, setShowAudit] = useState(false)

  useEffect(() => {
    if (showAudit) {
      adminApi.getMaintenanceAuditLog().then((res) => setAuditLog(res.data || [])).catch(() => {})
    }
  }, [showAudit, status?.enabled])

  const openConfirm = (action) => {
    setError('')
    setPendingAction(action)
    setConfirmOpen(true)
  }

  const handleConfirm = async () => {
    setLoading(true)
    setError('')
    try {
      if (pendingAction === 'enable') {
        if (!reason.trim()) {
          setError('A reason is required to enable maintenance mode.')
          setLoading(false)
          return
        }
        await adminApi.enableMaintenance({ reason: reason.trim(), message: message.trim() || undefined })
        setReason('')
        setMessage('')
      } else {
        await adminApi.disableMaintenance({ reason: reason.trim() || undefined })
        setReason('')
      }
      await refresh()
      setConfirmOpen(false)
    } catch (err) {
      setError(err.message || 'Action failed.')
    } finally {
      setLoading(false)
    }
  }

  const enabled = !!status?.enabled

  return (
    <div className="bg-surface border border-border rounded-xl p-5 sm:p-6 shadow-sm space-y-4">
      <h4 className="font-bold text-sm text-text flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-primary" />
        <span>System Status — Maintenance Mode</span>
      </h4>

      <div className={`rounded-lg p-4 border text-xs space-y-2 ${enabled ? 'bg-danger-bg border-[#F3C7BD]' : 'bg-success-bg border-success/30'}`}>
        <div className="flex items-center justify-between">
          <span className="font-bold text-text">Application</span>
          <span className={`font-bold ${enabled ? 'text-danger' : 'text-success'}`}>
            {enabled ? 'Maintenance Mode' : 'Online'}
          </span>
        </div>
        {enabled && (
          <div className="space-y-1 pt-1 border-t border-black/5 font-mono text-[11px] text-text-muted">
            {status.enabled_by_name && <div>Enabled by: <span className="text-text font-bold">{status.enabled_by_name}</span></div>}
            {status.started_at && <div>Started: <span className="text-text font-bold">{new Date(status.started_at).toLocaleString()}</span></div>}
            {status.reason && <div>Reason: <span className="text-text font-bold">{status.reason}</span></div>}
          </div>
        )}
      </div>

      {!enabled ? (
        <div className="space-y-3">
          <div>
            <label className="block font-semibold text-text mb-1 text-xs">Reason (required)</label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Database maintenance"
              className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs text-text focus:outline-none focus:border-secondary"
            />
          </div>
          <div>
            <label className="block font-semibold text-text mb-1 text-xs">Custom maintenance message (optional)</label>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Shown to locked-out users"
              className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs text-text focus:outline-none focus:border-secondary"
            />
          </div>
          <button
            onClick={() => openConfirm('enable')}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-danger hover:opacity-90 text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
          >
            <Power className="w-3.5 h-3.5" />
            <span>Enable Maintenance Mode</span>
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <label className="block font-semibold text-text mb-1 text-xs">Disable reason (optional)</label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Maintenance complete"
              className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs text-text focus:outline-none focus:border-secondary"
            />
          </div>
          <button
            onClick={() => openConfirm('disable')}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-primary hover:bg-primary-light text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
          >
            <Power className="w-3.5 h-3.5" />
            <span>Disable Maintenance Mode</span>
          </button>
        </div>
      )}

      <button
        onClick={() => setShowAudit((v) => !v)}
        className="flex items-center gap-1.5 text-[11px] font-bold text-text-muted hover:text-text transition-colors"
      >
        <History className="w-3.5 h-3.5" />
        <span>{showAudit ? 'Hide' : 'Show'} audit log</span>
      </button>
      {showAudit && (
        <div className="rounded-lg border border-border divide-y divide-border max-h-56 overflow-y-auto">
          {auditLog.length === 0 && <div className="p-3 text-[11px] text-text-muted">No maintenance events recorded yet.</div>}
          {auditLog.map((log) => (
            <div key={log.id} className="p-3 text-[11px] flex flex-col gap-0.5">
              <div className="flex items-center justify-between">
                <span className={`font-bold ${log.action === 'enabled' ? 'text-danger' : 'text-success'}`}>
                  {log.action === 'enabled' ? 'Enabled' : 'Disabled'}
                </span>
                <span className="text-text-muted font-mono">{new Date(log.created_at).toLocaleString()}</span>
              </div>
              <div className="text-text">{log.performed_by_name || 'Unknown admin'}{log.reason ? ` — ${log.reason}` : ''}</div>
            </div>
          ))}
        </div>
      )}

      {confirmOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl p-6 max-w-sm w-full space-y-4 shadow-lg">
            <h5 className="font-bold text-sm text-text">
              {pendingAction === 'enable' ? 'Enable Maintenance Mode?' : 'Disable Maintenance Mode?'}
            </h5>
            <p className="text-xs text-text-muted leading-relaxed">
              {pendingAction === 'enable'
                ? 'Maintenance Mode will temporarily lock normal application usage for all users except authorized administrators.'
                : 'This will restore normal application access for all users.'}
            </p>
            {error && <p className="text-xs text-danger font-semibold">{error}</p>}
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setConfirmOpen(false)}
                className="px-4 py-2 text-xs font-bold text-text-muted hover:text-text"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={loading}
                className="px-4 py-2 bg-danger hover:opacity-90 disabled:opacity-50 text-white font-bold text-xs rounded-lg"
              >
                {loading ? 'Working…' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
