/**
 * BondForm component for creating and editing bonds.
 */

import React, { useState, useEffect } from 'react'
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
    interest_rate: bond?.interest_rate ?? '',
    interest_period_years: bond?.interest_period_years ?? '',
    capitalization: bond?.capitalization ?? 'ANNUAL',
    purchase_price: bond?.purchase_price ?? '',
    current_price: bond?.current_price ?? '',
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
        interest_rate: parseFloat(formData.interest_rate as string),
        interest_period_years: parseFloat(formData.interest_period_years as string),
        capitalization: formData.capitalization as 'ANNUAL' | 'MONTHLY',
        purchase_price: parseFloat(formData.purchase_price as string),
        current_price: formData.current_price
          ? parseFloat(formData.current_price as string)
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

      if (!formData.interest_rate || parseFloat(formData.interest_rate as string) < 0) {
        setError('Interest rate must be a non-negative number')
        setSubmitting(false)
        return
      }

      if (
        !formData.interest_period_years ||
        parseFloat(formData.interest_period_years as string) <= 0
      ) {
        setError('Interest period must be a positive number')
        setSubmitting(false)
        return
      }

      if (!formData.purchase_price || parseFloat(formData.purchase_price as string) <= 0) {
        setError('Purchase price must be a positive number')
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
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
      <h2 className="text-2xl font-bold mb-6">
        {bond ? 'Edit Bond' : 'Add New Bond'}
      </h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Bond Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="e.g., Polish Government 5Y Bond"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Interest Rate (%) *
          </label>
          <input
            type="number"
            name="interest_rate"
            value={formData.interest_rate}
            onChange={handleChange}
            step="0.01"
            min="0"
            max="100"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="5.50"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Interest Period (Years) *
          </label>
          <input
            type="number"
            name="interest_period_years"
            value={formData.interest_period_years}
            onChange={handleChange}
            step="0.1"
            min="0.1"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="5"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Capitalization *
          </label>
          <select
            name="capitalization"
            value={formData.capitalization}
            onChange={handleChange}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={submitting || isLoading}
            required
          >
            <option value="ANNUAL">Annual</option>
            <option value="MONTHLY">Monthly</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Purchase Price (PLN) *
          </label>
          <input
            type="number"
            name="purchase_price"
            value={formData.purchase_price}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="1000.00"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Current Price (PLN)
          </label>
          <input
            type="number"
            name="current_price"
            value={formData.current_price}
            onChange={handleChange}
            step="0.01"
            min="0.01"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="1000.00"
            disabled={submitting || isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Quantity *
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="1"
            disabled={submitting || isLoading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Purchase Date *
          </label>
          <input
            type="date"
            name="purchase_date"
            value={formData.purchase_date}
            onChange={handleChange}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={submitting || isLoading}
            required
          />
        </div>
      </div>

      <div className="flex gap-4 pt-6">
        <button
          type="submit"
          disabled={submitting || isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {submitting || isLoading ? 'Saving...' : bond ? 'Update Bond' : 'Create Bond'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting || isLoading}
          className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
