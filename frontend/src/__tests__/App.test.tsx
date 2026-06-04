import React from 'react'
import { act, render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import App from '../App'

vi.mock('../components/LoginForm', () => ({
  default: () => React.createElement('div', { 'data-testid': 'login-form' }),
}))
vi.mock('../components/RegisterForm', () => ({
  default: () => React.createElement('div', { 'data-testid': 'register-form' }),
}))
vi.mock('../components/ForgotPasswordForm', () => ({
  default: () => React.createElement('div', { 'data-testid': 'forgot-password-form' }),
}))
vi.mock('../components/ImportForm', () => ({
  default: () => React.createElement('div', { 'data-testid': 'import-form' }),
}))
vi.mock('../components/ProfileForm', () => ({
  default: () => React.createElement('div', { 'data-testid': 'profile-form' }),
}))
vi.mock('../services/authApi', () => ({
  getMe: vi.fn(),
  logoutUser: vi.fn(),
}))

import { getMe } from '../services/authApi'

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: true } as Response),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.clearAllMocks()
  })

  describe('unauthenticated', () => {
    it('renders the app title and login form when no token is stored', async () => {
      await act(async () => { render(<App />) })
      expect(screen.getByText('Portfolio Manager')).toBeInTheDocument()
      expect(screen.getByTestId('login-form')).toBeInTheDocument()
    })

    it('shows Sign in subtitle on initial render', async () => {
      await act(async () => { render(<App />) })
      expect(screen.getByText('Sign in')).toBeInTheDocument()
    })

    it('does not render the topbar nav when unauthenticated', async () => {
      await act(async () => { render(<App />) })
      expect(screen.queryByRole('navigation')).toBeNull()
    })
  })

  describe('authenticated', () => {
    it('renders the app shell with Stocks tab after token is validated', async () => {
      vi.mocked(getMe).mockResolvedValueOnce({ id: 1, email: 'trader@example.com' })
      localStorage.setItem('access_token', 'valid-token')

      render(<App />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Stocks/i })).toBeInTheDocument()
      })
      expect(screen.getByTestId('import-form')).toBeInTheDocument()
    })

    it('displays the authenticated user email in the topbar', async () => {
      vi.mocked(getMe).mockResolvedValueOnce({ id: 1, email: 'trader@example.com' })
      localStorage.setItem('access_token', 'valid-token')

      render(<App />)

      await waitFor(() => {
        expect(screen.getByText('trader@example.com')).toBeInTheDocument()
      })
    })

    it('renders Crypto and Real Estate tabs as enabled', async () => {
      vi.mocked(getMe).mockResolvedValueOnce({ id: 1, email: 'trader@example.com' })
      localStorage.setItem('access_token', 'valid-token')

      render(<App />)

      await waitFor(() => {
        expect(screen.getByText('Crypto')).toBeInTheDocument()
      })
      const cryptoBtn = screen.getByText('Crypto').closest('button')
      expect(cryptoBtn).not.toBeDisabled()

      const realEstateBtn = screen.getByText('Real Estate').closest('button')
      expect(realEstateBtn).not.toBeDisabled()
    })

    it('falls back to login and clears token when getMe returns an error', async () => {
      vi.mocked(getMe).mockRejectedValueOnce(new Error('401 Unauthorized'))
      localStorage.setItem('access_token', 'expired-token')

      render(<App />)

      await waitFor(() => {
        expect(screen.getByTestId('login-form')).toBeInTheDocument()
      })
      expect(localStorage.getItem('access_token')).toBeNull()
    })
  })
})
