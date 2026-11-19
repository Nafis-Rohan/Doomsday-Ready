import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getRewatchOrder, listMovies } from '../api/movies'
import ErrorBanner from '../components/ErrorBanner'
import type { Movie, RewatchOrder } from '../types'
import { formatRuntime } from '../utils/formatRuntime'

export default function RewatchPlanPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const targetId = Number(searchParams.get('target')) || null

  const [movies, setMovies] = useState<Movie[]>([])
  const [plan, setPlan] = useState<RewatchOrder | null>(null)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    listMovies().then(setMovies).catch(setError)
  }, [])

  useEffect(() => {
    if (targetId === null) return
    let ignore = false
    getRewatchOrder(targetId)
      .then((result) => {
        if (!ignore) setPlan(result)
      })
      .catch((err) => {
        if (!ignore) setError(err)
      })
    return () => {
      ignore = true
    }
  }, [targetId])

  function handleSelect(value: string) {
    setError(null)
    if (value === '') {
      setSearchParams({})
    } else {
      setSearchParams({ target: value })
    }
  }

  const visiblePlan = plan && plan.target.id === targetId ? plan : null
  const loading = targetId !== null && visiblePlan === null && error === null

  return (
    <div>
      <div className="page-header">
        <h1>Rewatch Plan</h1>
      </div>

      <ErrorBanner error={error} />

      <div className="field" style={{ maxWidth: 360, marginBottom: 20 }}>
        <label htmlFor="target-movie">I want to watch</label>
        <select
          id="target-movie"
          value={targetId ?? ''}
          onChange={(e) => handleSelect(e.target.value)}
        >
          <option value="">Choose a movie…</option>
          {movies.map((movie) => (
            <option key={movie.id} value={movie.id}>
              {movie.title} ({movie.releaseYear})
            </option>
          ))}
        </select>
      </div>

      {targetId === null && (
        <p className="muted">Pick a movie to see what to watch before it.</p>
      )}

      {loading && <p className="muted">Loading plan…</p>}

      {visiblePlan && visiblePlan.order.length === 0 && (
        <p className="muted">
          Nothing to rewatch: {visiblePlan.target.title} has no prerequisites.
        </p>
      )}

      {visiblePlan && visiblePlan.order.length > 0 && (
        <div className="card">
          <p className="muted">
            {visiblePlan.watchedCount} of {visiblePlan.totalCount} watched ·{' '}
            {formatRuntime(visiblePlan.remainingRuntimeMinutes)} left
          </p>
          <ol>
            {visiblePlan.order.map((movie) => (
              <li key={movie.id}>
                <span className={movie.watched ? 'watched-title' : undefined}>
                  {movie.title}
                </span>{' '}
                <span className="muted">
                  ({movie.releaseYear}, {formatRuntime(movie.runtimeMinutes)})
                </span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}