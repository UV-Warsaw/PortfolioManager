import { useEffect, useState } from 'react'
import { getTopHoldings, type TopHoldingItem } from '../services/portfolioApi'

interface Props {
  token: string
  refreshKey?: number
}

export default function TopHoldingsChart({ token, refreshKey }: Props) {
  const [items, setItems] = useState<TopHoldingItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getTopHoldings(token)
      .then((data) => {
        if (!cancelled) {
          setItems(data.items)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [token, refreshKey])

  if (error) return null

  const maxValue = items.length > 0 ? Math.max(...items.map((i) => i.cost_basis)) : 1

  const formatPln = (value: number) =>
    value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' PLN'

  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '16px',
      }}
    >
      <h3
        style={{
          margin: '0 0 20px 0',
          fontSize: '13px',
          fontWeight: 600,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--text-secondary)',
        }}
      >
        Top 10 pozycji
      </h3>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              style={{
                height: '28px',
                borderRadius: '4px',
                background: 'var(--glass-border)',
                opacity: 0.5,
                animation: 'pulse 1.5s ease-in-out infinite',
                width: `${60 + i * 5}%`,
              }}
            />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p style={{ color: 'var(--text-tertiary)', fontSize: '13px', margin: 0 }}>
          Brak danych
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {items.map((item) => {
            const barPct = (item.cost_basis / maxValue) * 100
            return (
              <div
                key={item.ticker}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '72px 1fr 120px',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <span
                  style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    textAlign: 'right',
                    letterSpacing: '0.05em',
                    fontFamily: 'var(--font-mono, monospace)',
                  }}
                >
                  {item.ticker}
                </span>

                <div
                  style={{
                    position: 'relative',
                    height: '20px',
                    background: 'rgba(255,255,255,0.04)',
                    borderRadius: '4px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      inset: '0 auto 0 0',
                      width: `${barPct}%`,
                      background:
                        'linear-gradient(90deg, rgba(99,102,241,0.55) 0%, rgba(99,102,241,0.85) 100%)',
                      borderRadius: '4px',
                      transition: 'width 0.4s ease',
                    }}
                  />
                </div>

                <span
                  style={{
                    fontSize: '12px',
                    color: 'var(--text-secondary)',
                    textAlign: 'right',
                    fontVariantNumeric: 'tabular-nums',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {formatPln(item.cost_basis)}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
