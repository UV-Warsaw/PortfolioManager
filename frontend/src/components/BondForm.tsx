/**
 * BondForm component for creating and editing bonds.
 */

import React, { useState } from 'react'
import type { Bond, BondCreate, BondUpdate } from '../types/api'

interface BondFormProps {
  bond?: Bond
  onSubmit: (data: BondCreate | BondUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export const BondForm: React.FC<BondFormProps> = ({
  bond,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState({
    name: bond?.name ?? '',
    annual_rate: bond?.annual_rate ?? '',
    years: bond?.years ?? '',
    capitalization: bond?.capitalization ?? 'Annual',
    principal: bond?.principal ?? '',
    redemption_price: bond?.redemption_price ?? '',
    quantity: bond?.quantity ?? 1,
    purchase_date: bond?.purchase_date?.split('T')[0] ?? '',
  })
  const [error, setError] = useState<string>('')
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) || 0 : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      const submitData = {
        name: formData.name,
        annual_rate: parseFloat(formData.annual_rate as string),
        years: parseFloat(formData.years as string),
        capitalization: formData.capitalization as 'Annual' | 'Monthly',
        principal: parseFloat(formData.principal as string),
        redemption_price: formData.redemption_price
          ? parseFloat(formData.redemption_price as string)
          : null,
        quantity: formData.quantity as number,
        purchase_date: new Date(formData.purchase_date as string).toISOString(),
      }

      // Validate required fields
      if (!formData.name.trim()) {
        setError('Bond name is required')
        setSubmitting(false)
        return
      }

      if (!formData.annual_rate || parseFloat(formData.annual_rate as string) < 0) {
        setError('Annual rate must be a non-negative number')
        setSubmitting(false)
        return
      }

      if (
        !formData.years ||
        parseFloat(formData.years as string) <= 0
      ) {
        setError('Years must be a positive number')
        setSubmitting(false)
        return
      }

      if (!formData.principal || parseFloat(formData.principal as string) <= 0) {
        setError('Principal must be a positive number')
        setSubmitting(false)
        return
      }

      if (!formData.purchase_date) {
        setError('Purchase date is required')
        setSubmitting(false)
        return
      }

      if ((formData.quantity as number) < 1) {
        setError('Quantity must be at least 1')
        setSubmitting(false)
        return
      }

      await onSubmit(submitData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSubmitting(false)
    }
  }

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
      <h2
        style={{
          fontSize: '20px',
          fontWeight: 'bold',
          marginBottom: '16px',
          color: '#ffffff',
        }}
      >
        {bond ? 'Edit Bond' : 'Add New Bond'}
      </h2>

      {error && <div style={{
        background: 'rgba(248, 113, 113, 0.12)',
        color: '#f87171',
        borderRadius: '12px',
        padding: '12px 16px',
        marginBottom: '16px',
        border: '1px solid rgba(248, 113, 113, 0.3)',
      }}>
        {error}
      </div>}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Bond Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="e.g., Polish Government 5Y Bond"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Annual Rate (%) *
          </label>
          <input
            type="number"
            name="annual_rate"
            value={formData.annual_rate}
            onChange={handleChange}
            step="0.01"
            min="0"
            max="100"
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="5.50"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Years *
          </label>
          <input
            type="number"
            name="years"
            value={formData.years}
            onChange={handleChange}
            step="0.1"
            min="0.1"
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="5"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Capitalization *
          </label>
          <select
            name="capitalization"
            value={formData.capitalization}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            disabled={submitting || isLoading}
            required
          >
            <option value="Annual">Annual</option>
            <option value="Monthly">Monthly</option>
          </select>
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Principal (PLN) *
          </label>
          <input
            type="number"
            name="principal"
            value={formData.principal}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="1000.00"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Redemption Price (PLN)
          </label>
          <input
            type="number"
            name="redemption_price"
            value={formData.redemption_price}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="1000.00"
            disabled={submitting || isLoading}
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Quantity *
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            placeholder="1"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label
            style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: '600',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-tertiary)',
              marginBottom: '6px',
            }}
          >
            Purchase Date *
          </label>
          <input
            type="date"
            name="purchase_date"
            value={formData.purchase_date}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: '6px',
              border: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.2)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
            disabled={submitting || isLoading}
            required
          />
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          type="submit"
          disabled={submitting || isLoading}
          style={{
            padding: '10px 16px',
            borderRadius: '6px',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            background: 'rgba(99, 102, 241, 0.15)',
            color: '#6366f1',
            fontSize: '13px',
            fontWeight: '600',
            cursor: submitting || isLoading ? 'not-allowed' : 'pointer',
            opacity: submitting || isLoading ? 0.5 : 1,
          }}
        >
          {submitting || isLoading ? 'Saving...' : bond ? 'Update Bond' : 'Create Bond'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting || isLoading}
          style={{
            padding: '10px 16px',
            borderRadius: '6px',
            border: '1px solid rgba(148, 163, 184, 0.3)',
            background: 'transparent',
            color: 'var(--text-secondary)',
            fontSize: '13px',
            fontWeight: '600',
            cursor: submitting || isLoading ? 'not-allowed' : 'pointer',
            opacity: submitting || isLoading ? 0.5 : 1,
          }}
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
