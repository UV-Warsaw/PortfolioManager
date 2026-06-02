/**
 * API service for Bond endpoints.
 */

import axios from 'axios'
import type { Bond, BondCreate, BondUpdate } from '../types/api'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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
