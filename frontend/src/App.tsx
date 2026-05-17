import React, { useEffect, useState } from 'react'
import RegisterForm from './components/RegisterForm'

type ApiStatus = 'checking' | 'online' | 'offline'
type Screen = 'register' | 'registered'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const App: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')
  const [screen, setScreen] = useState<Screen>('register')
  const [registeredEmail, setRegisteredEmail] = useState('')

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
            {screen === 'register' ? 'Create your account' : 'Account created'}
          </p>
        </div>

        {screen === 'register' ? (
          <RegisterForm
            onSuccess={(email) => {
              setRegisteredEmail(email)
              setScreen('registered')
            }}
          />
        ) : (
          <div className="text-center">
            <div
              className="inline-flex items-center justify-center w-12 h-12 rounded-full mb-4"
              style={{ background: 'rgba(52,211,153,0.12)', border: '1px solid rgba(52,211,153,0.3)' }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <p className="font-semibold" style={{ color: 'var(--text)' }}>
              Welcome aboard
            </p>
            <p className="mt-1 text-sm" style={{ color: 'var(--muted)' }}>
              {registeredEmail}
            </p>
          </div>
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
