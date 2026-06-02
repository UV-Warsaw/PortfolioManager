/**
 * ErrorDisplay component for showing error messages.
 */

import React from 'react'

interface ErrorDisplayProps {
  error?: string
  message?: string
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, message }) => {
  const text = message || error || 'An unknown error occurred'
  
  return (
    <div
      style={{
        background: 'rgba(248, 113, 113, 0.12)',
        color: '#f87171',
        borderRadius: '12px',
        padding: '12px 16px',
        marginBottom: '16px',
        border: '1px solid rgba(248, 113, 113, 0.3)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
        <div>
          <p style={{ fontWeight: '600', marginBottom: '4px' }}>Error</p>
          <p style={{ fontSize: '13px' }}>{text}</p>
        </div>
      </div>
    </div>
  )
}
