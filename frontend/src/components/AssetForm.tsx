/**
 * Form for adding or editing a manually-valued asset (crypto or real estate).
 * Pass `initialAssetClass` to pre-set the class (and lock the selector).
 *
 * For crypto assets:
 *  - Price per unit is fetched automatically from CoinGecko (USD × 3.5 PLN),
 *    cached in sessionStorage so only one upstream request is made per session.
 *  - Quantity and purchase price are required.
 *  - Currency is locked to PLN.
 */

import React, { useState, useEffect } from 'react'
import type { OtherAsset, OtherAssetClass, OtherAssetCreate, OtherAssetUpdate } from '../services/assetsApi'
import { getCryptoPricesPLN } from '../services/portfolioApi'

interface AssetFormProps {
  asset?: OtherAsset
  initialAssetClass?: OtherAssetClass
  onSubmit: (data: OtherAssetCreate | OtherAssetUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  token?: string
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
  token,
}) => {
  const defaultClass = asset?.asset_class ?? initialAssetClass ?? 'Crypto'
  const [name, setName] = useState(asset?.name ?? (defaultClass === 'Crypto' ? 'BTC' : ''))
  const [assetClass, setAssetClass] = useState<OtherAssetClass>(defaultClass)
  const [currentValue, setCurrentValue] = useState(String(asset?.current_value ?? ''))
  const [currency, setCurrency] = useState(asset?.currency ?? 'PLN')
  const [quantity, setQuantity] = useState(String(asset?.quantity ?? ''))
  const [purchasePrice, setPurchasePrice] = useState(String(asset?.purchase_price ?? ''))
  const [mortgageRemaining, setMortgageRemaining] = useState(
    asset?.mortgage_remaining != null ? String(asset.mortgage_remaining) : '',
  )
  const [notes, setNotes] = useState(asset?.notes ?? '')
  const [error, setError] = useState('')

  // Crypto live price state
  const [pricesLoading, setPricesLoading] = useState(false)
  const [pricesError, setPricesError] = useState(false)
  const [livePricePLN, setLivePricePLN] = useState<number | null>(null)
  const [livePriceUSD, setLivePriceUSD] = useState<number | null>(null)

  const isCrypto = assetClass === 'Crypto'
  const isRealEstate = assetClass === 'Real Estate'
  const lockClass = initialAssetClass !== undefined || asset !== undefined

  const applyPrice = (prices: { BTC: number; ETH: number }, coin: string) => {
    const pln = coin === 'BTC' ? prices.BTC : prices.ETH
    const rounded = Math.round(pln * 100) / 100
    const usd = Math.round((pln / 3.5) * 100) / 100
    setLivePricePLN(rounded)
    setLivePriceUSD(usd)
    setCurrentValue(String(rounded))
  }

  // Auto-fetch once per session when form opens for a crypto asset
  useEffect(() => {
    if (!isCrypto || !token) return
    setPricesLoading(true)
    setPricesError(false)
    void getCryptoPricesPLN(token)
      .then((prices) => { applyPrice(prices, name) })
      .catch(() => { setPricesError(true) })
      .finally(() => { setPricesLoading(false) })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isCrypto])

  // When coin selection changes, re-apply from cache (no extra network call)
  const handleNameChange = (newName: string) => {
    setName(newName)
    if (!token) return
    void getCryptoPricesPLN(token).then((prices) => { applyPrice(prices, newName) })
  }

  // Sync state when editing an existing asset
  useEffect(() => {
    if (asset) {
      setName(asset.name)
      setAssetClass(asset.asset_class)
      setCurrentValue(String(asset.current_value))
      setCurrency(asset.currency)
      setQuantity(asset.quantity != null ? String(asset.quantity) : '')
      setPurchasePrice(asset.purchase_price != null ? String(asset.purchase_price) : '')
      setMortgageRemaining(asset.mortgage_remaining != null ? String(asset.mortgage_remaining) : '')
      setNotes(asset.notes ?? '')
    }
  }, [asset])

  const handleAssetClassChange = (cls: OtherAssetClass) => {
    setAssetClass(cls)
    if (cls === 'Crypto') {
      setName('BTC')
      setLivePricePLN(null)
      if (token) {
        setPricesLoading(true)
        void getCryptoPricesPLN(token)
          .then((prices) => { applyPrice(prices, 'BTC') })
          .catch(() => { setPricesError(true) })
          .finally(() => { setPricesLoading(false) })
      }
    } else {
      setName('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!name.trim()) { setError('Name is required'); return }

    const val = parseFloat(currentValue)
    if (isNaN(val) || val < 0) { setError('Could not determine asset price — please try again.'); return }

    if (isCrypto) {
      const qty = parseFloat(quantity)
      if (!quantity || isNaN(qty) || qty <= 0) { setError('Quantity is required and must be positive'); return }
      const pp = parseFloat(purchasePrice)
      if (!purchasePrice || isNaN(pp) || pp < 0) { setError('Purchase price is required'); return }
    }

    const mortgage = mortgageRemaining ? parseFloat(mortgageRemaining) : null
    if (mortgage !== null && (isNaN(mortgage) || mortgage < 0)) {
      setError('Remaining mortgage must be non-negative')
      return
    }

    await onSubmit({
      name: name.trim(),
      asset_class: assetClass,
      current_value: val,
      currency: isCrypto ? 'PLN' : currency,
      quantity: isCrypto ? parseFloat(quantity) : null,
      purchase_price: isCrypto ? Math.round(parseFloat(purchasePrice) * 3.5 * 100) / 100 : null,
      mortgage_remaining: isRealEstate ? mortgage : null,
      notes: notes.trim() || null,
    })
  }

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
        {asset ? 'Edit Asset' : isCrypto ? 'Add Cryptocurrency' : isRealEstate ? 'Add Property' : 'Add Asset'}
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

        {/* Asset class selector (hidden when locked) */}
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

        {/* Name / Coin */}
        <div style={lockClass ? { gridColumn: '1 / -1' } : {}}>
          <label style={labelStyle}>{isCrypto ? 'Coin *' : 'Name *'}</label>
          {isCrypto ? (
            <select
              style={inputStyle}
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
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

        {/* Currency — hidden for crypto (locked to PLN) */}
        {!isCrypto && (
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
        )}

        {/* Crypto: read-only live price display */}
        {isCrypto && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={labelStyle}>Current Price (PLN)</label>
            <div
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid var(--glass-border)',
                background: 'rgba(255,255,255,0.02)',
                fontSize: '14px',
                color: pricesError
                  ? '#f87171'
                  : livePricePLN !== null
                  ? 'var(--text-primary)'
                  : 'var(--text-tertiary)',
                minHeight: '38px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {pricesLoading
                ? 'Fetching live price…'
                : pricesError
                ? 'Could not fetch price — check connection and reopen the form'
                : livePriceUSD !== null && livePricePLN !== null
                ? (
                  <>
                    <span>{livePriceUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</span>
                    <span style={{ color: 'var(--text-tertiary)', fontSize: '12px' }}>→</span>
                    <span style={{ fontWeight: 600 }}>{livePricePLN.toLocaleString('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} PLN</span>
                  </>
                )
                : '—'}
            </div>
            <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '3px', display: 'block' }}>
              Live from CoinGecko · × 3.5 exchange rate · cached for this session
            </span>
          </div>
        )}

        {/* Non-crypto: manual current value input */}
        {!isCrypto && (
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
        )}

        {/* Crypto: required quantity + required purchase price */}
        {isCrypto && (
          <>
            <div>
              <label style={labelStyle}>Quantity *</label>
              <input
                style={inputStyle}
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g. 0.5"
                min={0}
                step="any"
                required
              />
            </div>
            <div>
              <label style={labelStyle}>Purchase Price / Unit (USD) *</label>
              <input
                style={inputStyle}
                type="number"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                placeholder="Cost per unit in USD"
                min={0}
                step="any"
                required
              />
            </div>

            {/* Live P&L preview */}
            {quantity && livePricePLN !== null && (
              <div
                style={{
                  gridColumn: '1 / -1',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'rgba(99,102,241,0.07)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  fontSize: '13px',
                }}
              >
                {(() => {
                  const qty = parseFloat(quantity)
                  const pp = parseFloat(purchasePrice)
                  const totalVal = qty * livePricePLN
                  const totalCost = !isNaN(pp) && purchasePrice ? qty * (pp * 3.5) : null
                  const profit = totalCost !== null ? totalVal - totalCost : null
                  const pct = totalCost && totalCost > 0 && profit !== null ? (profit / totalCost) * 100 : null
                  return (
                    <>
                      <div style={{ color: 'var(--text-secondary)', marginBottom: '4px' }}>
                        Total holding value:{' '}
                        <strong style={{ color: 'var(--text-primary)' }}>
                          {totalVal.toLocaleString('pl-PL', { maximumFractionDigits: 2 })} PLN
                        </strong>
                      </div>
                      {profit !== null && (
                        <div style={{ color: profit >= 0 ? '#34d399' : '#f87171' }}>
                          P&L: {profit >= 0 ? '+' : ''}
                          {profit.toLocaleString('pl-PL', { maximumFractionDigits: 2 })}
                          {pct !== null && ` (${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%)`}
                        </div>
                      )}
                    </>
                  )
                })()}
              </div>
            )}
          </>
        )}

        {/* Real estate: optional mortgage */}
        {isRealEstate && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label style={labelStyle}>Remaining Mortgage (optional)</label>
            <input
              style={inputStyle}
              type="number"
              value={mortgageRemaining}
              onChange={(e) => setMortgageRemaining(e.target.value)}
              placeholder="Outstanding mortgage balance"
              min={0}
              step="any"
            />
            {mortgageRemaining && (
              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '3px', display: 'block' }}>
                Net equity: {netEquityPreview.toLocaleString('pl-PL', { maximumFractionDigits: 2 })} {currency}
              </span>
            )}
          </div>
        )}

        {/* Notes */}
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={labelStyle}>Notes (optional)</label>
          <input
            style={inputStyle}
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional notes"
            maxLength={1000}
          />
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: '8px 16px',
            borderRadius: '8px',
            background: 'transparent',
            border: '1px solid var(--glass-border)',
            color: 'var(--text-secondary)',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading || (isCrypto && pricesLoading)}
          style={{
            padding: '8px 20px',
            borderRadius: '8px',
            background: isLoading || (isCrypto && pricesLoading) ? 'rgba(99,102,241,0.4)' : 'rgba(99,102,241,0.8)',
            border: 'none',
            color: '#fff',
            fontSize: '13px',
            fontWeight: 600,
            cursor: isLoading || (isCrypto && pricesLoading) ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Saving…' : asset ? 'Save Changes' : 'Add Asset'}
        </button>
      </div>
    </form>
  )
}
