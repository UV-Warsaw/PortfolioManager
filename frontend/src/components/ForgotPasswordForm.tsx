import React, { useState } from 'react'
import { ApiError, confirmPasswordReset, requestPasswordReset } from '../services/authApi'

interface Props {
  onSwitchToLogin: () => void
}

type Step = 'email' | 'code' | 'done'

const ForgotPasswordForm: React.FC<Props> = ({ onSwitchToLogin }) => {
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await requestPasswordReset(email)
      setStep('code')
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async (e: React.FormEvent) => {
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
      await confirmPasswordReset(email, code, password)
      setStep('done')
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError('Invalid or expired code. Please request a new one.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const inputStyle: React.CSSProperties = {
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.1)',
    color: 'var(--text)',
  }

  if (step === 'done') {
    return (
      <div className="text-center">
        <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
          Your password has been updated. You can now sign in.
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

  if (step === 'code') {
    return (
      <form onSubmit={(e) => { void handleConfirm(e) }} noValidate>
        <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
          A 6-digit code was sent to <strong style={{ color: 'var(--text)' }}>{email}</strong>.
          Enter it below along with your new password.
        </p>

        <div className="mb-4">
          <label
            htmlFor="reset-code"
            className="block text-xs font-medium uppercase tracking-widest mb-1"
            style={{ color: 'var(--muted)' }}
          >
            Verification code
          </label>
          <input
            id="reset-code"
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            required
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
            className="w-full rounded-lg px-3 py-2 text-sm outline-none
              focus-visible:ring-2 focus-visible:ring-indigo-500 tracking-widest text-center"
            style={inputStyle}
            placeholder="000000"
          />
        </div>

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
            style={inputStyle}
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
            style={inputStyle}
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

        <p className="mt-4 text-center text-xs" style={{ color: 'var(--muted)' }}>
          <button
            type="button"
            onClick={() => { setStep('email'); setError(null) }}
            className="font-semibold underline underline-offset-2 focus-visible:outline-none
              focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
            style={{ color: 'var(--accent)' }}
          >
            Request a new code
          </button>
        </p>
      </form>
    )
  }

  return (
    <form onSubmit={(e) => { void handleRequestCode(e) }} noValidate>
      <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
        Enter your email address and we will send you a verification code.
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
          style={inputStyle}
          placeholder="you@example.com"
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
        {loading ? 'Sending...' : 'Send verification code'}
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
