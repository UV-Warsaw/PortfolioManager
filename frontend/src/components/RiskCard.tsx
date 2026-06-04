/**
 * RiskCard — PROJ-27
 * Shows computed portfolio risk level vs the user's declared preference.
 * Risk rules:
 *   Crypto                → high   → aggressive
 *   Stocks + Real Estate  → medium → moderate
 *   Bonds + Cash          → low    → conservative
 */

import React, { useEffect, useState } from 'react'
import { getRiskAssessment, type RiskAssessment } from '../services/portfolioApi'

interface Props {
  token: string
}

const RISK_COLORS: Record<string, string> = {
  conservative: '#34d399',  // green
  moderate: '#facc15',      // yellow
  aggressive: '#f97316',    // orange
}

const RISK_LABELS: Record<string, string> = {
  conservative: 'Conservative',
  moderate: 'Moderate',
  aggressive: 'Aggressive',
}

const BAR_SEGMENTS = [
  { key: 'low_pct',    label: 'Low risk',    color: '#34d399' },
  { key: 'medium_pct', label: 'Medium risk', color: '#facc15' },
  { key: 'high_pct',   label: 'High risk',   color: '#f97316' },
] as const

export const RiskCard: React.FC<Props> = ({ token }) => {
  const [data, setData] = useState<RiskAssessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setData(await getRiskAssessment(token))
      } catch {
        setError('Failed to load risk assessment.')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token])

  if (loading) {
    return (
      <div style={{ padding: '24px', borderRadius: '16px', background: 'var(--glass-bg)', border: '1px solid var(--glass-border)', color: 'var(--text-tertiary)', fontSize: '13px', marginBottom: '24px' }}>
        Loading risk assessment...
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.2)', color: '#f87171', fontSize: '13px', marginBottom: '24px' }}>
        {error}
      </div>
    )
  }

  if (!data) return null

  const portfolioColor = RISK_COLORS[data.portfolio_risk] ?? '#94a3b8'
  const preferenceColor = RISK_COLORS[data.user_preference] ?? '#94a3b8'

  return (
    <div
      style={{
        background: 'var(--glass-bg)',
        border: `1px solid ${data.has_data ? (data.is_aligned ? 'rgba(52,211,153,0.25)' : 'rgba(249,115,22,0.25)') : 'var(--glass-border)'}`,
        borderRadius: '16px',
        padding: '24px 28px',
        marginBottom: '24px',
      }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', margin: '0 0 4px' }}>
            Risk Assessment
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '22px', fontWeight: 800, color: portfolioColor, letterSpacing: '-0.01em' }}>
              {RISK_LABELS[data.portfolio_risk] ?? data.portfolio_risk}
            </span>
            <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>portfolio profile</span>
          </div>
        </div>

        {/* Alignment badge */}
        {data.has_data && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              background: data.is_aligned ? 'rgba(52,211,153,0.1)' : 'rgba(249,115,22,0.1)',
              color: data.is_aligned ? '#34d399' : '#f97316',
              border: `1px solid ${data.is_aligned ? 'rgba(52,211,153,0.25)' : 'rgba(249,115,22,0.25)'}`,
            }}
          >
            <span>{data.is_aligned ? '✓' : '!'}</span>
            {data.is_aligned ? 'Aligned with your preference' : 'Mismatch with your preference'}
          </div>
        )}
      </div>

      {/* Risk breakdown bar */}
      {data.has_data && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', height: '8px', borderRadius: '4px', overflow: 'hidden', gap: '2px' }}>
            {BAR_SEGMENTS.map(({ key, color }) => {
              const pct = data[key]
              return pct > 0 ? (
                <div key={key} style={{ width: `${pct}%`, background: color, borderRadius: '4px', transition: 'width 0.4s ease' }} />
              ) : null
            })}
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '8px', flexWrap: 'wrap' }}>
            {BAR_SEGMENTS.map(({ key, label, color }) => (
              <span key={key} style={{ fontSize: '11px', color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: color, display: 'inline-block' }} />
                {label}: {data[key]}%
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Comparison row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          borderRadius: '10px',
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.06)',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ flex: 1, minWidth: '120px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Portfolio</div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: portfolioColor }}>
            {data.has_data ? (RISK_LABELS[data.portfolio_risk] ?? data.portfolio_risk) : '—'}
          </div>
        </div>

        <div style={{ color: 'var(--text-tertiary)', fontSize: '16px' }}>vs</div>

        <div style={{ flex: 1, minWidth: '120px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Your Preference</div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: preferenceColor }}>
            {RISK_LABELS[data.user_preference] ?? data.user_preference}
          </div>
        </div>
      </div>

      {/* Mismatch message */}
      {data.has_data && !data.is_aligned && (
        <p style={{ margin: '14px 0 0', fontSize: '13px', color: '#f97316', lineHeight: 1.5 }}>
          Your portfolio has a <strong>{RISK_LABELS[data.portfolio_risk]}</strong> risk profile, but your declared preference is <strong>{RISK_LABELS[data.user_preference]}</strong>. Consider rebalancing or updating your preference in Profile settings.
        </p>
      )}

      {data.has_data && data.is_aligned && (
        <p style={{ margin: '14px 0 0', fontSize: '13px', color: '#34d399', lineHeight: 1.5 }}>
          Your portfolio risk matches your declared <strong>{RISK_LABELS[data.user_preference]}</strong> preference.
        </p>
      )}

      {!data.has_data && (
        <p style={{ margin: '14px 0 0', fontSize: '13px', color: 'var(--text-tertiary)' }}>
          Add assets to see your portfolio risk profile.
        </p>
      )}
    </div>
  )
}
