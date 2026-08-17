import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { authApi, adminApi } from '../services/api'
import { RoleBadge } from '../components/common/RoleBadge'
import { UserAvatar } from '../components/common/UserAvatar'
import { AdminMaintenancePanel } from '../components/admin/AdminMaintenancePanel'
import { User, Lock, LogOut, CheckCircle2, Shield, KeyRound, Plus, Trash2, Copy, Check, Clock } from 'lucide-react'

const AdminInvitePanel = () => {
  const [codes, setCodes] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [copiedId, setCopiedId] = useState(null)
  const [genError, setGenError] = useState('')

  const fetchCodes = useCallback(async () => {
    setLoading(true)
    try {
      const res = await adminApi.listInviteCodes()
      setCodes(res.data || [])
    } catch {
      // silently ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchCodes() }, [fetchCodes])

  const handleGenerate = async () => {
    setGenerating(true)
    setGenError('')
    try {
      await adminApi.generateInviteCode()
      await fetchCodes()
    } catch (err) {
      setGenError(err.message || 'Failed to generate code.')
    } finally {
      setGenerating(false)
    }
  }

  const handleRevoke = async (id) => {
    try {
      await adminApi.revokeInviteCode(id)
      setCodes(prev => prev.filter(c => c.id !== id))
    } catch (err) {
      alert(err.message || 'Failed to revoke code.')
    }
  }

  const handleCopy = (code, id) => {
    navigator.clipboard.writeText(code).catch(() => {})
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const isExpired = (expiresAt) => new Date(expiresAt) < new Date()

  const activeCodes = codes.filter(c => !c.used && !isExpired(c.expires_at))
  const pastCodes = codes.filter(c => c.used || isExpired(c.expires_at))

  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <h4 className="font-bold text-sm text-text flex items-center gap-2">
            <KeyRound className="w-4 h-4 text-primary" />
            Admin Invite Codes
          </h4>
          <p className="text-xs text-text-muted mt-0.5">
            Generate one-time codes to allow new users to register as administrators. Each code expires in 48 hours.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex-shrink-0 flex items-center gap-1.5 px-3.5 py-2 bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs rounded-lg shadow-xs transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          {generating ? 'Generating…' : 'Generate Code'}
        </button>
      </div>

      {genError && (
        <p className="text-danger text-xs font-semibold mb-3">{genError}</p>
      )}

      {loading ? (
        <div className="space-y-2">
          {[1, 2].map(i => <div key={i} className="skeleton h-10 rounded-lg" />)}
        </div>
      ) : activeCodes.length === 0 && pastCodes.length === 0 ? (
        <div className="text-center py-6 text-xs text-text-muted">
          No invite codes yet. Generate one to share with a new administrator.
        </div>
      ) : (
        <div className="space-y-4">
          {activeCodes.length > 0 && (
            <div>
              <div className="text-[11px] font-bold text-text-muted uppercase tracking-wider mb-2">Active</div>
              <div className="space-y-2">
                {activeCodes.map(c => (
                  <div key={c.id} className="flex items-center justify-between gap-3 px-3 py-2.5 bg-success-bg border border-success/20 rounded-lg">
                    <div className="flex items-center gap-2 min-w-0">
                      <code className="font-mono text-xs text-text font-semibold truncate">{c.code}</code>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-[10px] text-text-muted whitespace-nowrap flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Expires {new Date(c.expires_at).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => handleCopy(c.code, c.id)}
                        className="p-1.5 rounded text-text-muted hover:text-secondary hover:bg-sunken transition-colors"
                        title="Copy code"
                      >
                        {copiedId === c.id ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                      <button
                        onClick={() => handleRevoke(c.id)}
                        className="p-1.5 rounded text-text-muted hover:text-danger hover:bg-danger-bg transition-colors"
                        title="Revoke code"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {pastCodes.length > 0 && (
            <div>
              <div className="text-[11px] font-bold text-text-muted uppercase tracking-wider mb-2">Used / Expired</div>
              <div className="space-y-1.5">
                {pastCodes.map(c => (
                  <div key={c.id} className="flex items-center justify-between gap-3 px-3 py-2 bg-slate-50 border border-border rounded-lg opacity-60">
                    <code className="font-mono text-xs text-text-muted truncate">{c.code}</code>
                    <span className="text-[10px] text-text-muted flex-shrink-0">
                      {c.used ? `Used by ${c.used_by_name || 'unknown'}` : 'Expired'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export const Settings = () => {
  const { user, logout, setUser } = useAuth()

  const [name, setName] = useState(user?.name || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    setMessage('')
    setError('')

    if (newPassword && newPassword !== confirmPassword) {
      setError('New passwords do not match.')
      return
    }

    setLoading(true)
    try {
      const payload = { name: name.trim() }
      if (newPassword) {
        payload.password = newPassword
        payload.current_password = currentPassword
      }

      const res = await authApi.updateProfile(payload)
      if (res.data) {
        setUser(res.data)
        localStorage.setItem('salesiq_user', JSON.stringify(res.data))
        setMessage('Profile updated successfully!')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
      }
    } catch (err) {
      setError(err.message || 'Failed to update profile.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-5 max-w-3xl">
      <div>
        <h1 className="text-xl font-bold text-text tracking-tight">
          Account Settings
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Manage your personal profile, credentials, and user preferences
        </p>
      </div>

      {message && (
        <div className="p-4 bg-success-bg border border-success/30 text-success rounded-xl text-xs flex items-center gap-2 font-semibold">
          <CheckCircle2 className="w-4 h-4" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-danger-bg border border-[#F3C7BD] text-danger rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Profile Overview Card */}
      <div className="bg-surface border border-border rounded-xl p-5 sm:p-6 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4 text-center sm:text-left">
          <UserAvatar name={user?.name} size="xl" />
          <div>
            <h4 className="font-bold text-base text-text">{user?.name}</h4>
            <p className="text-xs text-text-muted">{user?.email}</p>
            <div className="mt-2">
              <RoleBadge role={user?.role} />
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-4 py-2 border border-danger/40 text-danger hover:bg-danger-bg rounded-lg text-xs font-bold transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Log Out</span>
        </button>
      </div>

      {/* Edit Profile & Password Form */}
      <div className="bg-surface border border-border rounded-xl p-5 sm:p-6 shadow-sm">
        <h4 className="font-bold text-sm text-text mb-4 flex items-center gap-2">
          <User className="w-4 h-4 text-primary" />
          <span>Update Profile Details</span>
        </h4>

        <form onSubmit={handleUpdateProfile} className="space-y-4 text-xs sm:text-sm">
          <div>
            <label className="block font-semibold text-text mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs sm:text-sm text-text focus:outline-none focus:border-secondary"
            />
          </div>

          <div>
            <label className="block font-semibold text-text mb-1">Email Address</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full bg-slate-100 border border-border rounded-lg px-3.5 py-2.5 text-xs sm:text-sm text-text-muted cursor-not-allowed"
            />
            <span className="text-[10.5px] text-text-muted mt-1 block">
              Contact an administrator to change your email address.
            </span>
          </div>

          <div className="pt-3 border-t border-border space-y-3">
            <h5 className="font-bold text-xs text-text flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-secondary" />
              <span>Change Password (optional)</span>
            </h5>

            <div>
              <label className="block font-semibold text-text mb-1">Current Password</label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Required only if changing password"
                className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs sm:text-sm text-text focus:outline-none focus:border-secondary"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-text mb-1">New Password</label>
                <input
                  type="password"
                  minLength={6}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs sm:text-sm text-text focus:outline-none focus:border-secondary"
                />
              </div>
              <div>
                <label className="block font-semibold text-text mb-1">Confirm New Password</label>
                <input
                  type="password"
                  minLength={6}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-border rounded-lg px-3.5 py-2.5 text-xs sm:text-sm text-text focus:outline-none focus:border-secondary"
                />
              </div>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
            >
              {loading ? 'Saving changes…' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>

      {user?.role === 'admin' && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-text tracking-tight flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-primary" />
            <span>Admin Settings</span>
          </h3>
          <AdminMaintenancePanel />
          <AdminInvitePanel />
        </div>
      )}

      {/* Project & Team Credits */}
      <div className="bg-slate-50 border border-border rounded-xl p-4 text-xs text-text-muted space-y-1">
        <div className="font-bold text-text">CSE4104-7A-T02 · Project Team</div>
        <p>
          Mohaimeen Islam Pial (11230121094) · Sk Mesbaul Arefin (11230121077) · Sumaiya Akter (11230121081) · Afia Maliha Priota (11230121090)
        </p>
        <p className="text-[11px]">Northern University of Business and Technology, Khulna</p>
      </div>
    </div>
  )
}
