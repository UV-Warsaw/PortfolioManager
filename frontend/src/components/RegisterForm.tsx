import React, { useState } from 'react'
import { ApiError, registerUser } from '../services/authApi'

interface Props {
  onSuccess: (email: string, token: string) => void
  onSwitchToLogin: () => void
}

const RegisterForm: React.FC<Props> = ({ onSuccess, onSwitchToLogin }) => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await registerUser({ email, password })
      localStorage.setItem('access_token', result.access_token)
      onSuccess(result.email, result.access_token)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError('An account with this email already exists.')
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={(e) => { void handleSubmit(e) }} noValidate>
      <div className="mb-4">
        <label
          htmlFor="email"
          className="block text-xs font-medium uppercase tracking-widest mb-1"
          style={{ color: 'var(--muted)' }}
        >
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-lg px-3 py-2 text-sm outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500"
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text)',
          }}
          placeholder="you@example.com"
        />
      </div>

      <div className="mb-6">
        <label
          htmlFor="password"
          className="block text-xs font-medium uppercase tracking-widest mb-1"
          style={{ color: 'var(--muted)' }}
        >
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-lg px-3 py-2 text-sm outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500"
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text)',
          }}
          placeholder="Minimum 8 characters"
        />
      </div>

      {error !== null && (
        <div
          role="alert"
          className="mb-4 rounded-lg px-3 py-2 text-sm"
          style={{ background: 'rgba(239,68,68,0.12)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}
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
        {loading ? 'Creating account...' : 'Create account'}
      </button>

      <p className="mt-4 text-center text-xs" style={{ color: 'var(--muted)' }}>
        Already have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="font-semibold underline underline-offset-2 focus-visible:outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
          style={{ color: 'var(--accent)' }}
        >
          Sign in
        </button>
      </p>
    </form>
  )
}

export default RegisterForm
