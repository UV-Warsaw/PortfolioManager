/**
 * API service for Cash Account endpoints.
 */

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type CashAccountType =
  | 'Savings'
  | 'Checking'
  | 'High-Yield Savings'
  | 'Money Market'
  | 'Cash'
  | 'Other'

export interface CashAccount {
  id: number
  name: string
  account_type: CashAccountType
  balance: number
  interest_rate: number | null
  bank_name: string | null
  currency: string
  created_at: string
  updated_at: string | null
}

export interface CashCreate {
  name: string
  account_type: CashAccountType
  balance: number
  interest_rate?: number | null
  bank_name?: string | null
  currency?: string
}

export interface CashUpdate {
  name?: string
  account_type?: CashAccountType
  balance?: number
  interest_rate?: number | null
  bank_name?: string | null
  currency?: string
}

export interface CashAnalysis {
  account_id: number
  name: string
  balance: number
  annual_interest: number
  monthly_interest: number
  daily_interest: number
}

export interface CashPortfolioSummary {
  total_balance: number
  total_annual_interest: number
  total_monthly_interest: number
  weighted_avg_interest_rate: number
  accounts_count: number
  accounts_by_type: Record<string, { count: number; total_balance: number }>
}

const authHeaders = (token: string) => ({ Authorization: `Bearer ${token}` })

export async function getCashAccounts(token: string): Promise<CashAccount[]> {
  const res = await axios.get(`${API_URL}/portfolio/cash`, { headers: authHeaders(token) })
  return res.data
}

export async function getCashAccount(token: string, id: number): Promise<CashAccount> {
  const res = await axios.get(`${API_URL}/portfolio/cash/${id}`, { headers: authHeaders(token) })
  return res.data
}

export async function getCashAnalysis(token: string, id: number): Promise<CashAnalysis> {
  const res = await axios.get(`${API_URL}/portfolio/cash/${id}/analysis`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function getCashPortfolioSummary(token: string): Promise<CashPortfolioSummary> {
  const res = await axios.get(`${API_URL}/portfolio/cash/summary`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function createCashAccount(token: string, data: CashCreate): Promise<CashAccount> {
  const res = await axios.post(`${API_URL}/portfolio/cash`, data, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function updateCashAccount(
  token: string,
  id: number,
  data: CashUpdate,
): Promise<CashAccount> {
  const res = await axios.put(`${API_URL}/portfolio/cash/${id}`, data, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function deleteCashAccount(token: string, id: number): Promise<void> {
  await axios.delete(`${API_URL}/portfolio/cash/${id}`, { headers: authHeaders(token) })
}
