import { useState } from 'react'
import type { FormEvent } from 'react'
import { createCinema } from '../api/cinemas'
import type { Cinema } from '../types'
import ErrorBanner from './ErrorBanner'

interface Props {
  onCreated: (cinema: Cinema) => void
  onCancel: () => void
}

/** Turn "2, 5, 10" into [2, 5, 10], or return an error message. */
function parseSizes(text: string): { sizes: number[] } | { problem: string } {
  const parts = text.split(/[,\s]+/).filter((part) => part !== '')
  if (parts.length < 1 || parts.length > 10) {
    return { problem: 'Enter 1 to 10 bundle sizes, separated by commas.' }
  }
  const sizes = parts.map(Number)
  if (sizes.some((n) => !Number.isInteger(n) || n < 1 || n > 500)) {
    return { problem: 'Each bundle size must be a whole number from 1 to 500.' }
  }
  if (new Set(sizes).size !== sizes.length) {
    return { problem: 'Bundle sizes must all be different.' }
  }
  return { sizes }
}

export default function CinemaForm({ onCreated, onCancel }: Props) {
  const [name, setName] = useState('')
  const [sizesText, setSizesText] = useState('')
  const [sizesProblem, setSizesProblem] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<unknown>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    const parsed = parseSizes(sizesText)
    if ('problem' in parsed) {
      setSizesProblem(parsed.problem)
      return
    }
    setSizesProblem(null)

    setSubmitting(true)
    try {
      const cinema = await createCinema({
        name: name.trim(),
        bundleSizes: parsed.sizes,
      })
      onCreated(cinema)
    } catch (err) {
      setError(err)
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <ErrorBanner error={error} />

      <div className="field">
        <label htmlFor="cinema-name">Cinema name</label>
        <input
          id="cinema-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={200}
          required
          autoFocus
        />
      </div>

      <div className="field" style={{ marginTop: 12 }}>
        <label htmlFor="cinema-sizes">Bundle sizes</label>
        <input
          id="cinema-sizes"
          value={sizesText}
          onChange={(e) => setSizesText(e.target.value)}
          placeholder="e.g. 2, 5, 10"
          required
        />
        <span className="muted">
          1 to 10 different sizes, each from 1 to 500.
        </span>
        {sizesProblem && <span className="field-error">{sizesProblem}</span>}
      </div>

      <div className="modal-actions">
        <button
          type="button"
          className="secondary"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancel
        </button>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Adding…' : 'Add cinema'}
        </button>
      </div>
    </form>
  )
}