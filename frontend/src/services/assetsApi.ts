/**
 * API service for Other Asset (manual valuation) endpoints.
 */

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type OtherAssetClass = 'Crypto' | 'Real Estate' | 'Other'

export interface OtherAsset {
  id: number
  name: string
  asset_class: OtherAssetClass
  current_value: number
  currency: string
  quantity: number | null
  purchase_price: number | null
  mortgage_remaining: number | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface OtherAssetCreate {
  name: string
  asset_class: OtherAssetClass
  current_value: number
  currency?: string
  quantity?: number | null
  purchase_price?: number | null
  mortgage_remaining?: number | null
  notes?: string | null
}

export interface OtherAssetUpdate {
  name?: string
  asset_class?: OtherAssetClass
  current_value?: number
  currency?: string
  quantity?: number | null
  purchase_price?: number | null
  mortgage_remaining?: number | null
  notes?: string | null
}

export interface OtherAssetAnalysis {
  asset_id: number
  name: string
  asset_class: OtherAssetClass
  current_value: number
  currency: string
  total_cost: number | null
  profit: number | null
  profit_pct: number | null
  net_equity: number | null
}

export interface OtherAssetsPortfolioSummary {
  total_value: number
  total_cost: number
  total_profit: number
  total_mortgage: number
  total_net_equity: number
  assets_count: number
  assets_by_class: Record<string, { count: number; total_value: number }>
}

const authHeaders = (token: string) => ({ Authorization: `Bearer ${token}` })

export async function getOtherAssets(token: string): Promise<OtherAsset[]> {
  const res = await axios.get(`${API_URL}/portfolio/assets`, { headers: authHeaders(token) })
  return res.data
}

export async function getOtherAsset(token: string, id: number): Promise<OtherAsset> {
  const res = await axios.get(`${API_URL}/portfolio/assets/${id}`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function getOtherAssetAnalysis(
  token: string,
  id: number,
): Promise<OtherAssetAnalysis> {
  const res = await axios.get(`${API_URL}/portfolio/assets/${id}/analysis`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function getOtherAssetsPortfolioSummary(
  token: string,
): Promise<OtherAssetsPortfolioSummary> {
  const res = await axios.get(`${API_URL}/portfolio/assets/summary`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function createOtherAsset(
  token: string,
  data: OtherAssetCreate,
): Promise<OtherAsset> {
  const res = await axios.post(`${API_URL}/portfolio/assets`, data, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function updateOtherAsset(
  token: string,
  id: number,
  data: OtherAssetUpdate,
): Promise<OtherAsset> {
  const res = await axios.put(`${API_URL}/portfolio/assets/${id}`, data, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function deleteOtherAsset(token: string, id: number): Promise<void> {
  await axios.delete(`${API_URL}/portfolio/assets/${id}`, { headers: authHeaders(token) })
}
