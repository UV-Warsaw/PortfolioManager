import React, { useState, useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'

import {
  getBonds,
  getBondAnalysis,
  getBondsPortfolioSummary,
  createBond,
  updateBond,
  deleteBond,
  type Bond,
  type BondAnalysis,
  type BondsPortfolioSummary,
} from '../services/bondsApi'
import type { BondCreate, BondUpdate } from '../types/api'
import { BondForm } from './BondForm'
import { ErrorDisplay } from './ErrorDisplay'
import { Loading } from './Loading'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

interface BondsProps {
  token: string
}

export const Bonds: React.FC<BondsProps> = ({ token }) => {
  const [bonds, setBonds] = useState<Bond[]>([])
  const [summary, setSummary] = useState<BondsPortfolioSummary | null>(null)
  const [selectedBond, setSelectedBond] = useState<Bond | null>(null)
  const [bondAnalysis, setBondAnalysis] = useState<BondAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingBond, setEditingBond] = useState<Bond | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [token])

  useEffect(() => {
    if (selectedBond) {
      fetchBondAnalysis(selectedBond.id)
    }
  }, [selectedBond])

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [bondsData, summaryData] = await Promise.all([
        getBonds(token),
        getBondsPortfolioSummary(token),
      ])

      setBonds(bondsData)
      setSummary(summaryData)

      if (bondsData.length > 0 && !selectedBond) {
        setSelectedBond(bondsData[0])
      } else if (selectedBond && bondsData.length > 0) {
        const updated = bondsData.find((b) => b.id === selectedBond.id)
        if (updated) {
          setSelectedBond(updated)
        } else {
          setSelectedBond(bondsData[0])
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bonds')
    } finally {
      setLoading(false)
    }
  }

  const fetchBondAnalysis = async (bondId: number) => {
    try {
      const analysis = await getBondAnalysis(token, bondId)
      setBondAnalysis(analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bond analysis')
    }
  }

  const handleCreateBond = async (data: BondCreate | BondUpdate) => {
    setFormLoading(true)
    setError('')
    try {
      if (editingBond) {
        await updateBond(token, editingBond.id, data as BondUpdate)
      } else {
        await createBond(token, data as BondCreate)
      }
      setShowForm(false)
      setEditingBond(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save bond')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteBond = async (bondId: number) => {
    if (!window.confirm('Are you sure you want to delete this bond?')) {
      return
    }

    try {
      await deleteBond(token, bondId)
      if (selectedBond?.id === bondId) {
        setSelectedBond(null)
        setBondAnalysis(null)
      }
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete bond')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingBond(null)
    setError('')
  }

  // Dynamic chart colors for dark theme
  const textColor = '#ffffff'
  const gridColor = 'rgba(99, 102, 241, 0.1)'

  // Prepare chart data
  const chartData = bondAnalysis
    ? {
        labels: bondAnalysis.value_projection.map((point) => {
          const date = new Date(point.date)
          return `${date.getMonth() + 1}/${date.getFullYear()}`
        }),
        datasets: [
          {
            label: 'Bond Value Growth',
            data: bondAnalysis.value_projection.map((point) => point.total_value),
            borderColor: 'rgba(99, 102, 241, 1)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      }
    : null

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: textColor,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: 'rgba(99, 102, 241, 0.5)',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: textColor,
        },
      },
      y: {
        beginAtZero: false,
        grid: {
          color: gridColor,
        },
        ticks: {
          color: textColor,
          callback: function (value: any) {
            return value.toLocaleString('en-US', {
              style: 'currency',
              currency: 'PLN',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0,
            })
          },
        },
      },
    },
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div className="page-section">
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
          <h1
            style={{
              fontSize: '28px',
              fontWeight: 'bold',
              color: '#ffffff',
              marginBottom: '8px',
            }}
          >
            Bonds
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Manage your bonds and track their growth
          </p>
        </div>

        <button
          onClick={() => {
            setEditingBond(null)
            setShowForm(true)
          }}
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
          <span>+</span> Add Bond
        </button>
      </div>

      {/* Error Display */}
      {error && <ErrorDisplay message={error} />}

      {/* Form */}
      {showForm && (
        <div
          style={{
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px',
          }}
        >
          <BondForm
            bond={editingBond ?? undefined}
            onSubmit={handleCreateBond}
            onCancel={handleCancel}
            isLoading={formLoading}
          />
        </div>
      )}

      {bonds.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '48px 24px',
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)',
            borderRadius: '12px',
          }}
        >
          <p style={{ color: 'var(--text-tertiary)', marginBottom: '16px' }}>
            No bonds yet. Start by adding one!
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
            Create First Bond
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
                <span style={summaryLabelStyle}>Total Invested</span>
                <span style={summaryValueStyle}>
                  {summary.total_invested.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{' '}
                  PLN
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Current Value</span>
                <span style={summaryValueStyle}>
                  {summary.current_total_value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{' '}
                  PLN
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Total Profit</span>
                <span
                  style={{
                    ...summaryValueStyle,
                    color: summary.total_profit >= 0 ? '#34d399' : '#f87171',
                  }}
                >
                  {summary.total_profit >= 0 ? '+' : ''}{summary.total_profit.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{' '}
                  PLN
                </span>
                <span
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: summary.total_profit_percentage >= 0 ? '#34d399' : '#f87171',
                  }}
                >
                  {summary.total_profit_percentage >= 0 ? '+' : ''}{summary.total_profit_percentage.toFixed(2)}%
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Redemption Value (After Tax)</span>
                <span style={{ ...summaryValueStyle, color: '#fbbf24' }}>
                  {summary.total_redemption_value_after_tax.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{' '}
                  PLN
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                  If all bonds redeemed today − 19% CGT
                </span>
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="sidebar-grid">
            {/* Bonds List */}
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
                Your Bonds
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {bonds.map((bond) => (
                  <div
                    key={bond.id}
                    onClick={() => setSelectedBond(bond)}
                    style={{
                      padding: '12px',
                      borderRadius: '6px',
                      background:
                        selectedBond?.id === bond.id
                          ? 'rgba(99, 102, 241, 0.15)'
                          : 'transparent',
                      border: `1px solid ${
                        selectedBond?.id === bond.id
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
                        marginBottom: '4px',
                      }}
                    >
                      {bond.name}
                    </div>
                    <div
                      style={{
                        fontSize: '11px',
                        color: 'var(--text-tertiary)',
                      }}
                    >
                      {bond.quantity}x @ {bond.principal.toFixed(2)} PLN
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Bond Details */}
            {selectedBond && bondAnalysis ? (
              <div>
                {/* Bond Info Card */}
                <div
                  style={{
                    background: 'var(--glass-bg)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '12px',
                    padding: '24px',
                    marginBottom: '24px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      marginBottom: '16px',
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
                        {selectedBond.name}
                      </h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                        {selectedBond.annual_rate}% annual rate, {selectedBond.capitalization}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => {
                          setEditingBond(selectedBond)
                          setShowForm(true)
                        }}
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
                        onClick={() => handleDeleteBond(selectedBond.id)}
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
                  <div className="two-col-grid">
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        CURRENT VALUE
                      </span>
                      <div style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                        {bondAnalysis.current_total_value.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}{' '}
                        PLN
                      </div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}>
                        {bondAnalysis.current_value_per_bond.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} PLN × {selectedBond.quantity}
                      </div>
                    </div>
                    {(() => {
                      const totalInvested = selectedBond.principal * selectedBond.quantity
                      const profit = bondAnalysis.current_total_value - totalInvested
                      const profitPct = totalInvested > 0 ? (profit / totalInvested) * 100 : 0
                      return (
                        <div>
                          <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                            GROSS PROFIT
                          </span>
                          <div
                            style={{
                              color: profit >= 0 ? '#34d399' : '#f87171',
                              fontWeight: '600',
                            }}
                          >
                            {profit >= 0 ? '+' : ''}{profit.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}{' '}
                            PLN
                          </div>
                          <div style={{ color: profit >= 0 ? '#34d399' : '#f87171', fontSize: '12px', marginTop: '2px' }}>
                            {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(2)}%
                          </div>
                        </div>
                      )
                    })()}
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        REDEMPTION VALUE (AFTER TAX)
                      </span>
                      <div style={{ color: '#fbbf24', fontWeight: '600' }}>
                        {bondAnalysis.redemption_value_after_tax.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}{' '}
                        PLN
                      </div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}>
                        Redeem now − 19% CGT on gain
                      </div>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        TAX ON GAIN
                      </span>
                      <div style={{ color: '#f87171', fontWeight: '600' }}>
                        {Math.max(0, bondAnalysis.current_total_value - bondAnalysis.redemption_value_after_tax).toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}{' '}
                        PLN
                      </div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}>
                        19% of gross profit
                      </div>
                    </div>
                  </div>
                </div>

                {/* Chart */}
                {chartData && (
                  <div
                    style={{
                      background: 'var(--glass-bg)',
                      border: '1px solid var(--glass-border)',
                      borderRadius: '12px',
                      padding: '24px',
                      height: '400px',
                    }}
                  >
                    <h3
                      style={{
                        fontSize: '13px',
                        fontWeight: '600',
                        letterSpacing: '0.08em',
                        textTransform: 'uppercase',
                        color: 'var(--text-secondary)',
                        marginBottom: '16px',
                      }}
                    >
                      Value Projection
                    </h3>
                    <Line data={chartData} options={chartOptions} height={320} />
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </>
      )}
    </div>
  )
}

const summaryCardStyle = {
  background: 'var(--glass-bg)',
  border: '1px solid var(--glass-border)',
  borderRadius: '10px',
  padding: '16px 20px',
  display: 'flex',
  flexDirection: 'column' as const,
  gap: '6px',
}

const summaryLabelStyle = {
  fontSize: '10px',
  fontWeight: 600,
  letterSpacing: '0.1em',
  textTransform: 'uppercase' as const,
  color: 'var(--text-tertiary)',
}

const summaryValueStyle = {
  fontSize: '18px',
  fontWeight: 700,
  color: 'var(--text-primary)',
  fontVariantNumeric: 'tabular-nums' as const,
}
