import React, { useRef, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type AccountType = 'IKE' | 'PLN' | 'USD'

interface ImportResult {
  imported_transactions: number
  imported_dividends: number
  account: string
}

interface Props {
  token: string
}

const ImportForm: React.FC<Props> = ({ token }) => {
  const [account, setAccount] = useState<AccountType>('PLN')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ImportResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResult(null)
    setError(null)
    setFile(e.target.files?.[0] ?? null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Wybierz plik Excel (.xlsx lub .xls)')
      return
    }

    const fname = file.name.toLowerCase()
    if (!fname.endsWith('.xlsx') && !fname.endsWith('.xls')) {
      setError('Nieobsługiwany format pliku. Wybierz plik .xlsx lub .xls')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    const form = new FormData()
    form.append('file', file)
    form.append('account', account)

    try {
      const res = await fetch(`${API_URL}/portfolio/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail ?? `Błąd serwera: ${res.status}`)
      }

      const data: ImportResult = await res.json()
      setResult(data)
      setFile(null)
      if (fileRef.current) fileRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nieznany błąd')
    } finally {
      setLoading(false)
    }
  }

  const accountOptions: AccountType[] = ['PLN', 'IKE', 'USD']

  return (
    <div
      className="rounded-xl p-5"
      style={{
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <h2 className="text-sm font-semibold mb-4" style={{ color: 'var(--text)' }}>
        Import z XTB
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Account type selector */}
        <div>
          <label className="block text-xs mb-1" style={{ color: 'var(--muted)' }}>
            Typ konta
          </label>
          <div className="flex gap-2">
            {accountOptions.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setAccount(opt)}
                className="flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all"
                style={{
                  background:
                    account === opt
                      ? 'var(--accent)'
                      : 'rgba(99,102,241,0.08)',
                  color: account === opt ? '#fff' : '#a5b4fc',
                  border:
                    account === opt
                      ? '1px solid var(--accent)'
                      : '1px solid rgba(99,102,241,0.2)',
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        {/* File picker */}
        <div>
          <label className="block text-xs mb-1" style={{ color: 'var(--muted)' }}>
            Plik Excel (.xlsx / .xls)
          </label>
          <input
            ref={fileRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="w-full text-xs rounded-lg px-3 py-2 cursor-pointer"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'var(--muted)',
            }}
          />
          {file && (
            <p className="mt-1 text-xs truncate" style={{ color: 'var(--muted)' }}>
              {file.name}
            </p>
          )}
        </div>

        {/* Error */}
        {error !== null && (
          <p
            className="text-xs rounded-lg px-3 py-2"
            style={{
              background: 'rgba(239,68,68,0.08)',
              border: '1px solid rgba(239,68,68,0.25)',
              color: '#f87171',
            }}
          >
            {error}
          </p>
        )}

        {/* Success */}
        {result !== null && (
          <div
            className="text-xs rounded-lg px-3 py-2 space-y-0.5"
            style={{
              background: 'rgba(16,185,129,0.08)',
              border: '1px solid rgba(16,185,129,0.25)',
              color: '#6ee7b7',
            }}
          >
            <p>Zaimportowano pomyślnie ({result.account})</p>
            <p>Transakcje: {result.imported_transactions}</p>
            <p>Dywidendy: {result.imported_dividends}</p>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || file === null}
          className="w-full rounded-lg py-2 text-sm font-semibold transition-opacity
            focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500
            disabled:opacity-40"
          style={{ background: 'var(--accent)', color: '#fff' }}
        >
          {loading ? 'Importowanie…' : 'Importuj plik'}
        </button>
      </form>
    </div>
  )
}

export default ImportForm
