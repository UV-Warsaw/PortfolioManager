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
  const top = holdings ? holdings.slice(0, 10) : []
  const maxValue = top.length > 0 ? Math.max(...top.map((h) => h.value)) : 1

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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {top.length > 0 ? (
          top.map((holding, idx) => {
            const pct = (holding.value / maxValue) * 100
            return (
              <div
                key={idx}
                style={{
                  position: 'relative',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  overflow: 'hidden',
                }}
              >
                {/* background bar */}
                <div
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: `${pct}%`,
                    background: 'rgba(99,102,241,0.12)',
                    borderRight: '2px solid rgba(99,102,241,0.35)',
                    borderRadius: '6px 0 0 6px',
                    transition: 'width 0.4s ease',
                  }}
                />
                <span
                  style={{
                    position: 'relative',
                    fontSize: '13px',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    zIndex: 1,
                  }}
                >
                  {holding.ticker}
                </span>
                <span
                  style={{
                    position: 'relative',
                    fontSize: '13px',
                    fontWeight: 600,
                    color: 'rgba(99,102,241,0.9)',
                    fontVariantNumeric: 'tabular-nums',
                    zIndex: 1,
                  }}
                >
                  {formatPLN(holding.value)}
                </span>
              </div>
            )
          })
        ) : (
          <p style={{ fontSize: '13px', color: 'var(--text-tertiary)' }}>No holdings</p>
        )}
      </div>
    </div>
  )
}

