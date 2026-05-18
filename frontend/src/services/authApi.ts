// API client for authentication endpoints.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface RegisterRequest {
  email: string
  password: string
}

export interface RegisterResponse {
  id: number
  email: string
  access_token: string
  token_type: string
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function registerUser(data: RegisterRequest): Promise<RegisterResponse> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(res.status, body.detail ?? 'Registration failed')
  }

  return res.json() as Promise<RegisterResponse>
}
