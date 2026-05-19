import React, { useState } from 'react'
import { requestPasswordReset } from '../services/authApi'

interface Props {
  onSwitchToLogin: () => void
}

const ForgotPasswordForm: React.FC<Props> = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await requestPasswordReset(email)
    } finally {
      setLoading(false)
      setSubmitted(true)
    }
  }

  if (submitted) {
    return (
      <div className="text-center">
        <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
          If that address is registered you will receive a reset link shortly.
        </p>
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-sm font-semibold underline underline-offset-2
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
          style={{ color: 'var(--accent)' }}
        >
          Back to sign in
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={(e) => { void handleSubmit(e) }} noValidate>
      <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
        Enter your email address and we will send you a reset link.
      </p>

      <div className="mb-6">
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

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
          disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
        style={{ background: 'var(--accent)', color: '#fff' }}
      >
        {loading ? 'Sending...' : 'Send reset link'}
      </button>

      <p className="mt-4 text-center text-xs" style={{ color: 'var(--muted)' }}>
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="font-semibold underline underline-offset-2 focus-visible:outline-none
            focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
          style={{ color: 'var(--accent)' }}
        >
          Back to sign in
        </button>
      </p>
    </form>
  )
}

export default ForgotPasswordForm
