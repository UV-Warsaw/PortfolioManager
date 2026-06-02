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
