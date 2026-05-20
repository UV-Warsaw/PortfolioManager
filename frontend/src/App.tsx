import React, { useEffect, useState } from 'react'
import ForgotPasswordForm from './components/ForgotPasswordForm'
import LoginForm from './components/LoginForm'
import ProfileForm from './components/ProfileForm'
import RegisterForm from './components/RegisterForm'
import { getMe, logoutUser } from './services/authApi'

type ApiStatus = 'checking' | 'online' | 'offline'
type Screen = 'login' | 'register' | 'dashboard' | 'forgot-password' | 'profile'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const App: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')
  const [screen, setScreen] = useState<Screen>('login')
  const [currentEmail, setCurrentEmail] = useState('')
  const [loggingOut, setLoggingOut] = useState(false)

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(4000) })
        setApiStatus(res.ok ? 'online' : 'offline')
      } catch {
        setApiStatus('offline')
      }
    }
    void check()
  }, [])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token === null) return

    const restore = async () => {
      try {
        const me = await getMe(token)
        setCurrentEmail(me.email)
        setScreen('dashboard')
      } catch {
        localStorage.removeItem('access_token')
      }
    }
    void restore()
  }, [])

  const handleAuthSuccess = (email: string) => {
    setCurrentEmail(email)
    setScreen('dashboard')
  }

  const handleLogout = async () => {
    setLoggingOut(true)
    const token = localStorage.getItem('access_token')
    if (token !== null) {
      await logoutUser(token).catch(() => {})
    }
    localStorage.removeItem('access_token')
    setCurrentEmail('')
    setScreen('login')
    setLoggingOut(false)
  }

  const statusColor: Record<ApiStatus, string> = {
    checking: 'text-yellow-400',
    online: 'text-emerald-400',
    offline: 'text-red-400',
  }

  const statusLabel: Record<ApiStatus, string> = {
    checking: 'Checking...',
    online: 'Online',
    offline: 'Offline',
  }

  const screenTitle: Record<Screen, string> = {
    login: 'Sign in',
    register: 'Create your account',
    dashboard: 'Dashboard',
    'forgot-password': 'Reset your password',
    profile: 'Edit profile',
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center px-4"
      style={{ background: 'var(--bg)' }}
    >
      <div
        className="w-full max-w-md rounded-2xl border p-8"
        style={{
          background: 'var(--card)',
          borderColor: 'rgba(99,102,241,0.2)',
          boxShadow: '0 0 40px rgba(99,102,241,0.08)',
        }}
      >
        <div className="mb-8 text-center">
          <div
            className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4"
            style={{
              background: 'var(--accent-glow)',
              border: '1px solid rgba(99,102,241,0.3)',
            }}
          >
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#6366f1"
              strokeWidth="1.8"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <h1
            className="text-2xl font-semibold tracking-tight"
            style={{ color: 'var(--text)' }}
          >
            Portfolio Manager
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--muted)' }}>
            {screenTitle[screen]}
          </p>
        </div>

        {screen === 'login' && (
          <LoginForm
            onSuccess={(email) => handleAuthSuccess(email)}
            onSwitchToRegister={() => setScreen('register')}
            onForgotPassword={() => setScreen('forgot-password')}
          />
        )}

        {screen === 'forgot-password' && (
          <ForgotPasswordForm
            onSwitchToLogin={() => setScreen('login')}
          />
        )}

        {screen === 'register' && (
          <RegisterForm
            onSuccess={(email) => handleAuthSuccess(email)}
            onSwitchToLogin={() => setScreen('login')}
          />
        )}

        {screen === 'dashboard' && (
          <div>
            <div
              className="rounded-xl p-4 mb-6 flex items-center gap-3"
              style={{
                background: 'rgba(99,102,241,0.08)',
                border: '1px solid rgba(99,102,241,0.2)',
              }}
            >
              <div
                className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold"
                style={{ background: 'var(--accent)', color: '#fff' }}
              >
                {currentEmail.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-xs" style={{ color: 'var(--muted)' }}>Signed in as</p>
                <p
                  className="text-sm font-medium truncate"
                  style={{ color: 'var(--text)' }}
                >
                  {currentEmail}
                </p>
              </div>
            </div>

            <div
              className="rounded-xl p-6 mb-6 text-center"
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <p className="text-sm" style={{ color: 'var(--muted)' }}>
                Portfolio dashboard coming soon.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setScreen('profile')}
                className="flex-1 rounded-lg py-2 text-sm font-semibold transition-opacity
                  focus-visible:outline focus-visible:outline-2
                  focus-visible:outline-indigo-500"
                style={{
                  background: 'rgba(99,102,241,0.12)',
                  color: '#a5b4fc',
                  border: '1px solid rgba(99,102,241,0.25)',
                }}
              >
                Edit profile
              </button>
              <button
                type="button"
                onClick={() => { void handleLogout() }}
                disabled={loggingOut}
                className="flex-1 rounded-lg py-2 text-sm font-semibold transition-opacity
                  disabled:opacity-50 focus-visible:outline focus-visible:outline-2
                  focus-visible:outline-red-500"
                style={{
                  background: 'rgba(239,68,68,0.12)',
                  color: '#f87171',
                  border: '1px solid rgba(239,68,68,0.25)',
                }}
              >
                {loggingOut ? 'Signing out...' : 'Sign out'}
              </button>
            </div>
          </div>
        )}

        {screen === 'profile' && (
          <ProfileForm
            onBack={() => setScreen('dashboard')}
            onEmailChanged={(email) => setCurrentEmail(email)}
          />
        )}

        <div
          className="mt-6 rounded-xl p-3 flex items-center justify-between"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <p className="text-xs" style={{ color: 'var(--muted)' }}>
            API
          </p>
          <span className={`text-xs font-semibold ${statusColor[apiStatus]}`}>
            {statusLabel[apiStatus]}
          </span>
        </div>
      </div>
    </div>
  )
}

export default App
