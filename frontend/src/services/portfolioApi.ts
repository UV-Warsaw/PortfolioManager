const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface PortfolioValueResponse {
  accounts: Record<string, number>
  total: number
  profit_data?: Record<string, {
    market_value: number
    cost_basis: number
    profit: number
    profit_percentage: number
  }>
}

export async function getPortfolioValue(token: string): Promise<PortfolioValueResponse> {
  const res = await fetch(`${API_URL}/portfolio/value`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch portfolio value: ${res.status}`)
  }
  return res.json() as Promise<PortfolioValueResponse>
}

export interface TopHoldingItem {
  ticker: string
  cost_basis: number
}

export interface TopHoldingsResponse {
  items: TopHoldingItem[]
}

export async function getTopHoldings(token: string): Promise<TopHoldingsResponse> {
  const res = await fetch(`${API_URL}/portfolio/top-holdings`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch top holdings: ${res.status}`)
  }
  return res.json() as Promise<TopHoldingsResponse>
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

export async function getDashboardSummary(
  token: string,
  account?: string,
): Promise<PortfolioSummaryResponse> {
  const params = new URLSearchParams()
  if (account) {
    params.append('account', account)
  }
  const res = await fetch(`${API_URL}/summary/dashboard?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard summary: ${res.status}`)
  }
  return res.json() as Promise<PortfolioSummaryResponse>
}

export interface DividendSummaryResponse {
  year: number
  total: number
}

export async function getDividendYearlySummary(
  token: string,
  account?: string,
): Promise<DividendSummaryResponse[]> {
  const params = new URLSearchParams()
  if (account) {
    params.append('account', account)
  }
  const res = await fetch(`${API_URL}/summary/dividends/yearly?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch dividend summary: ${res.status}`)
  }
  return res.json() as Promise<DividendSummaryResponse[]>
}

export interface DividendTimelineResponse {
  month: number
  total: number
}

export async function getDividendTimeline(
  token: string,
  year?: number,
  account?: string,
): Promise<DividendTimelineResponse[]> {
  const params = new URLSearchParams()
  if (year) {
    params.append('year', String(year))
  }
  if (account) {
    params.append('account', account)
  }
  const res = await fetch(`${API_URL}/summary/dividends/timeline?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch dividend timeline: ${res.status}`)
  }
  return res.json() as Promise<DividendTimelineResponse[]>
}