function DividendLineChart({ yearly }: { yearly: DividendSummaryResponse[] }) {
  const [hoveredPoint, setHoveredPoint] = useState<{ year: number; total: number } | null>(null)

  if (!yearly || yearly.length === 0) {
    return (
      <div style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '16px 20px' }}>
        <h3 style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginBottom: '12px' }}>Yearly Dividends</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)' }}>No dividend data</p>
      </div>
    )
  }

  const maxValue = Math.max(...yearly.map((d) => d.total), 100)
  const padding = 40
  const viewBoxWidth = 1000
  const viewBoxHeight = 300

  const points = yearly.map((d, i) => {
    const x = padding + (i / (yearly.length - 1 || 1)) * (viewBoxWidth - 2 * padding)
    const y = viewBoxHeight - padding - (d.total / maxValue) * (viewBoxHeight - 2 * padding)
    return { x, y, year: d.year, total: d.total }
  })

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')

  return (
    <div style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '16px 20px' }}>
      <h3 style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginBottom: '12px' }}>Yearly Dividends</h3>
      <svg width="100%" height="auto" viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`} style={{ display: 'block', aspectRatio: `${viewBoxWidth}/${viewBoxHeight}` }}>
        {[0, 0.25, 0.5, 0.75, 1].map((p, i) => <line key={`grid-${i}`} x1={padding} y1={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} stroke="var(--glass-border)" strokeWidth="1" />)}
        <line x1={padding} y1={padding} x2={padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
        <line x1={padding} y1={viewBoxHeight - padding} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
        <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="2" />
        {points.map((p, i) => (
          <g key={`point-${i}`} style={{ cursor: 'pointer' }} onMouseEnter={() => setHoveredPoint(p)} onMouseLeave={() => setHoveredPoint(null)}>
            <circle cx={p.x} cy={p.y} r="6" fill="#3b82f6" opacity={hoveredPoint?.year === p.year ? 1 : 0.5} />
            {hoveredPoint?.year === p.year && (
              <>
                <rect x={p.x - 60} y={p.y - 50} width="120" height="40" fill="rgba(0,0,0,0.9)" rx="4" />
                <text x={p.x} y={p.y - 28} textAnchor="middle" fontSize="13" fill="white" fontWeight="600">{p.year}</text>
                <text x={p.x} y={p.y - 10} textAnchor="middle" fontSize="12" fill="white">{p.total.toFixed(2)} PLN</text>
              </>
            )}
          </g>
        ))}
        {points.map((p, i) => <text key={`label-${i}`} x={p.x} y={viewBoxHeight - padding + 25} textAnchor="middle" fontSize="12" fill="var(--text-tertiary)">{p.year}</text>)}
      </svg>
    </div>
  )
}

function DividendBarChart({ yearly, token }: { yearly: DividendSummaryResponse[]; token: string }) {
  const [selectedYear, setSelectedYear] = useState<number | null>(yearly[yearly.length - 1]?.year ?? new Date().getFullYear())
  const [monthlyData, setMonthlyData] = useState<DividendTimelineResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [hoveredBar, setHoveredBar] = useState<number | null>(null)

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  // Build a full 12-month array, filling missing months with 0
  const fullYear: DividendTimelineResponse[] = Array.from({ length: 12 }, (_, i) => {
    const found = monthlyData.find((d) => d.month === i + 1)
    return { month: i + 1, total: found?.total ?? 0 }
  })

  useEffect(() => {
    if (selectedYear) {
      setLoading(true)
      getDividendTimeline(token, selectedYear)
        .then((data: DividendTimelineResponse[]) => setMonthlyData(data))
        .catch((err: Error) => console.error('Failed to load monthly data:', err))
        .finally(() => setLoading(false))
    }
  }, [selectedYear, token])

  const maxValue = Math.max(...fullYear.map((d) => d.total), 1)
  const padding = 40
  const viewBoxWidth = 1000
  const viewBoxHeight = 300
  const barWidth = (viewBoxWidth - 2 * padding) / 12

  return (
    <div style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '16px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
        <h3 style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', margin: 0 }}>Monthly Dividends</h3>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {yearly.map((d) => (
            <button key={d.year} onClick={() => setSelectedYear(d.year)} style={{ padding: '4px 10px', border: selectedYear === d.year ? '1px solid #3b82f6' : '1px solid var(--glass-border)', background: selectedYear === d.year ? 'rgba(59,130,246,0.1)' : 'transparent', borderRadius: '6px', color: selectedYear === d.year ? '#3b82f6' : 'var(--text-primary)', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>{d.year}</button>
          ))}
          {/* always show current year selector even if no dividend data exists for it */}
          {!yearly.find((d) => d.year === new Date().getFullYear()) && (
            <button onClick={() => setSelectedYear(new Date().getFullYear())} style={{ padding: '4px 10px', border: selectedYear === new Date().getFullYear() ? '1px solid #3b82f6' : '1px solid var(--glass-border)', background: selectedYear === new Date().getFullYear() ? 'rgba(59,130,246,0.1)' : 'transparent', borderRadius: '6px', color: selectedYear === new Date().getFullYear() ? '#3b82f6' : 'var(--text-primary)', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>{new Date().getFullYear()}</button>
          )}
        </div>
      </div>
      {loading ? (
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)' }}>Loading...</p>
      ) : (
        <svg width="100%" height="auto" viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`} style={{ display: 'block', aspectRatio: `${viewBoxWidth}/${viewBoxHeight}` }}>
          {[0, 0.25, 0.5, 0.75, 1].map((p, i) => <line key={`grid-${i}`} x1={padding} y1={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} stroke="var(--glass-border)" strokeWidth="1" />)}
          <line x1={padding} y1={padding} x2={padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
          <line x1={padding} y1={viewBoxHeight - padding} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
          {fullYear.map((d, i) => {
            const barHeight = maxValue > 0 ? (d.total / maxValue) * (viewBoxHeight - 2 * padding) : 0
            const x = padding + i * barWidth + barWidth * 0.1
            const y = viewBoxHeight - padding - barHeight
            const isHovered = hoveredBar === d.month
            const hasData = d.total > 0
            return (
              <g key={`bar-${i}`} style={{ cursor: hasData ? 'pointer' : 'default' }} onMouseEnter={() => hasData && setHoveredBar(d.month)} onMouseLeave={() => setHoveredBar(null)}>
                {/* empty slot outline */}
                {!hasData && <rect x={x} y={padding} width={barWidth * 0.8} height={viewBoxHeight - 2 * padding} fill="rgba(255,255,255,0.02)" stroke="var(--glass-border)" strokeWidth="0.5" strokeDasharray="4 4" />}
                {hasData && <rect x={x} y={y} width={barWidth * 0.8} height={barHeight} fill="#10b981" opacity={isHovered ? 1 : 0.75} rx="2" />}
                {isHovered && hasData && (
                  <>
                    <rect x={Math.min(x + barWidth * 0.4 - 55, viewBoxWidth - 120)} y={Math.max(y - 48, 4)} width="110" height="36" fill="rgba(0,0,0,0.85)" rx="4" />
                    <text x={Math.min(x + barWidth * 0.4, viewBoxWidth - 65)} y={Math.max(y - 30, 22)} textAnchor="middle" fontSize="12" fill="white" fontWeight="600">{monthNames[i]}</text>
                    <text x={Math.min(x + barWidth * 0.4, viewBoxWidth - 65)} y={Math.max(y - 14, 38)} textAnchor="middle" fontSize="12" fill="white">{d.total.toFixed(2)} PLN</text>
                  </>
                )}
              </g>
            )
          })}
          {fullYear.map((d, i) => <text key={`label-${i}`} x={padding + i * barWidth + barWidth * 0.5} y={viewBoxHeight - padding + 20} textAnchor="middle" fontSize="11" fill="var(--text-tertiary)">{monthNames[i]}</text>)}
        </svg>
      )}
    </div>
  )
}

export default function Dashboard({ token, refreshKey = 0 }: Props) {
  const [summary, setSummary] = useState<PortfolioSummaryResponse | null>(null)
  const [dividendYearly, setDividendYearly] = useState<DividendSummaryResponse[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    Promise.all([
      getDashboardSummary(token),
      getDividendYearlySummary(token),
    ])
      .then(([sum, yearly]) => {
        if (!cancelled) {
          setSummary(sum)
          setDividendYearly(yearly)
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
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {stats.map((stat, idx) => (
          <DashboardCard key={idx} stat={stat} />
        ))}
      </div>

      {/* Holdings and Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px', marginBottom: '20px' }}>
        <TopHoldingsSection holdings={summary.top_holdings} />
        <DividendLineChart yearly={dividendYearly} />
      </div>

      {/* Monthly Dividend Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
        <DividendBarChart yearly={dividendYearly} token={token} />
      </div>
    </div>
  )
}
