import React, { useState } from 'react'
import { ApiError, confirmPasswordReset } from '../services/authApi'

interface Props {
  token: string
  onSuccess: () => void
}

const ResetPasswordForm: React.FC<Props> = ({ token, onSuccess }) => {
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)
    try {
      await confirmPasswordReset(token, password)
      onSuccess()
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError('This reset link is invalid or has already been used.')
      } else {
        setError('Something went wrong. Please request a new reset link.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={(e) => { void handleSubmit(e) }} noValidate>
      <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
        Choose a new password for your account.
      </p>

      <div className="mb-4">
        <label
          htmlFor="new-password"
          className="block text-xs font-medium uppercase tracking-widest mb-1"
          style={{ color: 'var(--muted)' }}
        >
          New password
        </label>
        <input
          id="new-password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-lg px-3 py-2 text-sm outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500"
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text)',
          }}
          placeholder="Min. 8 characters"
        />
      </div>

      <div className="mb-6">
        <label
          htmlFor="confirm-password"
          className="block text-xs font-medium uppercase tracking-widest mb-1"
          style={{ color: 'var(--muted)' }}
        >
          Confirm password
        </label>
        <input
          id="confirm-password"
          type="password"
          autoComplete="new-password"
          required
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="w-full rounded-lg px-3 py-2 text-sm outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500"
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text)',
          }}
          placeholder="Repeat new password"
        />
      </div>

      {error !== null && (
        <div
          role="alert"
          className="mb-4 rounded-lg px-3 py-2 text-sm"
          style={{
            background: 'rgba(239,68,68,0.12)',
            color: '#f87171',
            border: '1px solid rgba(239,68,68,0.3)',
          }}
        >
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
          disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
        style={{ background: 'var(--accent)', color: '#fff' }}
      >
        {loading ? 'Saving...' : 'Set new password'}
      </button>
    </form>
  )
}

export default ResetPasswordForm
