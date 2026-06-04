/**
 * CashForm component for creating and editing cash accounts.
 */

import React, { useState, useEffect } from 'react'
import type { CashAccount, CashAccountType, CashCreate, CashUpdate } from '../services/cashApi'

interface CashFormProps {
  account?: CashAccount
  onSubmit: (data: CashCreate | CashUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: '6px',
  border: '1px solid var(--glass-border)',
  background: 'rgba(0, 0, 0, 0.2)',
  color: 'var(--text-primary)',
  fontSize: '13px',
  boxSizing: 'border-box',
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: '6px',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}

export const CashForm: React.FC<CashFormProps> = ({
  account,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState({
    name: account?.name ?? '',
    account_type: (account?.account_type ?? 'Savings') as CashAccountType,
    balance: account?.balance ?? '',
    interest_rate: account?.interest_rate ?? '',
    bank_name: account?.bank_name ?? '',
    currency: account?.currency ?? 'PLN',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (account) {
      setFormData({
        name: account.name,
        account_type: account.account_type,
        balance: account.balance,
        interest_rate: account.interest_rate ?? '',
        bank_name: account.bank_name ?? '',
        currency: account.currency,
      })
    }
  }, [account])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      if (!formData.name.trim()) {
        setError('Account name is required')
        setSubmitting(false)
        return
      }

      const balance = parseFloat(formData.balance as string)
      if (isNaN(balance) || balance < 0) {
        setError('Balance must be a non-negative number')
        setSubmitting(false)
        return
      }

      const interestRate =
        formData.interest_rate === '' ? null : parseFloat(formData.interest_rate as string)
      if (interestRate !== null && (isNaN(interestRate) || interestRate < 0 || interestRate > 100)) {
        setError('Interest rate must be between 0 and 100')
        setSubmitting(false)
        return
      }

      const submitData: CashCreate = {
        name: formData.name.trim(),
        account_type: formData.account_type,
        balance,
        interest_rate: interestRate,
        bank_name: formData.bank_name.trim() || null,
        currency: formData.currency,
      }

      await onSubmit(submitData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSubmitting(false)
    }
  }

  const isDisabled = submitting || isLoading

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        background: 'var(--glass-bg)',
        border: '1px solid var(--glass-border)',
        borderRadius: '12px',
        padding: '24px',
      }}
    >
      <h3
        style={{
          fontSize: '16px',
          fontWeight: 'bold',
          color: 'var(--text-primary)',
          marginBottom: '20px',
        }}
      >
        {account ? 'Edit Cash Account' : 'Add Cash Account'}
      </h3>

      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: '6px',
            background: 'rgba(248, 113, 113, 0.1)',
            border: '1px solid rgba(248, 113, 113, 0.3)',
            color: '#f87171',
            fontSize: '13px',
            marginBottom: '16px',
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '16px',
          marginBottom: '16px',
        }}
      >
        {/* Account Name */}
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={labelStyle}>Account Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            style={inputStyle}
            placeholder="e.g., PKO Savings Account"
            required
            disabled={isDisabled}
          />
        </div>

        {/* Account Type */}
        <div>
          <label style={labelStyle}>Account Type *</label>
          <select
            name="account_type"
            value={formData.account_type}
            onChange={handleChange}
            style={inputStyle}
            required
            disabled={isDisabled}
          >
            <option value="Savings">Savings</option>
            <option value="Checking">Checking</option>
            <option value="High-Yield Savings">High-Yield Savings</option>
            <option value="Money Market">Money Market</option>
            <option value="Cash">Cash</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Currency */}
        <div>
          <label style={labelStyle}>Currency *</label>
          <select
            name="currency"
            value={formData.currency}
            onChange={handleChange}
            style={inputStyle}
            required
            disabled={isDisabled}
          >
            <option value="PLN">PLN</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
          </select>
        </div>

        {/* Balance */}
        <div>
          <label style={labelStyle}>Balance *</label>
          <input
            type="number"
            name="balance"
            value={formData.balance}
            onChange={handleChange}
            style={inputStyle}
            placeholder="50000.00"
            min="0"
            step="0.01"
            required
            disabled={isDisabled}
          />
        </div>

        {/* Interest Rate */}
        <div>
          <label style={labelStyle}>Interest Rate (% / year)</label>
          <input
            type="number"
            name="interest_rate"
            value={formData.interest_rate}
            onChange={handleChange}
            style={inputStyle}
            placeholder="5.00"
            min="0"
            max="100"
            step="0.01"
            disabled={isDisabled}
          />
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            Leave empty if no interest
          </div>
        </div>

        {/* Bank Name */}
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={labelStyle}>Bank / Institution</label>
          <input
            type="text"
            name="bank_name"
            value={formData.bank_name}
            onChange={handleChange}
            style={inputStyle}
            placeholder="e.g., PKO Bank Polski"
            disabled={isDisabled}
          />
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
        <button
          type="button"
          onClick={onCancel}
          disabled={isDisabled}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid var(--glass-border)',
            background: 'transparent',
            color: 'var(--text-secondary)',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isDisabled}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            background: 'rgba(99, 102, 241, 0.15)',
            color: '#6366f1',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          {submitting || isLoading ? 'Saving...' : account ? 'Save Changes' : 'Add Account'}
        </button>
      </div>
    </form>
  )
}
