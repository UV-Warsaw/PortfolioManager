import React, { useEffect, useState } from 'react'
import {
  ProfileApiError,
  ProfileResponse,
  getProfile,
  updateEmail,
  updatePassword,
  updateProfileSettings,
} from '../services/profileApi'

interface Props {
  onBack: () => void
  onEmailChanged: (newEmail: string) => void
}

type Section = 'settings' | 'email' | 'password'

const inputStyle: React.CSSProperties = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(255,255,255,0.1)',
  color: 'var(--text)',
}

const inputClass =
  'w-full rounded-lg px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-indigo-500'

const labelClass =
  'block text-xs font-medium uppercase tracking-widest mb-1'

const RISK_LEVELS = ['conservative', 'moderate', 'aggressive'] as const

const ProfileForm: React.FC<Props> = ({ onBack, onEmailChanged }) => {
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [activeSection, setActiveSection] = useState<Section>('settings')

  // Settings section state
  const [riskLevel, setRiskLevel] = useState('')
  const [monthlyExpenses, setMonthlyExpenses] = useState('')
  const [settingsError, setSettingsError] = useState<string | null>(null)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsLoading, setSettingsLoading] = useState(false)

  // Email section state
  const [emailCurrentPw, setEmailCurrentPw] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [emailError, setEmailError] = useState<string | null>(null)
  const [emailSuccess, setEmailSuccess] = useState<string | null>(null)
  const [emailLoading, setEmailLoading] = useState(false)

  // Password section state
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [pwError, setPwError] = useState<string | null>(null)
  const [pwSuccess, setPwSuccess] = useState<string | null>(null)
  const [pwLoading, setPwLoading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token === null) return

    const load = async () => {
      try {
        const data = await getProfile(token)
        setProfile(data)
        setRiskLevel(data.risk_level)
        setMonthlyExpenses(String(data.monthly_expenses))
      } catch {
        setLoadError('Failed to load profile.')
      }
    }

    void load()
  }, [])

  const handleSettings = async (e: React.FormEvent) => {
    e.preventDefault()
    setSettingsError(null)
    setSettingsSuccess(null)
    const token = localStorage.getItem('access_token')
    if (token === null) return
    setSettingsLoading(true)
    try {
      const result = await updateProfileSettings(token, {
        risk_level: riskLevel,
        monthly_expenses: parseFloat(monthlyExpenses),
      })
      setProfile(result.profile)
      setSettingsSuccess('Settings saved.')
    } catch (err) {
      setSettingsError(
        err instanceof ProfileApiError ? err.message : 'Failed to save settings.',
      )
    } finally {
      setSettingsLoading(false)
    }
  }

  const handleEmail = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailError(null)
    setEmailSuccess(null)
    const token = localStorage.getItem('access_token')
    if (token === null) return
    setEmailLoading(true)
    try {
      const updated = await updateEmail(token, {
        current_password: emailCurrentPw,
        new_email: newEmail,
      })
      setProfile(updated)
      onEmailChanged(updated.email)
      setEmailSuccess('Email updated.')
      setEmailCurrentPw('')
      setNewEmail('')
    } catch (err) {
      setEmailError(
        err instanceof ProfileApiError ? err.message : 'Failed to update email.',
      )
    } finally {
      setEmailLoading(false)
    }
  }

  const handlePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setPwError(null)
    setPwSuccess(null)
    const token = localStorage.getItem('access_token')
    if (token === null) return
    if (newPw !== confirmPw) {
      setPwError('New passwords do not match.')
      return
    }
    setPwLoading(true)
    try {
      await updatePassword(token, {
        current_password: currentPw,
        new_password: newPw,
        confirm_password: confirmPw,
      })
      setPwSuccess('Password changed.')
      setCurrentPw('')
      setNewPw('')
      setConfirmPw('')
    } catch (err) {
      setPwError(
        err instanceof ProfileApiError ? err.message : 'Failed to change password.',
      )
    } finally {
      setPwLoading(false)
    }
  }

  const sectionTab = (id: Section, label: string) => (
    <button
      key={id}
      type="button"
      onClick={() => setActiveSection(id)}
      className="flex-1 py-2 text-xs font-semibold uppercase tracking-widest rounded-lg
        transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
      style={
        activeSection === id
          ? { background: 'rgba(99,102,241,0.2)', color: '#a5b4fc' }
          : { background: 'transparent', color: 'var(--muted)' }
      }
    >
      {label}
    </button>
  )

  const feedbackRow = (error: string | null, success: string | null) => {
    if (error !== null) {
      return (
        <p className="text-xs mb-4" style={{ color: '#f87171' }}>
          {error}
        </p>
      )
    }
    if (success !== null) {
      return (
        <p className="text-xs mb-4" style={{ color: '#34d399' }}>
          {success}
        </p>
      )
    }
    return null
  }

  if (loadError !== null) {
    return (
      <div className="text-center py-6">
        <p className="text-sm mb-4" style={{ color: '#f87171' }}>
          {loadError}
        </p>
        <button
          type="button"
          onClick={onBack}
          className="text-xs underline"
          style={{ color: 'var(--muted)' }}
        >
          Back to dashboard
        </button>
      </div>
    )
  }

  return (
    <div>
      {profile !== null && (
        <div
          className="rounded-xl p-4 mb-5 flex items-center gap-3"
          style={{
            background: 'rgba(99,102,241,0.06)',
            border: '1px solid rgba(99,102,241,0.15)',
          }}
        >
          <div
            className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold"
            style={{ background: 'var(--accent)', color: '#fff' }}
          >
            {profile.email.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate" style={{ color: 'var(--text)' }}>
              {profile.email}
            </p>
            <p className="text-xs" style={{ color: 'var(--muted)' }}>
              Risk: {profile.risk_level} &nbsp;|&nbsp; Expenses:{' '}
              {profile.monthly_expenses.toLocaleString('pl-PL')} PLN
            </p>
          </div>
        </div>
      )}

      <div
        className="flex gap-1 rounded-xl p-1 mb-5"
        style={{ background: 'rgba(255,255,255,0.03)' }}
      >
        {sectionTab('settings', 'Settings')}
        {sectionTab('email', 'Email')}
        {sectionTab('password', 'Password')}
      </div>

      {activeSection === 'settings' && (
        <form onSubmit={(e) => { void handleSettings(e) }} noValidate>
          {feedbackRow(settingsError, settingsSuccess)}

          <div className="mb-4">
            <label
              htmlFor="risk-level"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              Risk level
            </label>
            <select
              id="risk-level"
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
              className={inputClass}
              style={inputStyle}
            >
              {RISK_LEVELS.map((r) => (
                <option key={r} value={r} style={{ background: '#1e1e2e' }}>
                  {r.charAt(0).toUpperCase() + r.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-6">
            <label
              htmlFor="monthly-expenses"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              Monthly expenses (PLN)
            </label>
            <input
              id="monthly-expenses"
              type="number"
              min="0"
              step="0.01"
              value={monthlyExpenses}
              onChange={(e) => setMonthlyExpenses(e.target.value)}
              className={inputClass}
              style={inputStyle}
              placeholder="0.00"
            />
          </div>

          <button
            type="submit"
            disabled={settingsLoading}
            className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
              disabled:opacity-50 focus-visible:outline focus-visible:outline-2
              focus-visible:outline-indigo-500"
            style={{
              background: 'var(--accent)',
              color: '#fff',
              border: 'none',
            }}
          >
            {settingsLoading ? 'Saving...' : 'Save settings'}
          </button>
        </form>
      )}

      {activeSection === 'email' && (
        <form onSubmit={(e) => { void handleEmail(e) }} noValidate>
          {feedbackRow(emailError, emailSuccess)}

          <div className="mb-4">
            <label
              htmlFor="email-current-pw"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              Current password
            </label>
            <input
              id="email-current-pw"
              type="password"
              autoComplete="current-password"
              required
              value={emailCurrentPw}
              onChange={(e) => setEmailCurrentPw(e.target.value)}
              className={inputClass}
              style={inputStyle}
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="new-email"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              New email address
            </label>
            <input
              id="new-email"
              type="email"
              autoComplete="email"
              required
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              className={inputClass}
              style={inputStyle}
              placeholder="new@example.com"
            />
          </div>

          <button
            type="submit"
            disabled={emailLoading}
            className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
              disabled:opacity-50 focus-visible:outline focus-visible:outline-2
              focus-visible:outline-indigo-500"
            style={{ background: 'var(--accent)', color: '#fff', border: 'none' }}
          >
            {emailLoading ? 'Updating...' : 'Update email'}
          </button>
        </form>
      )}

      {activeSection === 'password' && (
        <form onSubmit={(e) => { void handlePassword(e) }} noValidate>
          {feedbackRow(pwError, pwSuccess)}

          <div className="mb-4">
            <label
              htmlFor="current-pw"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              Current password
            </label>
            <input
              id="current-pw"
              type="password"
              autoComplete="current-password"
              required
              value={currentPw}
              onChange={(e) => setCurrentPw(e.target.value)}
              className={inputClass}
              style={inputStyle}
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="new-pw"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              New password
            </label>
            <input
              id="new-pw"
              type="password"
              autoComplete="new-password"
              required
              value={newPw}
              onChange={(e) => setNewPw(e.target.value)}
              className={inputClass}
              style={inputStyle}
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="confirm-pw"
              className={labelClass}
              style={{ color: 'var(--muted)' }}
            >
              Confirm new password
            </label>
            <input
              id="confirm-pw"
              type="password"
              autoComplete="new-password"
              required
              value={confirmPw}
              onChange={(e) => setConfirmPw(e.target.value)}
              className={inputClass}
              style={inputStyle}
            />
          </div>

          <button
            type="submit"
            disabled={pwLoading}
            className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
              disabled:opacity-50 focus-visible:outline focus-visible:outline-2
              focus-visible:outline-indigo-500"
            style={{ background: 'var(--accent)', color: '#fff', border: 'none' }}
          >
            {pwLoading ? 'Changing...' : 'Change password'}
          </button>
        </form>
      )}

      <button
        type="button"
        onClick={onBack}
        className="w-full mt-4 rounded-lg py-2 text-xs font-medium transition-opacity
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
        style={{ background: 'transparent', color: 'var(--muted)', border: 'none' }}
      >
        Back to dashboard
      </button>
    </div>
  )
}

export default ProfileForm
