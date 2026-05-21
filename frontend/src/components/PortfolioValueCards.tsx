import { useEffect, useState } from 'react'
import { getPortfolioValue, type PortfolioValueResponse } from '../services/portfolioApi'

interface Props {
  token: string
  refreshKey?: number
}

const ACCOUNT_ORDER = ['PLN', 'IKE', 'USD'] as const

function formatPLN(value: number): string {
  return value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' PLN'
}

function AccountCard({ label, value }: { label: string; value: number }) {
  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '10px',
        padding: '16px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}
    >
      <span
        style={{
          fontSize: '10px',
          fontWeight: 600,
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          color: 'var(--text-tertiary)',
        }}
      >
        {label === 'USD' ? 'USD (~PLN)' : label}
      </span>
      <span
        style={{
          fontSize: '20px',
          fontWeight: 700,
          color: 'var(--text-primary)',
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {formatPLN(value)}
      </span>
    </div>
  )
}

export default function PortfolioValueCards({ token, refreshKey = 0 }: Props) {
  const [data, setData] = useState<PortfolioValueResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getPortfolioValue(token)
      .then((res) => {
        if (!cancelled) {
          setData(res)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [token, refreshKey])

  if (loading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {ACCOUNT_ORDER.map((key) => (
          <div
            key={key}
            style={{
              background: 'var(--glass-bg)',
              border: '1px solid var(--glass-border)',
              borderRadius: '10px',
              padding: '16px 20px',
              height: '72px',
              animation: 'pulse 1.5s ease-in-out infinite',
            }}
          />
        ))}
      </div>
    )
  }

  if (!data || Object.keys(data.accounts).length === 0) return null

  const presentAccounts = ACCOUNT_ORDER.filter((key) => key in data.accounts)

  return (
    <div style={{ marginBottom: '20px' }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${presentAccounts.length}, 1fr)`,
          gap: '12px',
          marginBottom: '12px',
        }}
      >
        {presentAccounts.map((key) => (
          <AccountCard key={key} label={key} value={data.accounts[key]} />
        ))}
      </div>

      <div
        style={{
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: '10px',
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span
          style={{
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: 'rgba(99, 102, 241, 0.8)',
          }}
        >
          Lacznie
        </span>
        <span
          style={{
            fontSize: '22px',
            fontWeight: 700,
            color: 'var(--text-primary)',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {formatPLN(data.total)}
        </span>
      </div>
    </div>
  )
}
