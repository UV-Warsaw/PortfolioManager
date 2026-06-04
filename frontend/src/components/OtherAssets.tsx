/**
 * OtherAssets — two sections: Cryptocurrency (BTC/ETH) and Real Estate.
 */

import React, { useState, useEffect, useCallback } from 'react'
import {
  getOtherAssets,
  getOtherAssetAnalysis,
  createOtherAsset,
  updateOtherAsset,
  deleteOtherAsset,
  getOtherAssetsPortfolioSummary,
  type OtherAsset,
  type OtherAssetAnalysis,
  type OtherAssetCreate,
  type OtherAssetUpdate,
  type OtherAssetsPortfolioSummary,
  type OtherAssetClass,
} from '../services/assetsApi'
import { AssetForm } from './AssetForm'

interface Props {
  token: string
}

// ─── helpers ──────────────────────────────────────────────────────────────────

const fmt = (n: number, currency = 'PLN') =>
  new Intl.NumberFormat('pl-PL', { style: 'currency', currency }).format(n)

const fmtSimple = (n: number) =>
  new Intl.NumberFormat('pl-PL', { maximumFractionDigits: 2 }).format(n)

const profitColor = (n: number | null) => {
  if (n === null) return 'var(--text-secondary)'
  return n >= 0 ? '#34d399' : '#f87171'
}

// ─── sub-components ───────────────────────────────────────────────────────────

const SectionHeader: React.FC<{
  title: string
  subtitle?: string
  onAdd: () => void
  addLabel: string
}> = ({ title, subtitle, onAdd, addLabel }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '16px',
    }}
  >
    <div>
      <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
        {title}
      </h2>
      {subtitle && (
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '2px 0 0' }}>
          {subtitle}
        </p>
      )}
    </div>
    <button
      onClick={onAdd}
      style={{
        padding: '8px 14px',
        borderRadius: '8px',
        border: '1px solid rgba(99,102,241,0.4)',
        background: 'rgba(99,102,241,0.12)',
        color: '#6366f1',
        fontSize: '13px',
        fontWeight: 600,
        cursor: 'pointer',
      }}
    >
      + {addLabel}
    </button>
  </div>
)

const StatCard: React.FC<{
  label: string
  value: string
  valueColor?: string
}> = ({ label, value, valueColor }) => (
  <div
    style={{
      background: 'var(--glass-bg)',
      border: '1px solid var(--glass-border)',
      borderRadius: '10px',
      padding: '14px 18px',
    }}
  >
    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
      {label}
    </div>
    <div style={{ fontSize: '20px', fontWeight: 700, color: valueColor ?? 'var(--text-primary)' }}>
      {value}
    </div>
  </div>
)

// ─── main component ───────────────────────────────────────────────────────────

