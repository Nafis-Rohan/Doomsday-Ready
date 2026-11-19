import { useState } from 'react'
import { updateMovie } from '../api/movies'
import type { Movie } from '../types'
import ErrorBanner from './ErrorBanner'
import PrerequisitePicker from './PrerequisitePicker'

interface Props {
  movie: Movie
  movies: Movie[]
  onSaved: (movie: Movie) => void
  onCancel: () => void
}

export default function PrerequisiteEditor({
  movie,
  movies,
  onSaved,
  onCancel,
}: Props) {
  const [selected, setSelected] = useState<number[]>(
    movie.prerequisites.map((prereq) => prereq.id),
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<unknown>(null)

  async function save() {
    setError(null)
    setSaving(true)
    try {
      const saved = await updateMovie(movie.id, { prerequisites: selected })
      onSaved(saved)
    } catch (err) {
      setError(err)
      setSaving(false)
    }
  }

  return (
    <div>
      <p className="muted">Pick the movies to watch before {movie.title}.</p>
      <ErrorBanner error={error} />

      <PrerequisitePicker
        movies={movies}
        selected={selected}
        onChange={setSelected}
        excludeId={movie.id}
        disabled={saving}
      />

      <div className="modal-actions">
        <button
          type="button"
          className="secondary"
          onClick={onCancel}
          disabled={saving}
        >
          Cancel
        </button>
        <button type="button" onClick={save} disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
    </div>
  )
}