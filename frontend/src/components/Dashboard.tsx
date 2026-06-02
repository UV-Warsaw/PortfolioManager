import { useEffect, useState } from 'react'
import {
  getDashboardSummary,
  getDividendYearlySummary,
  getDividendTimeline,
  type PortfolioSummaryResponse,
  type DividendSummaryResponse,
  type DividendTimelineResponse,
} from '../services/portfolioApi'

interface Props {
  token: string
  refreshKey?: number
}

function formatPLN(value: number): string {
  return value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' PLN'
}

function formatPercent(value: number): string {
  return value.toFixed(2) + '%'
}

interface DashboardStat {
  label: string
  value: string
  subtext?: string
  color?: 'positive' | 'negative' | 'neutral'
}

function DashboardCard({ stat }: { stat: DashboardStat }) {
  const bgColor =
    stat.color === 'positive'
      ? 'rgba(34, 197, 94, 0.1)'
      : stat.color === 'negative'
        ? 'rgba(239, 68, 68, 0.1)'
        : 'transparent'

  const textColor =
    stat.color === 'positive'
      ? '#22c55e'
      : stat.color === 'negative'
        ? '#ef4444'
        : 'var(--text-primary)'

  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '10px',
        padding: '16px 20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
      }}
    >
      <span
        style={{
          fontSize: '11px',
          fontWeight: 600,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: 'var(--text-tertiary)',
        }}
      >
        {stat.label}
      </span>
      <span
        style={{
          fontSize: '24px',
          fontWeight: 700,
          color: textColor,
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {stat.value}
      </span>
      {stat.subtext && (
        <span
          style={{
            fontSize: '11px',
            color: 'var(--text-tertiary)',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {stat.subtext}
        </span>
      )}
    </div>
  )
}

function TopHoldingsSection({ holdings }: { holdings: Array<{ ticker: string; value: number }> }) {
  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '10px',
        padding: '16px 20px',
      }}
    >
      <h3
        style={{
          fontSize: '13px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--text-tertiary)',
          marginBottom: '12px',
        }}
      >
        Top Holdings
      </h3>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        {holdings.slice(0, 10).map((holding, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingBottom: '8px',
              borderBottom: idx < holdings.length - 1 ? '1px solid var(--glass-border)' : 'none',
            }}
          >
            <span
              style={{
                fontSize: '13px',
                fontWeight: 500,
                color: 'var(--text-primary)',
              }}
            >
              {holding.ticker}
            </span>
            <span
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--accent-color)',
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {formatPLN(holding.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function DividendSection({ yearly, timeline }: { yearly: DividendSummaryResponse[]; timeline: DividendTimelineResponse[] }) {
  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '10px',
        padding: '16px 20px',
      }}
    >
      <h3
        style={{
          fontSize: '13px',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--text-tertiary)',
          marginBottom: '12px',
        }}
      >
        Dividends
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div>
          <p
            style={{
              fontSize: '11px',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '8px',
            }}
          >
            Yearly
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {yearly.slice(-5).map((item, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span>{item.year}</span>
                <span style={{ fontVariantNumeric: 'tabular-nums' }}>{formatPLN(item.total)}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p
            style={{
              fontSize: '11px',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '8px',
            }}
          >
            Recent Months
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {timeline.slice(-5).map((item, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span>{item.month}</span>
                <span style={{ fontVariantNumeric: 'tabular-nums' }}>{formatPLN(item.total)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard({ token, refreshKey = 0 }: Props) {
  const [summary, setSummary] = useState<PortfolioSummaryResponse | null>(null)
  const [dividendYearly, setDividendYearly] = useState<DividendSummaryResponse[]>([])
  const [dividendTimeline, setDividendTimeline] = useState<DividendTimelineResponse[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    Promise.all([
      getDashboardSummary(token),
      getDividendYearlySummary(token),
      getDividendTimeline(token),
    ])
      .then(([sum, yearly, timeline]) => {
        if (!cancelled) {
          setSummary(sum)
          setDividendYearly(yearly)
          setDividendTimeline(timeline)
          setLoading(false)
        }
      })
      .catch((err) => {
        console.error('Failed to load dashboard data:', err)
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [token, refreshKey])

  if (loading || !summary) {
    return (
      <div style={{ padding: '20px' }}>
        <p style={{ color: 'var(--text-tertiary)' }}>Loading dashboard...</p>
      </div>
    )
  }

  const stats: DashboardStat[] = [
    {
      label: 'Portfolio Value',
      value: formatPLN(summary.portfolio_value),
    },
    {
      label: 'Total Invested',
      value: formatPLN(summary.total_invested),
    },
    {
      label: 'Profit / Loss',
      value: formatPLN(summary.profit),
      color: summary.profit >= 0 ? 'positive' : 'negative',
      subtext: `(${formatPercent(summary.profit_percentage)})`,
    },
  ]

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {stats.map((stat, idx) => (
          <DashboardCard key={idx} stat={stat} />
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <TopHoldingsSection holdings={summary.top_holdings} />
        <DividendSection yearly={dividendYearly} timeline={dividendTimeline} />
      </div>
    </div>
  )
}
