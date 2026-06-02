/**
 * Bonds component for displaying and managing bonds.
 */

import React, { useState, useEffect } from 'react'
import type { Bond, BondCreate, BondUpdate } from '../types/api'
import { getBonds, createBond, updateBond, deleteBond } from '../services/bondsApi'
import { BondForm } from './BondForm'
import { ErrorDisplay } from './ErrorDisplay'
import { Loading } from './Loading'

interface BondsProps {
  token: string
}

export const Bonds: React.FC<BondsProps> = ({ token }) => {
  const [bonds, setBonds] = useState<Bond[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingBond, setEditingBond] = useState<Bond | undefined>()
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadBonds()
  }, [token])

  const loadBonds = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getBonds(token)
      setBonds(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bonds')
    } finally {
      setLoading(false)
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
      setEditingBond(undefined)
      await loadBonds()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save bond')
    } finally {
      setFormLoading(false)
    }
  }

  const handleEditBond = (bond: Bond) => {
    setEditingBond(bond)
    setShowForm(true)
  }

  const handleDeleteBond = async (bondId: number) => {
    if (!window.confirm('Are you sure you want to delete this bond?')) {
      return
    }

    try {
      await deleteBond(token, bondId)
      await loadBonds()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete bond')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingBond(undefined)
    setError('')
  }

  const getTotalValue = (): number => {
    return bonds.reduce((total, bond) => {
      const price = bond.current_price ?? bond.purchase_price
      return total + price * bond.quantity
    }, 0)
  }

  const getTotalInvested = (): number => {
    return bonds.reduce((total, bond) => total + bond.purchase_price * bond.quantity, 0)
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div className="space-y-6">
      {error && <ErrorDisplay error={error} />}

      {showForm ? (
        <BondForm
          bond={editingBond}
          onSubmit={handleCreateBond}
          onCancel={handleCancel}
          isLoading={formLoading}
        />
      ) : (
        <>
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold">Bonds</h1>
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 font-medium"
            >
              + Add Bond
            </button>
          </div>

          {bonds.length === 0 ? (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <p className="text-gray-600 mb-4">No bonds yet. Start by adding your first bond!</p>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 font-medium"
              >
                Add Your First Bond
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">Total Market Value</p>
                  <p className="text-3xl font-bold text-indigo-600 mt-2">
                    {getTotalValue().toFixed(2)} PLN
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">Total Invested</p>
                  <p className="text-3xl font-bold text-indigo-600 mt-2">
                    {getTotalInvested().toFixed(2)} PLN
                  </p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">Unrealized Gain/Loss</p>
                  <p
                    className={`text-3xl font-bold mt-2 ${
                      getTotalValue() - getTotalInvested() >= 0
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {(getTotalValue() - getTotalInvested()).toFixed(2)} PLN
                  </p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Interest Rate
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Purchase Price
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Current Price
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {bonds.map((bond) => {
                      const currentPrice = bond.current_price ?? bond.purchase_price
                      const totalValue = currentPrice * bond.quantity
                      const gain = (currentPrice - bond.purchase_price) * bond.quantity

                      return (
                        <tr key={bond.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {bond.name}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-700">
                            {bond.interest_rate.toFixed(2)}% ({bond.capitalization})
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-700">{bond.quantity}</td>
                          <td className="px-6 py-4 text-sm text-gray-700">
                            {bond.purchase_price.toFixed(2)} PLN
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-700">
                            {currentPrice.toFixed(2)} PLN
                          </td>
                          <td className={`px-6 py-4 text-sm font-semibold ${
                            gain >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {totalValue.toFixed(2)} PLN
                            {gain !== 0 && (
                              <div className="text-xs font-normal">
                                ({gain > 0 ? '+' : ''}{gain.toFixed(2)} PLN)
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 text-sm space-x-2">
                            <button
                              onClick={() => handleEditBond(bond)}
                              className="text-indigo-600 hover:text-indigo-900 font-medium"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteBond(bond.id)}
                              className="text-red-600 hover:text-red-900 font-medium"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
