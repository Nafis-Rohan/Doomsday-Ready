import { Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { listMovies, updateMovie } from '../api/movies'
import ErrorBanner from '../components/ErrorBanner'
import Modal from '../components/Modal'
import MovieCard from '../components/MovieCard'
import MovieForm from '../components/MovieForm'
import PrerequisiteEditor from '../components/PrerequisiteEditor'
import type { Movie } from '../types'

function sortMovies(movies: Movie[]): Movie[] {
  return [...movies].sort(
    (a, b) => a.releaseYear - b.releaseYear || a.title.localeCompare(b.title),
  )
}

export default function MoviesPage() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [adding, setAdding] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  useEffect(() => {
    listMovies()
      .then(setMovies)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  async function toggleWatched(movie: Movie) {
    setError(null)
    const watched = !movie.watched

    // Show the change right away; undo it if the server says no.
    setMovies((current) =>
      current.map((m) => (m.id === movie.id ? { ...m, watched } : m)),
    )
    try {
      const saved = await updateMovie(movie.id, { watched })
      setMovies((current) => current.map((m) => (m.id === saved.id ? saved : m)))
    } catch (err) {
      setError(err)
      setMovies((current) =>
        current.map((m) =>
          m.id === movie.id ? { ...m, watched: movie.watched } : m,
        ),
      )
    }
  }

  function handleCreated(movie: Movie) {
    setMovies((current) => sortMovies([...current, movie]))
    setAdding(false)
  }

  function handleEdited(saved: Movie) {
    setMovies((current) => current.map((m) => (m.id === saved.id ? saved : m)))
    setEditingId(null)
  }

  const editing = movies.find((movie) => movie.id === editingId)

  return (
    <div>
      <div className="page-header">
        <h1>Movies</h1>
        <button type="button" onClick={() => setAdding(true)}>
          <Plus size={16} style={{ verticalAlign: '-3px' }} /> Add movie
        </button>
      </div>

      <ErrorBanner error={error} />

      {loading ? (
        <p className="muted">Loading movies…</p>
      ) : movies.length === 0 ? (
        <p className="muted">No movies yet. Click “Add movie” to create one.</p>
      ) : (
        <div className="movie-grid">
          {movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onToggleWatched={toggleWatched}
              onEdit={(m) => setEditingId(m.id)}
            />
          ))}
        </div>
      )}

      {adding && (
        <Modal title="Add a movie" onClose={() => setAdding(false)}>
          <MovieForm
            movies={movies}
            onCreated={handleCreated}
            onCancel={() => setAdding(false)}
          />
        </Modal>
      )}

      {editing && (
        <Modal
          title={`Edit prerequisites: ${editing.title}`}
          onClose={() => setEditingId(null)}
        >
          <PrerequisiteEditor
            key={editing.id}
            movie={editing}
            movies={movies}
            onSaved={handleEdited}
            onCancel={() => setEditingId(null)}
          />
        </Modal>
      )}
    </div>
  )
}