/**
 * EmergencyFundCard — PROJ-28
 * Shows emergency fund adequacy: cash + bonds vs monthly expenses.
 * Status levels: critical (<3 months), good (3–6 months), excellent (>6 months).
 */

import React, { useEffect, useState } from 'react'
import { getEmergencyFund, type EmergencyFundResponse } from '../services/portfolioApi'

interface Props {
  token: string
  refreshKey?: number
}

const STATUS_COLOR: Record<string, string> = {
  critical: '#f87171',
  good: '#facc15',
  excellent: '#34d399',
}

const STATUS_BG: Record<string, string> = {
  critical: 'rgba(248,113,113,0.08)',
  good: 'rgba(250,204,21,0.08)',
  excellent: 'rgba(52,211,153,0.08)',
}

const STATUS_BORDER: Record<string, string> = {
  critical: 'rgba(248,113,113,0.25)',
  good: 'rgba(250,204,21,0.25)',
  excellent: 'rgba(52,211,153,0.25)',
}

const STATUS_LABEL: Record<string, string> = {
  critical: 'Critical',
  good: 'Good',
  excellent: 'Excellent',
}

function formatPLN(value: number): string {
  return value.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' PLN'
}

export const EmergencyFundCard: React.FC<Props> = ({ token, refreshKey }) => {
  const [data, setData] = useState<EmergencyFundResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    const load = async () => {
      try {
        setData(await getEmergencyFund(token))
      } catch {
        setError('Failed to load emergency fund data.')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token, refreshKey])

  if (loading) {
    return (
      <div
        style={{
          padding: '24px',
          borderRadius: '16px',
          background: 'var(--glass-bg)',
          border: '1px solid var(--glass-border)',
          color: 'var(--text-tertiary)',
          fontSize: '13px',
          marginBottom: '24px',
        }}
      >
        Loading emergency fund...
      </div>
    )
  }

  if (error) {
    return (
      <div
        style={{
          padding: '24px',
          borderRadius: '16px',
          background: 'var(--glass-bg)',
          border: '1px solid var(--glass-border)',
          color: '#f87171',
          fontSize: '13px',
          marginBottom: '24px',
        }}
      >
        {error}
      </div>
    )
  }

  if (data === null) return null

  const color = STATUS_COLOR[data.status] ?? '#facc15'
  const bg = STATUS_BG[data.status] ?? 'rgba(250,204,21,0.08)'
  const border = STATUS_BORDER[data.status] ?? 'rgba(250,204,21,0.25)'
  const label = STATUS_LABEL[data.status] ?? data.status

  return (
    <div
      style={{
        borderRadius: '16px',
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        padding: '24px',
        marginBottom: '24px',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h3
          style={{
            margin: 0,
            fontSize: '15px',
            fontWeight: 600,
            color: 'var(--text-primary)',
          }}
        >
          Emergency Fund
        </h3>
        <p style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--text-tertiary)' }}>
          Cash + Bonds coverage in months
        </p>
      </div>

      {!data.has_data ? (
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)', margin: 0 }}>
          No portfolio data yet. Add assets to see emergency fund analysis.
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Status badge + months */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              padding: '14px 16px',
              borderRadius: '10px',
              background: bg,
              border: `1px solid ${border}`,
            }}
          >
            <div>
              <p
                style={{
                  margin: 0,
                  fontSize: '22px',
                  fontWeight: 700,
                  color,
                  lineHeight: 1,
                }}
              >
                {data.monthly_expenses > 0
                  ? `${data.months_covered.toFixed(1)} months coverage`
                  : '—'}
              </p>
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--text-tertiary)' }}>
                {data.monthly_expenses > 0
                  ? `Your monthly expenses: ${formatPLN(data.monthly_expenses)}`
                  : 'Set your monthly expenses in Profile to see coverage'}
              </p>
            </div>
            <span
              style={{
                flexShrink: 0,
                fontSize: '11px',
                fontWeight: 700,
                padding: '4px 10px',
                borderRadius: '6px',
                background: `${color}22`,
                color,
                border: `1px solid ${border}`,
              }}
            >
              {label}
            </span>
          </div>

          {/* Breakdown */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <BreakdownRow label="Cash" value={data.cash_value} />
            <BreakdownRow label="Bonds" value={data.bonds_value} />
            <div
              style={{
                height: '1px',
                background: 'var(--glass-border)',
                margin: '2px 0',
              }}
            />
            <BreakdownRow
              label="Total emergency fund"
              value={data.emergency_fund}
              bold
            />
          </div>

          {/* Action hint for critical */}
          {data.status === 'critical' && data.monthly_expenses > 0 && (
            <div
              style={{
                padding: '12px 14px',
                borderRadius: '10px',
                background: 'rgba(248,113,113,0.06)',
                border: '1px solid rgba(248,113,113,0.2)',
              }}
            >
              <p style={{ margin: 0, fontSize: '12px', color: '#f87171' }}>
                ⚠ Your emergency fund covers less than 3 months of expenses. Consider increasing your cash or bonds holdings.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface RowProps {
  label: string
  value: number
  bold?: boolean
}

const BreakdownRow: React.FC<RowProps> = ({ label, value, bold }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '8px',
    }}
  >
    <span
      style={{
        fontSize: '13px',
        color: bold ? 'var(--text-primary)' : 'var(--text-secondary)',
        fontWeight: bold ? 600 : 400,
      }}
    >
      {label}
    </span>
    <span
      style={{
        fontSize: '13px',
        color: bold ? 'var(--text-primary)' : 'var(--text-secondary)',
        fontWeight: bold ? 600 : 400,
      }}
    >
      {formatPLN(value)}
    </span>
  </div>
)
