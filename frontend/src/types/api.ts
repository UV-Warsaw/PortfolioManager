/**
 * API type definitions.
 */

// Authentication
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  created_at: string
  updated_at: string | null
}

// Portfolio
export interface Cash {
  id: number
  amount: number
  currency: string
  bank: string
  created_at: string
  updated_at: string | null
}

export interface CashCreate {
  amount: number
  currency: string
  bank: string
}

export interface CashUpdate {
  amount?: number
  currency?: string
  bank?: string
}

// Bonds
export interface Bond {
  id: number
  name: string
  annual_rate: number
  years: number
  capitalization: 'Annual' | 'Monthly'
  principal: number
  redemption_price: number | null
  quantity: number
  purchase_date: string
  created_at: string
  updated_at: string | null
}

export interface BondCreate {
  name: string
  annual_rate: number
  years: number
  capitalization: 'Annual' | 'Monthly'
  principal: number
  redemption_price?: number | null
  quantity?: number
  purchase_date: string
}

export interface BondUpdate {
  name?: string
  annual_rate?: number
  years?: number
  capitalization?: 'Annual' | 'Monthly'
  principal?: number
  redemption_price?: number | null
  quantity?: number
  purchase_date?: string
}

// Portfolio Summary
export interface DividendSummaryResponse {
  year: number
  total: number
}

export interface DividendTimelineResponse {
  month: number
  total: number
}

export interface TopHoldingItemSummary {
  ticker: string
  value: number
}

export interface PortfolioSummaryResponse {
  portfolio_value: number
  total_invested: number
  profit: number
  profit_percentage: number
  top_holdings: TopHoldingItemSummary[]
}
