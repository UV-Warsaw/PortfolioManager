import { useEffect, useState } from 'react'
import {
  getDashboardSummary,
  getDividendYearlySummary,
  type PortfolioSummaryResponse,
  type DividendSummaryResponse,
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
        {holdings && holdings.length > 0 ? (
          holdings.slice(0, 10).map((holding, idx) => (
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
          ))
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
  const [selectedYear, setSelectedYear] = useState<number | null>(yearly[yearly.length - 1]?.year || null)
  const [monthlyData, setMonthlyData] = useState<DividendTimelineResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [hoveredBar, setHoveredBar] = useState<{ month: number; total: number } | null>(null)

  useEffect(() => {
    if (selectedYear) {
      setLoading(true)
      getDividendTimeline(token, selectedYear).then((data) => setMonthlyData(data)).catch((err) => console.error('Failed to load monthly data:', err)).finally(() => setLoading(false))
    }
  }, [selectedYear, token])

  if (!monthlyData || monthlyData.length === 0) {
    return (
      <div style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '16px 20px' }}>
        <h3 style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginBottom: '12px' }}>Monthly Dividends {selectedYear}</h3>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
          {yearly.map((d) => (
            <button key={d.year} onClick={() => setSelectedYear(d.year)} style={{ padding: '6px 12px', border: selectedYear === d.year ? '1px solid #3b82f6' : '1px solid var(--glass-border)', background: selectedYear === d.year ? 'rgba(59, 130, 246, 0.1)' : 'transparent', borderRadius: '6px', color: selectedYear === d.year ? '#3b82f6' : 'var(--text-primary)', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>{d.year}</button>
          ))}
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)' }}>{loading ? 'Loading...' : 'No data for this year'}</p>
      </div>
    )
  }

  const maxValue = Math.max(...monthlyData.map((d) => d.total), 100)
  const padding = 40
  const viewBoxWidth = 1000
  const viewBoxHeight = 300
  const barWidth = (viewBoxWidth - 2 * padding) / Math.max(monthlyData.length, 12)
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  return (
    <div style={{ background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', borderRadius: '10px', padding: '16px 20px' }}>
      <h3 style={{ fontSize: '13px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-tertiary)', marginBottom: '12px' }}>Monthly Dividends {selectedYear}</h3>
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {yearly.map((d) => (
          <button key={d.year} onClick={() => setSelectedYear(d.year)} style={{ padding: '6px 12px', border: selectedYear === d.year ? '1px solid #3b82f6' : '1px solid var(--glass-border)', background: selectedYear === d.year ? 'rgba(59, 130, 246, 0.1)' : 'transparent', borderRadius: '6px', color: selectedYear === d.year ? '#3b82f6' : 'var(--text-primary)', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}>{d.year}</button>
        ))}
      </div>
      <svg width="100%" height="auto" viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`} style={{ display: 'block', aspectRatio: `${viewBoxWidth}/${viewBoxHeight}` }}>
        {[0, 0.25, 0.5, 0.75, 1].map((p, i) => <line key={`grid-${i}`} x1={padding} y1={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding - p * (viewBoxHeight - 2 * padding)} stroke="var(--glass-border)" strokeWidth="1" />)}
        <line x1={padding} y1={padding} x2={padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
        <line x1={padding} y1={viewBoxHeight - padding} x2={viewBoxWidth - padding} y2={viewBoxHeight - padding} stroke="var(--glass-border)" strokeWidth="1" />
        {monthlyData.map((d, i) => {
          const barHeight = (d.total / maxValue) * (viewBoxHeight - 2 * padding)
          const x = padding + i * barWidth + barWidth * 0.1
          const y = viewBoxHeight - padding - barHeight
          const isHovered = hoveredBar?.month === d.month
          return (
            <g key={`bar-${i}`} style={{ cursor: 'pointer' }} onMouseEnter={() => setHoveredBar(d)} onMouseLeave={() => setHoveredBar(null)}>
              <rect x={x} y={y} width={barWidth * 0.8} height={barHeight} fill="#10b981" opacity={isHovered ? 1 : 0.7} />
              {isHovered && (
                <>
                  <rect x={x + barWidth * 0.4 - 60} y={y - 45} width="120" height="35" fill="rgba(0,0,0,0.8)" rx="4" />
                  <text x={x + barWidth * 0.4} y={y - 28} textAnchor="middle" fontSize="12" fill="white" fontWeight="600">{monthNames[d.month - 1]}</text>
                  <text x={x + barWidth * 0.4} y={y - 12} textAnchor="middle" fontSize="12" fill="white">{d.total.toFixed(2)} PLN</text>
                </>
              )}
            </g>
          )
        })}
        {monthlyData.map((d, i) => <text key={`label-${i}`} x={padding + i * barWidth + barWidth * 0.5} y={viewBoxHeight - padding + 20} textAnchor="middle" fontSize="11" fill="var(--text-tertiary)">{monthNames[d.month - 1]}</text>)}
      </svg>
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