export const OtherAssets: React.FC<Props> = ({ token }) => {
  const [assets, setAssets] = useState<OtherAsset[]>([])
  const [summary, setSummary] = useState<OtherAssetsPortfolioSummary | null>(null)
  const [analysisMap, setAnalysisMap] = useState<Record<number, OtherAssetAnalysis>>({})
  const [loading, setLoading] = useState(true)
  const [formSection, setFormSection] = useState<OtherAssetClass | null>(null)
  const [editingAsset, setEditingAsset] = useState<OtherAsset | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [all, sum] = await Promise.all([
        getOtherAssets(token),
        getOtherAssetsPortfolioSummary(token),
      ])
      setAssets(all)
      setSummary(sum)

      // Load analysis for all assets
      const analyses = await Promise.all(all.map((a) => getOtherAssetAnalysis(token, a.id)))
      const map: Record<number, OtherAssetAnalysis> = {}
      analyses.forEach((an) => { map[an.asset_id] = an })
      setAnalysisMap(map)
    } catch {
      setError('Failed to load assets.')
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { void reload() }, [reload])

  const handleSubmit = async (data: OtherAssetCreate | OtherAssetUpdate) => {
    setSaving(true)
    try {
      if (editingAsset) {
        await updateOtherAsset(token, editingAsset.id, data as OtherAssetUpdate)
      } else {
        await createOtherAsset(token, data as OtherAssetCreate)
      }
      setFormSection(null)
      setEditingAsset(null)
      await reload()
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : typeof err === 'object' && err !== null && 'response' in err
          ? String((err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Unknown error')
          : 'Unknown error'
      throw new Error(msg)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this asset?')) return
    try {
      await deleteOtherAsset(token, id)
      if (selectedId === id) setSelectedId(null)
      await reload()
    } catch {
      setError('Failed to delete asset.')
    }
  }

  const cryptoAssets = assets.filter((a) => a.asset_class === 'Crypto')
  const realEstateAssets = assets.filter((a) => a.asset_class === 'Real Estate')

  const reByClass = summary?.assets_by_class?.['Real Estate']
  const totalPropertyValue = reByClass?.total_value ?? 0

  // Compute total mortgage across all real estate from assets array
  const totalMortgage = realEstateAssets.reduce(
    (acc, a) => acc + (a.mortgage_remaining ?? 0),
    0,
  )
  const totalNetEquity = totalPropertyValue - totalMortgage

  const totalCryptoValue = cryptoAssets.reduce((acc, a) => acc + a.current_value, 0)

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading assets...
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: '8px',
            background: 'rgba(248,113,113,0.1)',
            border: '1px solid rgba(248,113,113,0.3)',
            color: '#f87171',
            fontSize: '13px',
            marginBottom: '20px',
          }}
        >
          {error}
        </div>
      )}

      {/* ── CRYPTO SECTION ── */}
      <section style={{ marginBottom: '40px' }}>
        <SectionHeader
          title="Cryptocurrency"
          subtitle="Bitcoin and Ethereum holdings"
          onAdd={() => { setEditingAsset(null); setFormSection('Crypto') }}
          addLabel="Add BTC / ETH"
        />

        {formSection === 'Crypto' && (
          <div style={{ marginBottom: '20px' }}>
            <AssetForm
              asset={editingAsset ?? undefined}
              initialAssetClass="Crypto"
              onSubmit={handleSubmit}
              onCancel={() => { setFormSection(null); setEditingAsset(null) }}
              isLoading={saving}
            />
          </div>
        )}

        {/* Crypto summary card */}
        {cryptoAssets.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            <StatCard label="Total Crypto Value" value={fmtSimple(totalCryptoValue) + ' PLN'} />
            {cryptoAssets.map((a) => {
              const an = analysisMap[a.id]
              return (
                <StatCard
                  key={a.id}
                  label={a.name}
                  value={fmt(a.current_value, a.currency)}
                  valueColor={an?.profit != null ? profitColor(an.profit) : undefined}
                />
              )
            })}
          </div>
        )}

        {cryptoAssets.length === 0 && formSection !== 'Crypto' && (
          <div
            style={{
              padding: '24px',
              borderRadius: '10px',
              border: '1px dashed var(--glass-border)',
              textAlign: 'center',
              color: 'var(--text-tertiary)',
              fontSize: '14px',
            }}
          >
            No cryptocurrency assets yet. Add BTC or ETH to track your holdings.
          </div>
        )}

        {/* Crypto asset cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {cryptoAssets.map((a) => {
            const an = analysisMap[a.id]
            const isSelected = selectedId === a.id
            return (
              <div
                key={a.id}
                style={{
                  background: 'var(--glass-bg)',
                  border: `1px solid ${isSelected ? 'rgba(99,102,241,0.5)' : 'var(--glass-border)'}`,
                  borderRadius: '10px',
                  padding: '16px 20px',
                  cursor: 'pointer',
                }}
                onClick={() => setSelectedId(isSelected ? null : a.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {a.name}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginLeft: '8px' }}>
                      {a.currency}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {fmt(a.current_value, a.currency)}
                    </div>
                    {an?.profit != null && (
                      <div style={{ fontSize: '12px', color: profitColor(an.profit) }}>
                        {an.profit >= 0 ? '+' : ''}{fmtSimple(an.profit)}{' '}
                        {an.profit_pct != null && `(${an.profit_pct >= 0 ? '+' : ''}${an.profit_pct.toFixed(1)}%)`}
                      </div>
                    )}
                  </div>
                </div>

                {isSelected && (
                  <div style={{ marginTop: '14px', borderTop: '1px solid var(--glass-border)', paddingTop: '14px' }}>
                    {a.quantity != null && (
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                        Quantity: <strong style={{ color: 'var(--text-primary)' }}>{a.quantity}</strong>
                      </div>
                    )}
                    {an?.total_cost != null && (
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                        Total Cost: <strong style={{ color: 'var(--text-primary)' }}>{fmtSimple(an.total_cost)}</strong>
                      </div>
                    )}
                    {a.notes && (
                      <div style={{ fontSize: '13px', color: 'var(--text-tertiary)', marginBottom: '6px' }}>
                        {a.notes}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditingAsset(a); setFormSection('Crypto') }}
                        style={{
                          padding: '5px 12px',
                          borderRadius: '6px',
                          border: '1px solid var(--glass-border)',
                          background: 'transparent',
                          color: 'var(--text-secondary)',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); void handleDelete(a.id) }}
                        style={{
                          padding: '5px 12px',
                          borderRadius: '6px',
                          border: '1px solid rgba(248,113,113,0.3)',
                          background: 'rgba(248,113,113,0.08)',
                          color: '#f87171',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* ── REAL ESTATE SECTION ── */}
      <section>
        <SectionHeader
          title="Real Estate"
          subtitle="Properties and mortgage tracking"
          onAdd={() => { setEditingAsset(null); setFormSection('Real Estate') }}
          addLabel="Add Property"
        />

        {formSection === 'Real Estate' && (
          <div style={{ marginBottom: '20px' }}>
            <AssetForm
              asset={editingAsset ?? undefined}
              initialAssetClass="Real Estate"
              onSubmit={handleSubmit}
              onCancel={() => { setFormSection(null); setEditingAsset(null) }}
              isLoading={saving}
            />
          </div>
        )}

        {/* Real estate summary */}
        {realEstateAssets.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
            <StatCard label="Total Property Value" value={fmtSimple(totalPropertyValue) + ' PLN'} />
            <StatCard label="Total Mortgage" value={fmtSimple(totalMortgage) + ' PLN'} valueColor="#f87171" />
            <StatCard
              label="Total Net Equity"
              value={fmtSimple(totalNetEquity) + ' PLN'}
              valueColor={totalNetEquity >= 0 ? '#34d399' : '#f87171'}
            />
          </div>
        )}

        {realEstateAssets.length === 0 && formSection !== 'Real Estate' && (
          <div
            style={{
              padding: '24px',
              borderRadius: '10px',
              border: '1px dashed var(--glass-border)',
              textAlign: 'center',
              color: 'var(--text-tertiary)',
              fontSize: '14px',
            }}
          >
            No real estate assets yet. Add your first property to track its value and mortgage.
          </div>
        )}

        {/* Real estate asset cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {realEstateAssets.map((a) => {
            const mortgage = a.mortgage_remaining ?? 0
            const netEquity = a.current_value - mortgage
            const isSelected = selectedId === a.id
            return (
              <div
                key={a.id}
                style={{
                  background: 'var(--glass-bg)',
                  border: `1px solid ${isSelected ? 'rgba(99,102,241,0.5)' : 'var(--glass-border)'}`,
                  borderRadius: '10px',
                  padding: '16px 20px',
                  cursor: 'pointer',
                }}
                onClick={() => setSelectedId(isSelected ? null : a.id)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {a.name}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginLeft: '8px' }}>
                      {a.currency}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                      Value: <strong style={{ color: 'var(--text-primary)' }}>{fmtSimple(a.current_value)}</strong>
                    </div>
                    {a.mortgage_remaining != null && (
                      <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                        Mortgage: <strong style={{ color: '#f87171' }}>{fmtSimple(a.mortgage_remaining)}</strong>
                      </div>
                    )}
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                      Net Equity:{' '}
                      <strong style={{ color: netEquity >= 0 ? '#34d399' : '#f87171' }}>
                        {fmtSimple(netEquity)}
                      </strong>
                    </div>
                  </div>
                </div>

                {isSelected && (
                  <div style={{ marginTop: '14px', borderTop: '1px solid var(--glass-border)', paddingTop: '14px' }}>
                    {a.notes && (
                      <div style={{ fontSize: '13px', color: 'var(--text-tertiary)', marginBottom: '8px' }}>
                        {a.notes}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                      <button
                        onClick={(e) => { e.stopPropagation(); setEditingAsset(a); setFormSection('Real Estate') }}
                        style={{
                          padding: '5px 12px',
                          borderRadius: '6px',
                          border: '1px solid var(--glass-border)',
                          background: 'transparent',
                          color: 'var(--text-secondary)',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); void handleDelete(a.id) }}
                        style={{
                          padding: '5px 12px',
                          borderRadius: '6px',
                          border: '1px solid rgba(248,113,113,0.3)',
                          background: 'rgba(248,113,113,0.08)',
                          color: '#f87171',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
