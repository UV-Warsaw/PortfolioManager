/**
 * DiversificationCard — PROJ-28
 * Shows concentration alerts and diversification recommendations.
 * A recommendation is raised when one asset class exceeds 70% of the portfolio.
 */

import React, { useEffect, useState } from 'react'
import {
  getDiversificationRecommendations,
  type DiversificationRecommendation,
  type DiversificationResponse,
} from '../services/portfolioApi'

interface Props {
  token: string
  onNavigate?: (tab: string) => void
}

export const DiversificationCard: React.FC<Props> = ({ token, onNavigate }) => {
  const [data, setData] = useState<DiversificationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        setData(await getDiversificationRecommendations(token))
      } catch {
        setError('Failed to load diversification recommendations.')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [token])

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
        Loading recommendations...
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
          Diversification
        </h3>
        <p
          style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--text-tertiary)' }}
        >
          Concentration alerts — threshold: 70% per asset class
        </p>
      </div>

      {!data.has_data ? (
        <p style={{ fontSize: '13px', color: 'var(--text-tertiary)', margin: 0 }}>
          No portfolio data yet. Add assets to see diversification analysis.
        </p>
      ) : data.is_diversified ? (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '14px 16px',
            borderRadius: '10px',
            background: 'rgba(52,211,153,0.08)',
            border: '1px solid rgba(52,211,153,0.25)',
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 20 20"
            fill="#34d399"
            style={{ flexShrink: 0 }}
          >
            <path
              fillRule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          <span style={{ fontSize: '13px', color: '#34d399', fontWeight: 500 }}>
            Your portfolio is diversified according to your profile.
          </span>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {data.recommendations.map((rec) => (
            <RecommendationItem
              key={rec.asset_class}
              rec={rec}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface RecProps {
  rec: DiversificationRecommendation
  onNavigate?: (tab: string) => void
}

const RecommendationItem: React.FC<RecProps> = ({ rec, onNavigate }) => (
  <div
    style={{
      padding: '16px',
      borderRadius: '10px',
      background: 'rgba(249,115,22,0.06)',
      border: '1px solid rgba(249,115,22,0.25)',
    }}
  >
    {/* Problem */}
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '8px',
        marginBottom: '8px',
      }}
    >
      <p style={{ margin: 0, fontSize: '13px', fontWeight: 600, color: '#f97316' }}>
        ⚠ {rec.problem}
      </p>
      <span
        style={{
          flexShrink: 0,
          fontSize: '11px',
          fontWeight: 700,
          padding: '2px 8px',
          borderRadius: '6px',
          background: 'rgba(249,115,22,0.15)',
          color: '#f97316',
        }}
      >
        {rec.percentage.toFixed(0)}%
      </span>
    </div>

    {/* Action */}
    <p
      style={{ margin: '0 0 12px', fontSize: '12px', color: 'var(--text-secondary)' }}
    >
      {rec.action}
    </p>

    {/* Navigate button */}
    {onNavigate !== undefined && (
      <button
        type="button"
        onClick={() => onNavigate(rec.link_to)}
        style={{
          fontSize: '11px',
          fontWeight: 600,
          padding: '5px 12px',
          borderRadius: '6px',
          background: 'rgba(99,102,241,0.12)',
          border: '1px solid rgba(99,102,241,0.3)',
          color: '#6366f1',
          cursor: 'pointer',
        }}
      >
        Go to {rec.asset_class} →
      </button>
    )}
  </div>
)
