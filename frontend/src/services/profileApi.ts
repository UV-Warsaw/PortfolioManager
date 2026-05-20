// API client for profile endpoints.

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface ProfileResponse {
  id: number
  email: string
  risk_level: string
  monthly_expenses: number
  created_at: string | null
}

export interface UpdateEmailRequest {
  current_password: string
  new_email: string
}

export interface UpdatePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface UpdateProfileSettingsRequest {
  risk_level?: string
  monthly_expenses?: number
}

export interface UpdateSettingsResponse {
  message: string
  profile: ProfileResponse
}

export class ProfileApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ProfileApiError'
  }
}

async function request<T>(path: string, token: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers ?? {}),
    },
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ProfileApiError(res.status, body.detail ?? 'Request failed')
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json() as Promise<T>
}

export async function getProfile(token: string): Promise<ProfileResponse> {
  return request<ProfileResponse>('/profile', token)
}

export async function updateEmail(
  token: string,
  data: UpdateEmailRequest,
): Promise<ProfileResponse> {
  return request<ProfileResponse>('/profile/email', token, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function updatePassword(
  token: string,
  data: UpdatePasswordRequest,
): Promise<void> {
  return request<void>('/profile/password', token, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function updateProfileSettings(
  token: string,
  data: UpdateProfileSettingsRequest,
): Promise<UpdateSettingsResponse> {
  return request<UpdateSettingsResponse>('/profile/settings', token, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}
