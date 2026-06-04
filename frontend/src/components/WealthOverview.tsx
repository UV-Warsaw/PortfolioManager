/**
 * WealthOverview — total portfolio value + asset-class doughnut chart.
 * Satisfies PROJ-23: dashboard with total value and asset breakdown.
 */

import React, { useState, useEffect } from 'react'
import { Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { getWealthSummary, type WealthSummary, type AssetClassValue } from '../services/portfolioApi'

ChartJS.register(ArcElement, Tooltip, Legend)

interface Props {
  token: string
}

// colours per asset class (same order as backend: Stocks, Bonds, Cash, Crypto, Real Estate)
const CLASS_COLORS: Record<string, string> = {
  Stocks: '#6366f1',
  Bonds: '#34d399',
  Cash: '#facc15',
  Crypto: '#f97316',
  'Real Estate': '#a78bfa',
}

const fmtPLN = (n: number) =>
  new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN', maximumFractionDigits: 0 }).format(n)

const fmtSimple = (n: number) =>
  new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 2 }).format(n)

export const WealthOverview: React.FC<Props> = ({ token }) => {
  const [data, setData] = useState<WealthSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const result = await getWealthSummary(token)
        setData(result)
      } catch {
        setError('Failed to load wealth summary.')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token])

  if (loading) {
    return (
      <div style={{ padding: '24px 0', color: 'var(--text-tertiary)', fontSize: '14px' }}>
        Loading portfolio overview...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.2)', color: '#f87171', fontSize: '13px' }}>
        {error}
      </div>
    )
  }

  // Empty state
  if (!data?.has_data) {
    return (
      <div
        style={{
          padding: '32px 24px',
          borderRadius: '12px',
          border: '1px dashed var(--glass-border)',
          textAlign: 'center',
          background: 'var(--glass-bg)',
          marginBottom: '32px',
        }}
      >
        <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
        <p style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 6px' }}>
          Your portfolio is empty
        </p>
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)', margin: 0 }}>
          Import stock transactions or add bonds, cash accounts, crypto or real estate to see your wealth breakdown.
        </p>
      </div>
    )
  }

  const activeClasses = data.breakdown.filter((c) => c.value > 0)

  const chartData = {
    labels: activeClasses.map((c) => c.name),
    datasets: [
      {
        data: activeClasses.map((c) => c.value),
        backgroundColor: activeClasses.map((c) => CLASS_COLORS[c.name] ?? '#94a3b8'),
        borderColor: 'rgba(15,15,30,0.6)',
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: { label?: string; raw?: unknown; dataset?: { data?: unknown[] } }) => {
            const val = ctx.raw as number
            const pct = data.breakdown.find((c) => c.name === ctx.label)?.percentage ?? 0
            return ` ${fmtSimple(val)} PLN (${pct}%)`
          },
        },
      },
    },
  }

  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '16px',
        padding: '28px',
        marginBottom: '32px',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', margin: '0 0 6px' }}>
          Total Portfolio Value
        </h2>
        <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          {fmtPLN(data.total_value)}
        </div>
      </div>

      {/* Chart + legend */}
      <div style={{ display: 'flex', gap: '32px', alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Doughnut */}
        <div style={{ position: 'relative', width: '200px', height: '200px', flexShrink: 0 }}>
          <Doughnut data={chartData} options={chartOptions} />
          {/* centre label */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              pointerEvents: 'none',
            }}
          >
            <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              {activeClasses.length} classes
            </span>
          </div>
        </div>

        {/* Legend */}
        <div style={{ flex: 1, minWidth: '200px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[...data.breakdown].sort((a, b) => b.value - a.value).map((cls: AssetClassValue) => (
            <LegendRow key={cls.name} cls={cls} total={data.total_value} />
          ))}
        </div>
      </div>
    </div>
  )
}

const LegendRow: React.FC<{ cls: AssetClassValue; total: number }> = ({ cls }) => {
  const color = CLASS_COLORS[cls.name] ?? '#94a3b8'
  const isEmpty = cls.value === 0

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', opacity: isEmpty ? 0.35 : 1 }}>
      {/* colour swatch */}
      <div style={{ width: '10px', height: '10px', borderRadius: '3px', background: color, flexShrink: 0 }} />

      {/* bar track */}
      <div style={{ flex: 1, height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${cls.percentage}%`,
            background: color,
            borderRadius: '3px',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* label */}
      <div style={{ width: '80px', fontSize: '13px', color: 'var(--text-secondary)', flexShrink: 0 }}>
        {cls.name}
      </div>

      {/* value */}
      <div style={{ width: '100px', fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', textAlign: 'right', flexShrink: 0 }}>
        {isEmpty ? '—' : fmtSimple(cls.value) + ' PLN'}
      </div>

      {/* percentage */}
      <div style={{ width: '44px', fontSize: '12px', color: isEmpty ? 'var(--text-tertiary)' : color, textAlign: 'right', flexShrink: 0 }}>
        {isEmpty ? '0%' : `${cls.percentage}%`}
      </div>
    </div>
  )
}
