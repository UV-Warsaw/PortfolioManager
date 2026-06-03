/**
 * Cash component — manage cash accounts and track interest earnings.
 */

import React, { useState, useEffect } from 'react'

import {
  getCashAccounts,
  getCashAnalysis,
  getCashPortfolioSummary,
  createCashAccount,
  updateCashAccount,
  deleteCashAccount,
  type CashAccount,
  type CashAnalysis,
  type CashPortfolioSummary,
  type CashCreate,
  type CashUpdate,
} from '../services/cashApi'
import { CashForm } from './CashForm'
import { ErrorDisplay } from './ErrorDisplay'
import { Loading } from './Loading'

interface CashProps {
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

export const Cash: React.FC<CashProps> = ({ token }) => {
  const [accounts, setAccounts] = useState<CashAccount[]>([])
  const [summary, setSummary] = useState<CashPortfolioSummary | null>(null)
  const [selectedAccount, setSelectedAccount] = useState<CashAccount | null>(null)
  const [analysis, setAnalysis] = useState<CashAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingAccount, setEditingAccount] = useState<CashAccount | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [token])

  useEffect(() => {
    if (selectedAccount) {
      fetchAnalysis(selectedAccount.id)
    }
  }, [selectedAccount])

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [accountsData, summaryData] = await Promise.all([
        getCashAccounts(token),
        getCashPortfolioSummary(token),
      ])
      setAccounts(accountsData)
      setSummary(summaryData)

      if (accountsData.length > 0 && !selectedAccount) {
        setSelectedAccount(accountsData[0])
      } else if (selectedAccount && accountsData.length > 0) {
        const updated = accountsData.find((a) => a.id === selectedAccount.id)
        setSelectedAccount(updated ?? accountsData[0])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load cash accounts')
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalysis = async (accountId: number) => {
    try {
      const data = await getCashAnalysis(token, accountId)
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account analysis')
    }
  }

  const handleSave = async (data: CashCreate | CashUpdate) => {
    setFormLoading(true)
    setError('')
    try {
      if (editingAccount) {
        await updateCashAccount(token, editingAccount.id, data as CashUpdate)
      } else {
        await createCashAccount(token, data as CashCreate)
      }
      setShowForm(false)
      setEditingAccount(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save account')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (accountId: number) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return
    try {
      await deleteCashAccount(token, accountId)
      if (selectedAccount?.id === accountId) {
        setSelectedAccount(null)
        setAnalysis(null)
      }
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete account')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingAccount(null)
    setError('')
  }

  const fmt = (n: number, decimals = 2) =>
    n.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })

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
            Cash Accounts
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
            Manage savings, deposits and track interest earnings
          </p>
        </div>
        <button
          onClick={() => { setEditingAccount(null); setShowForm(true) }}
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
          <span>+</span> Add Account
        </button>
      </div>

      {error && <ErrorDisplay message={error} />}

      {/* Form */}
      {showForm && (
        <div style={{ marginBottom: '24px' }}>
          <CashForm
            account={editingAccount ?? undefined}
            onSubmit={handleSave}
            onCancel={handleCancel}
            isLoading={formLoading}
          />
        </div>
      )}

      {accounts.length === 0 ? (
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
            No cash accounts yet. Start by adding one!
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
            Create First Account
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
                <span style={summaryLabelStyle}>Total Balance</span>
                <span style={summaryValueStyle}>
                  {fmt(summary.total_balance)} PLN
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  {summary.accounts_count} account{summary.accounts_count !== 1 ? 's' : ''}
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Monthly Interest</span>
                <span style={{ ...summaryValueStyle, color: '#34d399' }}>
                  +{fmt(summary.total_monthly_interest)} PLN
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  ~{fmt(summary.total_monthly_interest / 30, 2)} PLN/day
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Annual Interest</span>
                <span style={{ ...summaryValueStyle, color: '#34d399' }}>
                  +{fmt(summary.total_annual_interest)} PLN
                </span>
              </div>
              <div style={summaryCardStyle}>
                <span style={summaryLabelStyle}>Weighted Avg Rate</span>
                <span style={{ ...summaryValueStyle, color: '#fbbf24' }}>
                  {(summary.weighted_avg_interest_rate).toFixed(2)}%
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  per year
                </span>
              </div>
            </div>
          )}

          {/* Main Content */}
          <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '24px' }}>
            {/* Account List */}
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
                Your Accounts
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {accounts.map((account) => (
                  <div
                    key={account.id}
                    onClick={() => setSelectedAccount(account)}
                    style={{
                      padding: '12px',
                      borderRadius: '6px',
                      background:
                        selectedAccount?.id === account.id
                          ? 'rgba(99, 102, 241, 0.15)'
                          : 'transparent',
                      border: `1px solid ${
                        selectedAccount?.id === account.id
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
                      {account.name}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {account.account_type}
                      {account.bank_name ? ` · ${account.bank_name}` : ''}
                    </div>
                    <div
                      style={{
                        fontSize: '12px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginTop: '4px',
                      }}
                    >
                      {fmt(account.balance)} {account.currency}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Account Details */}
            {selectedAccount && analysis && (
              <div>
                {/* Account Info Card */}
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
                        {selectedAccount.name}
                      </h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                        {selectedAccount.account_type}
                        {selectedAccount.bank_name ? ` · ${selectedAccount.bank_name}` : ''}
                        {' · '}
                        {selectedAccount.currency}
                        {selectedAccount.interest_rate
                          ? ` · ${selectedAccount.interest_rate}% p.a.`
                          : ''}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => { setEditingAccount(selectedAccount); setShowForm(true) }}
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
                        onClick={() => handleDelete(selectedAccount.id)}
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
                        BALANCE
                      </span>
                      <div style={{ color: 'var(--text-primary)', fontWeight: '600', fontSize: '18px' }}>
                        {fmt(selectedAccount.balance)} {selectedAccount.currency}
                      </div>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        INTEREST RATE
                      </span>
                      <div style={{ color: '#fbbf24', fontWeight: '600', fontSize: '18px' }}>
                        {selectedAccount.interest_rate
                          ? `${selectedAccount.interest_rate}% / year`
                          : '—'}
                      </div>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        MONTHLY INTEREST
                      </span>
                      <div style={{ color: '#34d399', fontWeight: '600' }}>
                        +{fmt(analysis.monthly_interest)} {selectedAccount.currency}
                      </div>
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '11px', marginTop: '2px' }}>
                        ~{fmt(analysis.daily_interest, 2)} {selectedAccount.currency}/day
                      </div>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '11px' }}>
                        ANNUAL INTEREST
                      </span>
                      <div style={{ color: '#34d399', fontWeight: '600' }}>
                        +{fmt(analysis.annual_interest)} {selectedAccount.currency}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Breakdown by account type if summary has multiple types */}
                {summary && Object.keys(summary.accounts_by_type).length > 1 && (
                  <div
                    style={{
                      background: 'var(--glass-bg)',
                      border: '1px solid var(--glass-border)',
                      borderRadius: '12px',
                      padding: '20px',
                    }}
                  >
                    <h4
                      style={{
                        fontSize: '12px',
                        fontWeight: '600',
                        letterSpacing: '0.08em',
                        textTransform: 'uppercase',
                        color: 'var(--text-secondary)',
                        marginBottom: '14px',
                      }}
                    >
                      Balance by Account Type
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {Object.entries(summary.accounts_by_type).map(([type, data]) => {
                        const pct =
                          summary.total_balance > 0
                            ? (data.total_balance / summary.total_balance) * 100
                            : 0
                        return (
                          <div key={type}>
                            <div
                              style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                marginBottom: '4px',
                              }}
                            >
                              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                                {type}
                                <span
                                  style={{
                                    fontSize: '11px',
                                    color: 'var(--text-tertiary)',
                                    marginLeft: '6px',
                                  }}
                                >
                                  ({data.count})
                                </span>
                              </span>
                              <span style={{ fontSize: '12px', color: 'var(--text-primary)', fontWeight: 600 }}>
                                {fmt(data.total_balance)} PLN
                              </span>
                            </div>
                            <div
                              style={{
                                height: '4px',
                                borderRadius: '2px',
                                background: 'rgba(99,102,241,0.12)',
                                position: 'relative',
                                overflow: 'hidden',
                              }}
                            >
                              <div
                                style={{
                                  position: 'absolute',
                                  top: 0,
                                  left: 0,
                                  height: '100%',
                                  width: `${pct}%`,
                                  background: 'rgba(99,102,241,0.7)',
                                  borderRadius: '2px',
                                }}
                              />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
