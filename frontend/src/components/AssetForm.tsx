/**
 * Form for adding or editing a manually-valued asset (crypto or real estate).
 * Pass `initialAssetClass` to pre-set the class (and lock the selector).
 */

import React, { useState, useEffect } from 'react'
import type { OtherAsset, OtherAssetClass, OtherAssetCreate, OtherAssetUpdate } from '../services/assetsApi'

interface AssetFormProps {
  asset?: OtherAsset
  initialAssetClass?: OtherAssetClass
  onSubmit: (data: OtherAssetCreate | OtherAssetUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

const ASSET_CLASSES: OtherAssetClass[] = ['Crypto', 'Real Estate', 'Other']
const CRYPTO_NAMES = ['BTC', 'ETH']
const CURRENCIES = ['PLN', 'USD', 'EUR', 'GBP']

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: '4px',
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  borderRadius: '6px',
  border: '1px solid var(--glass-border)',
  background: 'rgba(255,255,255,0.04)',
  color: 'var(--text-primary)',
  fontSize: '14px',
  outline: 'none',
  boxSizing: 'border-box',
}

export const AssetForm: React.FC<AssetFormProps> = ({
  asset,
  initialAssetClass,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const defaultClass = asset?.asset_class ?? initialAssetClass ?? 'Crypto'
  const [name, setName] = useState(asset?.name ?? (defaultClass === 'Crypto' ? 'BTC' : ''))
  const [assetClass, setAssetClass] = useState<OtherAssetClass>(defaultClass)
  const [currentValue, setCurrentValue] = useState(String(asset?.current_value ?? ''))
  const [currency, setCurrency] = useState(asset?.currency ?? 'PLN')
  const [quantity, setQuantity] = useState(String(asset?.quantity ?? ''))
  const [purchasePrice, setPurchasePrice] = useState(String(asset?.purchase_price ?? ''))
  const [mortgageRemaining, setMortgageRemaining] = useState(
    asset?.mortgage_remaining !== null && asset?.mortgage_remaining !== undefined
      ? String(asset.mortgage_remaining)
      : '',
  )
  const [notes, setNotes] = useState(asset?.notes ?? '')
  const [error, setError] = useState('')

  // When editing, sync state if asset prop changes
  useEffect(() => {
    if (asset) {
      setName(asset.name)
      setAssetClass(asset.asset_class)
      setCurrentValue(String(asset.current_value))
      setCurrency(asset.currency)
      setQuantity(asset.quantity !== null && asset.quantity !== undefined ? String(asset.quantity) : '')
      setPurchasePrice(
        asset.purchase_price !== null && asset.purchase_price !== undefined
          ? String(asset.purchase_price)
          : '',
      )
      setMortgageRemaining(
        asset.mortgage_remaining !== null && asset.mortgage_remaining !== undefined
          ? String(asset.mortgage_remaining)
          : '',
      )
      setNotes(asset.notes ?? '')
    }
  }, [asset])

  // When asset class changes (only relevant when class selector is shown), reset name if needed
  const handleAssetClassChange = (cls: OtherAssetClass) => {
    setAssetClass(cls)
    if (cls === 'Crypto') setName('BTC')
    else setName('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!name.trim()) { setError('Name is required'); return }
    const val = parseFloat(currentValue)
    if (isNaN(val) || val < 0) { setError('Current value must be a non-negative number'); return }

    const qty = quantity ? parseFloat(quantity) : null
    const pp = purchasePrice ? parseFloat(purchasePrice) : null
    const mortgage = mortgageRemaining ? parseFloat(mortgageRemaining) : null

    if (qty !== null && (isNaN(qty) || qty <= 0)) { setError('Quantity must be positive'); return }
    if (pp !== null && (isNaN(pp) || pp < 0)) { setError('Purchase price must be non-negative'); return }
    if (mortgage !== null && (isNaN(mortgage) || mortgage < 0)) {
      setError('Remaining mortgage must be non-negative')
      return
    }

    await onSubmit({
      name: name.trim(),
      asset_class: assetClass,
      current_value: val,
      currency,
      quantity: assetClass === 'Crypto' ? qty : null,
      purchase_price: assetClass === 'Crypto' ? pp : null,
      mortgage_remaining: assetClass === 'Real Estate' ? mortgage : null,
      notes: notes.trim() || null,
    })
  }

  const isCrypto = assetClass === 'Crypto'
  const isRealEstate = assetClass === 'Real Estate'
  const lockClass = initialAssetClass !== undefined || asset !== undefined

  const propertyValue = parseFloat(currentValue) || 0
  const mortgageVal = parseFloat(mortgageRemaining) || 0
  const netEquityPreview = propertyValue - mortgageVal

  return (
    <form
      onSubmit={(e) => { void handleSubmit(e) }}
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
        {asset
          ? 'Edit Asset'
          : isCrypto
          ? 'Add Cryptocurrency'
          : isRealEstate
          ? 'Add Property'
          : 'Add Asset'}
      </h3>

      {error && (
        <div
          style={{
            padding: '10px 14px',
            borderRadius: '6px',
            background: 'rgba(248,113,113,0.1)',
            border: '1px solid rgba(248,113,113,0.3)',
            color: '#f87171',
            fontSize: '13px',
            marginBottom: '16px',
          }}
        >
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Asset class (hidden when locked) */}
        {!lockClass && (
          <div>
            <label style={labelStyle}>Asset Class *</label>
            <select
              style={inputStyle}
              value={assetClass}
              onChange={(e) => handleAssetClassChange(e.target.value as OtherAssetClass)}
            >
              {ASSET_CLASSES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        )}

        {/* Name: dropdown for Crypto, text input for others */}
        <div style={lockClass ? { gridColumn: '1 / -1' } : {}}>
          <label style={labelStyle}>{isCrypto ? 'Coin *' : 'Property Name *'}</label>
          {isCrypto ? (
            <select
              style={inputStyle}
              value={name}
              onChange={(e) => setName(e.target.value)}
            >
              {CRYPTO_NAMES.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          ) : (
            <input
              style={inputStyle}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Warsaw Apartment"
              required
            />
          )}
        </div>

        {/* Currency */}
        <div>
          <label style={labelStyle}>Currency</label>
          <select
            style={inputStyle}
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          >
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Current value */}
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={labelStyle}>
            {isRealEstate ? 'Property Value *' : 'Current Value *'}
          </label>
          <input
            style={inputStyle}
            type="number"
            value={currentValue}
            onChange={(e) => setCurrentValue(e.target.value)}
            placeholder={isRealEstate ? 'Market value of the property' : 'Total current market value'}
            min={0}
            step="any"
            required
          />
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '3px', display: 'block' }}>
            No automatic pricing — update manually when value changes
          </span>
        </div>

        {/* Crypto-only: quantity + purchase price */}
        {isCrypto && (
          <>
            <div>
              <label style={labelStyle}>Quantity (optional)</label>
              <input
                style={inputStyle}
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g. 0.5"
                min={0}
                step="any"
              />
            </div>
            <div>
              <label style={labelStyle}>Purchase Price / Unit (optional)</label>
              <input
                style={inputStyle}
                type="number"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                placeholder="Cost per unit for P&L"
                min={0}
                step="any"
              />
            </div>
          </>
        )}

        {/* Real estate: mortgage */}
        {isRealEstate && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={labelStyle}>Remaining Mortgage Capital (optional)</label>
            <input
              style={inputStyle}
              type="number"
              value={mortgageRemaining}
              onChange={(e) => setMortgageRemaining(e.target.value)}
              placeholder="Outstanding mortgage principal"
              min={0}
              step="any"
            />
            {currentValue && (
              <span
                style={{
                  fontSize: '12px',
                  color: netEquityPreview >= 0 ? '#34d399' : '#f87171',
                  marginTop: '4px',
                  display: 'block',
                }}
              >
                Net equity = {propertyValue.toLocaleString()} − {mortgageVal.toLocaleString()} ={' '}
                <strong>{netEquityPreview.toLocaleString()}</strong>
              </span>
            )}
          </div>
        )}

        {/* Notes */}
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={labelStyle}>Notes (optional)</label>
          <textarea
            style={{ ...inputStyle, resize: 'vertical', minHeight: '72px' }}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any additional notes..."
          />
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid var(--glass-border)',
            background: 'transparent',
            color: 'var(--text-secondary)',
            fontSize: '14px',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid rgba(99,102,241,0.4)',
            background: 'rgba(99,102,241,0.15)',
            color: '#6366f1',
            fontSize: '14px',
            fontWeight: 500,
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Saving...' : asset ? 'Save Changes' : isCrypto ? 'Add Coin' : isRealEstate ? 'Add Property' : 'Add Asset'}
        </button>
      </div>
    </form>
  )
}

