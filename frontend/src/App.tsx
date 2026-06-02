import React, { useCallback, useEffect, useState } from 'react'
import ForgotPasswordForm from './components/ForgotPasswordForm'
import ImportForm from './components/ImportForm'
import { Bonds } from './components/Bonds'
import PortfolioValueCards from './components/PortfolioValueCards'
import TopHoldingsChart from './components/TopHoldingsChart'
import LoginForm from './components/LoginForm'
import ProfileForm from './components/ProfileForm'
import RegisterForm from './components/RegisterForm'
import { getMe, logoutUser } from './services/authApi'

type ApiStatus = 'checking' | 'online' | 'offline'
type AuthScreen = 'login' | 'register' | 'forgot-password'
type DashTab = 'gielda' | 'bonds'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const App: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')
  const [authScreen, setAuthScreen] = useState<AuthScreen>('login')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [currentEmail, setCurrentEmail] = useState('')
  const [dashTab, setDashTab] = useState<DashTab>('gielda')
  const [loggingOut, setLoggingOut] = useState(false)
  const [portfolioRefreshKey, setPortfolioRefreshKey] = useState(0)

  const handleImportSuccess = useCallback(() => {
    setPortfolioRefreshKey((k) => k + 1)
  }, [])

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
        setIsAuthenticated(true)
      } catch {
        localStorage.removeItem('access_token')
      }
    }
    void restore()
  }, [])

  const handleAuthSuccess = (email: string) => {
    setCurrentEmail(email)
    setIsAuthenticated(true)
    setShowProfile(false)
  }

  const handleLogout = async () => {
    setLoggingOut(true)
    const token = localStorage.getItem('access_token')
    if (token !== null) {
      await logoutUser(token).catch(() => {})
    }
    localStorage.removeItem('access_token')
    setCurrentEmail('')
    setIsAuthenticated(false)
    setShowProfile(false)
    setLoggingOut(false)
  }

  const statusColor: Record<ApiStatus, string> = {
    checking: '#facc15',
    online: '#34d399',
    offline: '#f87171',
  }

  // ── UNAUTHENTICATED: centred auth card ──────────────────────────────────
  if (!isAuthenticated) {
    const authTitle: Record<AuthScreen, string> = {
      login: 'Sign in',
      register: 'Create your account',
      'forgot-password': 'Reset your password',
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
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="1.8">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                <polyline points="16 7 22 7 22 13" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight" style={{ color: 'var(--text)' }}>
              Portfolio Manager
            </h1>
            <p className="mt-1 text-sm" style={{ color: 'var(--muted)' }}>
              {authTitle[authScreen]}
            </p>
          </div>

          {authScreen === 'login' && (
            <LoginForm
              onSuccess={handleAuthSuccess}
              onSwitchToRegister={() => setAuthScreen('register')}
              onForgotPassword={() => setAuthScreen('forgot-password')}
            />
          )}
          {authScreen === 'forgot-password' && (
            <ForgotPasswordForm onSwitchToLogin={() => setAuthScreen('login')} />
          )}
          {authScreen === 'register' && (
            <RegisterForm
              onSuccess={handleAuthSuccess}
              onSwitchToLogin={() => setAuthScreen('login')}
            />
          )}

          <div
            className="mt-6 rounded-xl p-3 flex items-center justify-between"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            <p className="text-xs" style={{ color: 'var(--muted)' }}>API</p>
            <span className="text-xs font-semibold" style={{ color: statusColor[apiStatus] }}>
              {apiStatus === 'checking' ? 'Checking...' : apiStatus === 'online' ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>
    )
  }

  // ── AUTHENTICATED: full-screen app shell ────────────────────────────────
  const token = localStorage.getItem('access_token') ?? ''

  return (
    <div className="app-shell">
      {/* Topbar */}
      <header className="topbar">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="flex items-center justify-center w-8 h-8 rounded-lg"
            style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)' }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <span
            className="text-sm font-semibold tracking-tight"
            style={{ color: 'var(--text-primary)' }}
          >
            Portfolio Manager
          </span>
        </div>

        {/* Nav tabs */}
        <nav className="flex items-center gap-1" aria-label="Main navigation">
          <button
            type="button"
            className={`nav-tab${dashTab === 'gielda' && !showProfile ? ' active' : ''}`}
            onClick={() => { setDashTab('gielda'); setShowProfile(false) }}
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
            </svg>
            Trading
          </button>

          <button
            type="button"
            className={`nav-tab${dashTab === 'bonds' && !showProfile ? ' active' : ''}`}
            onClick={() => { setDashTab('bonds'); setShowProfile(false) }}
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
            </svg>
            Bonds
          </button>

          <button
            type="button"
            className="nav-tab coming-soon"
            disabled
            title="Coming soon"
            aria-disabled="true"
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            Crypto
          </button>
        </nav>

        {/* User section */}
        <div className="flex items-center gap-2">
          <div
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg"
            style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)' }}
          >
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
              style={{ background: 'var(--accent)', color: '#fff' }}
            >
              {currentEmail.charAt(0).toUpperCase()}
            </div>
            <span className="text-xs truncate max-w-[140px]" style={{ color: 'var(--text-secondary)' }}>
              {currentEmail}
            </span>
          </div>

          <button
            type="button"
            className={`btn-cinematic${showProfile ? ' !border-indigo-500/50 !bg-indigo-500/10' : ''}`}
            onClick={() => setShowProfile((v) => !v)}
            aria-label="Edit profile"
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
            <span className="hidden sm:inline">Profile</span>
          </button>

          <button
            type="button"
            className="btn-cinematic"
            onClick={() => { void handleLogout() }}
            disabled={loggingOut}
            aria-label="Sign out"
            style={{ color: '#f87171', borderColor: 'rgba(248,113,113,0.25)' }}
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
            </svg>
            <span className="hidden sm:inline">{loggingOut ? 'Signing out...' : 'Sign out'}</span>
          </button>

          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: statusColor[apiStatus] }}
            title={`API: ${apiStatus}`}
          />
        </div>
      </header>

      {/* Main content */}
      <main className="main-content">
        {showProfile ? (
          <div className="max-w-lg mx-auto">
            <div className="card-cinematic">
              <ProfileForm
                onBack={() => setShowProfile(false)}
                onEmailChanged={(email) => setCurrentEmail(email)}
              />
            </div>
          </div>
        ) : dashTab === 'gielda' ? (
          <div className="max-w-2xl mx-auto">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                Trading
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
                Import transactions from XTB and track active positions
              </p>
            </div>
            <PortfolioValueCards token={token} refreshKey={portfolioRefreshKey} />
            <TopHoldingsChart token={token} refreshKey={portfolioRefreshKey} />
            <ImportForm token={token} onImportSuccess={handleImportSuccess} />
          </div>
        ) : dashTab === 'bonds' ? (
          <div className="max-w-6xl mx-auto">
            <Bonds token={token} />
          </div>
        ) : null}
      </main>
    </div>
  )
}

export default App
