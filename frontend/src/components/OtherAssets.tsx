/**
 * OtherAssets component — manage manually-valued assets (crypto, real estate, other).
 */

import React, { useState, useEffect } from 'react'

import {
  getOtherAssets,
  getOtherAssetAnalysis,
  getOtherAssetsPortfolioSummary,
  createOtherAsset,
  updateOtherAsset,
  deleteOtherAsset,
  type OtherAsset,
  type OtherAssetAnalysis,
  type OtherAssetsPortfolioSummary,
  type OtherAssetCreate,
  type OtherAssetUpdate,
} from '../services/assetsApi'
import { AssetForm } from './AssetForm'
import { ErrorDisplay } from './ErrorDisplay'
import { Loading } from './Loading'

interface OtherAssetsProps {
  token: string
}

const summaryCardStyle: React.CSSProperties = {
  background: 'var(--glass-bg)',
  border: '1px solid var(--glass-border)',
  borderRadius: '12px',
  padding: '16px',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
}

const summaryLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  color: 'var(--text-tertiary)',
}

const summaryValueStyle: React.CSSProperties = {
  fontSize: '22px',
  fontWeight: 700,
  color: 'var(--text-primary)',
}

export const OtherAssets: React.FC<OtherAssetsProps> = ({ token }) => {
  const [assets, setAssets] = useState<OtherAsset[]>([])
  const [summary, setSummary] = useState<OtherAssetsPortfolioSummary | null>(null)
  const [selectedAsset, setSelectedAsset] = useState<OtherAsset | null>(null)
  const [analysis, setAnalysis] = useState<OtherAssetAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingAsset, setEditingAsset] = useState<OtherAsset | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    void loadData()
  }, [token])

  useEffect(() => {
    if (selectedAsset) {
      void fetchAnalysis(selectedAsset.id)
    }
  }, [selectedAsset])

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [assetsData, summaryData] = await Promise.all([
        getOtherAssets(token),
        getOtherAssetsPortfolioSummary(token),
      ])
      setAssets(assetsData)
      setSummary(summaryData)

      if (assetsData.length > 0 && !selectedAsset) {
        setSelectedAsset(assetsData[0])
      } else if (selectedAsset && assetsData.length > 0) {
        const updated = assetsData.find((a) => a.id === selectedAsset.id)
        setSelectedAsset(updated ?? assetsData[0])
      } else if (assetsData.length === 0) {
        setSelectedAsset(null)
        setAnalysis(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assets')
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalysis = async (assetId: number) => {
    try {
      const data = await getOtherAssetAnalysis(token, assetId)
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load asset analysis')
    }
  }

  const handleSave = async (data: OtherAssetCreate | OtherAssetUpdate) => {
    setFormLoading(true)
    setError('')
    try {
      if (editingAsset) {
        await updateOtherAsset(token, editingAsset.id, data as OtherAssetUpdate)
      } else {
        await createOtherAsset(token, data as OtherAssetCreate)
      }
      setShowForm(false)
      setEditingAsset(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save asset')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (assetId: number) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return
    try {
      await deleteOtherAsset(token, assetId)
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(null)
        setAnalysis(null)
      }
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete asset')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingAsset(null)
    setError('')
  }

  const fmt = (n: number, decimals = 2) =>
    n.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })

  const profitColor = (v: number | null) =>
    v === null ? 'var(--text-primary)' : v >= 0 ? '#34d399' : '#f87171'

  if (loading) return <Loading />

  return (
    <div style={{ minHeight: '100vh', padding: '24px' }}>
      {/* Header */}
      <div
        style={{
          marginBottom: '32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#ffffff', marginBottom: '8px' }}>
            Other Assets
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Manually-valued assets — crypto, real estate and more. No automatic pricing.
          </p>
        </div>
        <button
          onClick={() => { setEditingAsset(null); setShowForm(true) }}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            background: 'rgba(99, 102, 241, 0.1)',
            color: '#6366f1',
            fontSize: '14px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span>+</span> Add Asset
        </button>
      </div>

      {error && <ErrorDisplay message={error} />}

      {/* Form */}
      {showForm && (
        <div style={{ marginBottom: '24px' }}>
          <AssetForm
            asset={editingAsset ?? undefined}
            onSubmit={handleSave}
            onCancel={handleCancel}
            isLoading={formLoading}
          />
        </div>
      )}

      {assets.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '48px 24px',
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)',
            borderRadius: '12px',
          }}
        >
          <p style={{ color: 'var(--text-tertiary)', marginBottom: '8px' }}>
            No manually-valued assets yet.
          </p>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '12px', marginBottom: '16px' }}>
            Add cryptocurrencies, real estate or any other asset with a manual value.
          </p>
          <button
            onClick={() => setShowForm(true)}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              background: 'rgba(99, 102, 241, 0.1)',
              color: '#6366f1',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            Add First Asset
          </button>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          {summary && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px',
                marginBottom: '24px',
              }}
            >
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Total Value</span>
                <span style={summaryValueStyle}>{fmt(summary.total_value)} PLN</span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  {summary.assets_count} asset{summary.assets_count !== 1 ? 's' : ''}
                </span>
              </div>

              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Total Cost</span>
                <span style={summaryValueStyle}>
                  {summary.total_cost > 0 ? fmt(summary.total_cost) : '—'} {summary.total_cost > 0 ? 'PLN' : ''}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  where cost basis known
                </span>
              </div>

              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Total P&amp;L</span>
                <span
                  style={{
                    ...summaryValueStyle,
                    color: summary.total_cost > 0 ? profitColor(summary.total_profit) : 'var(--text-tertiary)',
                  }}
                >
                  {summary.total_cost > 0
                    ? `${summary.total_profit >= 0 ? '+' : ''}${fmt(summary.total_profit)} PLN`
                    : '—'}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  {summary.total_cost > 0 && summary.total_profit !== 0
                    ? `${((summary.total_profit / summary.total_cost) * 100).toFixed(2)}%`
                    : 'no cost basis'}
                </span>
              </div>

              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>By Class</span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
                  {Object.entries(summary.assets_by_class).map(([cls, data]) => (
                    <div key={cls} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{cls}</span>
                      <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {fmt(data.total_value)} PLN
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Main Content */}
          <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '24px' }}>
            {/* Asset List */}
            <div
              style={{
                background: 'var(--glass-bg)',
                border: '1px solid var(--glass-border)',
                borderRadius: '12px',
                padding: '16px',
                maxHeight: '600px',
                overflowY: 'auto',
              }}
            >
              <h3
                style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: 'var(--text-secondary)',
                  marginBottom: '16px',
                }}
              >
                Your Assets
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {assets.map((asset) => (
                  <div
                    key={asset.id}
                    onClick={() => setSelectedAsset(asset)}
                    style={{
                      padding: '12px',
                      borderRadius: '6px',
                      background:
                        selectedAsset?.id === asset.id
                          ? 'rgba(99, 102, 241, 0.15)'
                          : 'transparent',
                      border: `1px solid ${
                        selectedAsset?.id === asset.id
                          ? 'rgba(99, 102, 241, 0.3)'
                          : 'transparent'
                      }`,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '13px',
                        fontWeight: '500',
                        color: 'var(--text-primary)',
                        marginBottom: '2px',
                      }}
                    >
                      {asset.name}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {asset.asset_class}
                    </div>
                    <div
                      style={{
                        fontSize: '12px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginTop: '4px',
                      }}
                    >
                      {fmt(asset.current_value)} {asset.currency}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Asset Details */}
            {selectedAsset && analysis && (
              <div>
                <div
                  style={{
                    background: 'var(--glass-bg)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '12px',
                    padding: '24px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '20px',
                    }}
                  >
                    <div>
                      <h3
                        style={{
                          fontSize: '18px',
                          fontWeight: 'bold',
                          color: 'var(--text-primary)',
                          marginBottom: '4px',
                        }}
                      >
                        {selectedAsset.name}
                      </h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                        {selectedAsset.asset_class} · {selectedAsset.currency}
                        {selectedAsset.quantity !== null
                          ? ` · ${selectedAsset.quantity} units`
                          : ''}
                      </p>
                      {selectedAsset.notes && (
                        <p
                          style={{
                            color: 'var(--text-tertiary)',
                            fontSize: '12px',
                            marginTop: '4px',
                            fontStyle: 'italic',
                          }}
                        >
                          {selectedAsset.notes}
                        </p>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => { setEditingAsset(selectedAsset); setShowForm(true) }}
                        style={{
                          padding: '6px 12px',
                          borderRadius: '4px',
                          border: '1px solid rgba(99, 102, 241, 0.3)',
                          background: 'rgba(99, 102, 241, 0.1)',
                          color: '#6366f1',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => { void handleDelete(selectedAsset.id) }}
                        style={{
                          padding: '6px 12px',
                          borderRadius: '4px',
                          border: '1px solid rgba(248, 113, 113, 0.3)',
                          background: 'rgba(248, 113, 113, 0.1)',
                          color: '#f87171',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div
                    style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}
                  >
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        CURRENT VALUE
                      </span>
                      <div
                        style={{ color: 'var(--text-primary)', fontWeight: '600', fontSize: '18px' }}
                      >
                        {fmt(selectedAsset.current_value)} {selectedAsset.currency}
                      </div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}>
                        manually set · no auto-pricing
                      </div>
                    </div>

                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        ASSET CLASS
                      </span>
                      <div style={{ color: '#a78bfa', fontWeight: '600', fontSize: '18px' }}>
                        {selectedAsset.asset_class}
                      </div>
                    </div>

                    {analysis.total_cost !== null && (
                      <div>
                        <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                          TOTAL COST
                        </span>
                        <div
                          style={{ color: 'var(--text-primary)', fontWeight: '600', fontSize: '18px' }}
                        >
                          {fmt(analysis.total_cost)} {selectedAsset.currency}
                        </div>
                        {selectedAsset.quantity !== null && selectedAsset.purchase_price !== null && (
                          <div
                            style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}
                          >
                            {selectedAsset.quantity} × {fmt(selectedAsset.purchase_price)}
                          </div>
                        )}
                      </div>
                    )}

                    {analysis.profit !== null && (
                      <div>
                        <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                          PROFIT / LOSS
                        </span>
                        <div
                          style={{
                            color: profitColor(analysis.profit),
                            fontWeight: '600',
                            fontSize: '18px',
                          }}
                        >
                          {analysis.profit >= 0 ? '+' : ''}
                          {fmt(analysis.profit)} {selectedAsset.currency}
                        </div>
                        {analysis.profit_pct !== null && (
                          <div
                            style={{
                              color: profitColor(analysis.profit),
                              fontSize: '11px',
                              marginTop: '2px',
                            }}
                          >
                            {analysis.profit_pct >= 0 ? '+' : ''}
                            {analysis.profit_pct.toFixed(2)}%
                          </div>
                        )}
                      </div>
                    )}

                    {analysis.total_cost === null && (
                      <div style={{ gridColumn: '1 / -1' }}>
                        <div
                          style={{
                            padding: '10px 14px',
                            borderRadius: '6px',
                            background: 'rgba(251,191,36,0.08)',
                            border: '1px solid rgba(251,191,36,0.2)',
                            color: '#fbbf24',
                            fontSize: '12px',
                          }}
                        >
                          Add quantity and purchase price to track P&amp;L for this asset.
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
