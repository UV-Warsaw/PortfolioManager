/**
 * API service for Bond endpoints.
 */

import axios from 'axios'
import type { Bond, BondCreate, BondUpdate } from '../types/api'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface BondValuePoint {
  date: string
  principal_value: number
  total_value: number
}

export interface BondAnalysis {
  bond_id: number
  name: string
  current_value_per_bond: number
  current_total_value: number
  sale_value_after_tax: number
  redemption_value_after_tax: number
  profit: number
  profit_percentage: number
  value_projection: BondValuePoint[]
}

export interface BondsPortfolioSummary {
  total_invested: number
  current_total_value: number
  total_profit: number
  total_profit_percentage: number
  total_sale_value_after_tax: number
  total_redemption_value_after_tax: number
  bonds_count: number
}

/**
 * Create a new bond.
 *
 * @param token - Authentication token
 * @param bondData - Bond creation data
 * @returns Created bond response
 */
export async function createBond(token: string, bondData: BondCreate): Promise<Bond> {
  const response = await axios.post<Bond>(`${API_URL}/portfolio/bonds`, bondData, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data
}

/**
 * Get all bonds.
 *
 * @param token - Authentication token
 * @returns List of bonds
 */
export async function getBonds(token: string): Promise<Bond[]> {
  const response = await axios.get<Bond[]>(`${API_URL}/portfolio/bonds`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data
}

/**
 * Get a single bond by ID.
 *
 * @param token - Authentication token
 * @param bondId - Bond ID
 * @returns Bond data
 */
export async function getBond(token: string, bondId: number): Promise<Bond> {
  const response = await axios.get<Bond>(`${API_URL}/portfolio/bonds/${bondId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data
}

/**
 * Get bond analysis with value projections.
 *
 * @param token - Authentication token
 * @param bondId - Bond ID
 * @returns Bond analysis data
 */
export async function getBondAnalysis(
  token: string,
  bondId: number,
): Promise<BondAnalysis> {
  const response = await axios.get<BondAnalysis>(
    `${API_URL}/portfolio/bonds/${bondId}/analysis`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )
  return response.data
}

/**
 * Get bonds portfolio summary.
 *
 * @param token - Authentication token
 * @returns Portfolio summary data
 */
export async function getBondsPortfolioSummary(
  token: string,
): Promise<BondsPortfolioSummary> {
  const response = await axios.get<BondsPortfolioSummary>(
    `${API_URL}/portfolio/bonds/portfolio/summary`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )
  return response.data
}


/**
 * Update an existing bond.
 *
 * @param token - Authentication token
 * @param bondId - Bond ID
 * @param bondData - Partial bond update data
 * @returns Updated bond response
 */
export async function updateBond(
  token: string,
  bondId: number,
  bondData: BondUpdate,
): Promise<Bond> {
  const response = await axios.put<Bond>(
    `${API_URL}/portfolio/bonds/${bondId}`,
    bondData,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  )
  return response.data
}

/**
 * Delete a bond by ID.
 *
 * @param token - Authentication token
 * @param bondId - Bond ID to delete
 */
export async function deleteBond(token: string, bondId: number): Promise<void> {
  await axios.delete(`${API_URL}/portfolio/bonds/${bondId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}
