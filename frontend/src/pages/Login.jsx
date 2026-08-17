import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { AlertCircle } from 'lucide-react'

export const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError('Incorrect email or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[radial-gradient(circle_at_30%_20%,#234880_0%,#142b4f_45%,#0d1f3a_100%)]">
      <div className="w-full max-w-[390px] bg-surface rounded-2xl p-8 sm:p-9 shadow-2xl border border-white/10">
        {/* Brand */}
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#5B9BD5] to-[#1F3864] flex items-center justify-center font-extrabold text-lg text-white mx-auto mb-5 shadow-md">
          SQ
        </div>

        <h2 className="text-center text-xl font-bold text-text mb-1 tracking-tight">
          Sign in to SalesIQ
        </h2>
        <p className="text-center text-xs text-text-muted mb-7">
          Enter your credentials to access your dashboard
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-text mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="name@company.com"
              className="w-full bg-[#fafbfc] border border-border focus:border-secondary focus:outline-none focus:ring-1 focus:ring-secondary rounded-lg px-3.5 py-2.5 text-sm text-text placeholder-text-muted transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-text mb-1.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="••••••••"
              className={`w-full bg-[#fafbfc] border rounded-lg px-3.5 py-2.5 text-sm text-text focus:outline-none transition-colors ${
                error
                  ? 'border-danger bg-danger-bg/30'
                  : 'border-border focus:border-secondary focus:ring-1 focus:ring-secondary'
              }`}
            />
            {error && (
              <p className="text-danger text-[11.5px] font-semibold mt-1.5 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-primary-light disabled:opacity-50 text-white font-bold text-sm py-3 rounded-lg shadow-sm transition-colors mt-1"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-xs text-text-muted mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-secondary font-bold hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}
