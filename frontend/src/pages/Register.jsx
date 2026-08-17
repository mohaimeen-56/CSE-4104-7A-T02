import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { AlertCircle, KeyRound, Info } from 'lucide-react'

export const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'viewer',
    invite_code: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (field) => (e) =>
    setFormData((prev) => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (formData.role === 'admin' && !formData.invite_code.trim()) {
      setError('An admin invite code is required to register as an administrator.')
      return
    }

    setLoading(true)
    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: formData.role,
        invite_code: formData.role === 'admin' ? formData.invite_code.trim() : undefined,
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const isAdmin = formData.role === 'admin'

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[radial-gradient(circle_at_30%_20%,#234880_0%,#142b4f_45%,#0d1f3a_100%)]">
      <div className="w-full max-w-[420px] bg-surface rounded-2xl p-8 sm:p-9 shadow-2xl border border-white/10">
        {/* Brand */}
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#5B9BD5] to-[#1F3864] flex items-center justify-center font-extrabold text-lg text-white mx-auto mb-5 shadow-md">
          SQ
        </div>

        <h2 className="text-center text-xl font-bold text-text mb-1 tracking-tight">
          Create an Account
        </h2>
        <p className="text-center text-xs text-text-muted mb-7">
          Join SalesIQ — AI Sales Analytics Dashboard
        </p>

        {error && (
          <div className="flex items-start gap-2 p-3 bg-danger-bg border border-[#F3C7BD] text-danger rounded-lg text-xs font-semibold mb-4">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-xs font-bold text-text mb-1.5">Full Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={handleChange('name')}
              placeholder="e.g. Jane Smith"
              autoComplete="name"
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary rounded-lg px-3.5 py-2.5 text-sm text-text placeholder-text-muted transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-text mb-1.5">Email Address</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={handleChange('email')}
              placeholder="name@company.com"
              autoComplete="email"
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary rounded-lg px-3.5 py-2.5 text-sm text-text placeholder-text-muted transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-text mb-1.5">Password</label>
            <input
              type="password"
              required
              minLength={6}
              value={formData.password}
              onChange={handleChange('password')}
              placeholder="Minimum 6 characters"
              autoComplete="new-password"
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary rounded-lg px-3.5 py-2.5 text-sm text-text placeholder-text-muted transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-text mb-1.5">Confirm Password</label>
            <input
              type="password"
              required
              value={formData.confirmPassword}
              onChange={handleChange('confirmPassword')}
              placeholder="Re-enter your password"
              autoComplete="new-password"
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary rounded-lg px-3.5 py-2.5 text-sm text-text placeholder-text-muted transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-text mb-1.5">Account Role</label>
            <select
              value={formData.role}
              onChange={handleChange('role')}
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none rounded-lg px-3.5 py-2.5 text-sm text-text transition-colors"
            >
              <option value="viewer">Viewer — Read-only access</option>
              <option value="manager">Manager — Create & manage sales records</option>
              <option value="admin">Administrator — Requires an invite code</option>
            </select>
          </div>

          {isAdmin && (
            <div className="space-y-2">
              <div className="flex items-start gap-2 px-3 py-2.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
                <Info className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                <span>Administrator accounts require a one-time invite code generated by an existing admin from their account settings.</span>
              </div>
              <div>
                <label className="block text-xs font-bold text-text mb-1.5 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-primary" />
                  Admin Invite Code
                </label>
                <input
                  type="text"
                  required={isAdmin}
                  value={formData.invite_code}
                  onChange={handleChange('invite_code')}
                  placeholder="Paste the invite code here"
                  className="w-full bg-[#fafbfc] border border-amber-300 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-300 rounded-lg px-3.5 py-2.5 text-sm text-text font-mono placeholder-text-muted transition-colors"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-sm py-3 rounded-lg shadow-sm transition-colors mt-1"
          >
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-xs text-text-muted mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-secondary font-bold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
