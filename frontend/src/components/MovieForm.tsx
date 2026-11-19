import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../api/client'
import { createMovie } from '../api/movies'
import type { Movie } from '../types'
import ErrorBanner from './ErrorBanner'
import PrerequisitePicker from './PrerequisitePicker'

interface Props {
  movies: Movie[]
  onCreated: (movie: Movie) => void
  onCancel: () => void
}

/** Turn a VALIDATION_ERROR response into {field name: message}. */
function fieldMessages(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || error.code !== 'VALIDATION_ERROR') {
    return {}
  }
  const messages: Record<string, string> = {}
  for (const [field, value] of Object.entries(error.details)) {
    messages[field] = Array.isArray(value)
      ? value.join(' ')
      : typeof value === 'string'
        ? value
        : 'Invalid value.'
  }
  return messages
}

export default function MovieForm({ movies, onCreated, onCancel }: Props) {
  const [title, setTitle] = useState('')
  const [releaseYear, setReleaseYear] = useState('')
  const [runtimeMinutes, setRuntimeMinutes] = useState('')
  const [prerequisites, setPrerequisites] = useState<number[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<unknown>(null)

  const fields = fieldMessages(error)
  const hasFieldErrors = Object.keys(fields).length > 0

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const movie = await createMovie({
        title: title.trim(),
        releaseYear: Number(releaseYear),
        runtimeMinutes: Number(runtimeMinutes),
        prerequisites,
      })
      onCreated(movie)
    } catch (err) {
      setError(err)
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error != null && !hasFieldErrors && <ErrorBanner error={error} />}

      <div className="row">
        <div className="field">
          <label htmlFor="movie-title">Title</label>
          <input
            id="movie-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            required
            autoFocus
          />
          {fields.title && <span className="field-error">{fields.title}</span>}
        </div>

        <div className="field">
          <label htmlFor="movie-year">Release year</label>
          <input
            id="movie-year"
            type="number"
            value={releaseYear}
            onChange={(e) => setReleaseYear(e.target.value)}
            min={1900}
            max={2100}
            required
          />
          {fields.releaseYear && (
            <span className="field-error">{fields.releaseYear}</span>
          )}
        </div>

        <div className="field">
          <label htmlFor="movie-runtime">Runtime (minutes)</label>
          <input
            id="movie-runtime"
            type="number"
            value={runtimeMinutes}
            onChange={(e) => setRuntimeMinutes(e.target.value)}
            min={1}
            max={300}
            required
          />
          {fields.runtimeMinutes && (
            <span className="field-error">{fields.runtimeMinutes}</span>
          )}
        </div>
      </div>

      <div className="field" style={{ marginTop: 12 }}>
        <label>Watch these first (optional)</label>
        <PrerequisitePicker
          movies={movies}
          selected={prerequisites}
          onChange={setPrerequisites}
          disabled={submitting}
        />
      </div>

      <div className="modal-actions">
        <button type="button" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Adding…' : 'Add movie'}
        </button>
      </div>
    </form>
  )
}