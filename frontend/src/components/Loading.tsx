/**
 * Loading component for displaying loading spinners.
 */

import React from 'react'

export const Loading: React.FC = () => {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" stroke="currentColor" className="text-indigo-600">
            <circle cx="20" cy="20" r="18" opacity="0.1" />
            <path d="M 20 2 A 18 18 0 0 1 35.12 6.88" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
        <p className="text-gray-600 text-sm font-medium">Loading...</p>
      </div>
    </div>
  )
}
