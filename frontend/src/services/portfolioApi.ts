const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface PortfolioValueResponse {
  accounts: Record<string, number>
  total: number
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
