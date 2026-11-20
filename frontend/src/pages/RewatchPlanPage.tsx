import { CheckCircle2, Circle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getRewatchOrder, listMovies, updateMovie } from '../api/movies'
import ErrorBanner from '../components/ErrorBanner'
import type { Movie, RewatchMovie, RewatchOrder } from '../types'
import { formatRuntime } from '../utils/formatRuntime'

function withWatched(
  plan: RewatchOrder,
  movieId: number,
  watched: boolean,
): RewatchOrder {
  const order = plan.order.map((m) =>
    m.id === movieId ? { ...m, watched } : m,
  )
  const unwatched = order.filter((m) => !m.watched)
  return {
    ...plan,
    order,
    watchedCount: order.length - unwatched.length,
    unwatchedCount: unwatched.length,
    remainingRuntimeMinutes: unwatched.reduce(
      (sum, m) => sum + m.runtimeMinutes,
      0,
    ),
  }
}

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

  async function toggleWatched(movie: RewatchMovie) {
    if (!plan) return
    setError(null)
    const previous = plan
    const watched = !movie.watched

    // Show the change right away; undo it if the server says no.
    setPlan(withWatched(plan, movie.id, watched))
    try {
      await updateMovie(movie.id, { watched })
    } catch (err) {
      setError(err)
      setPlan(previous)
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
          <p style={{ margin: '0 0 6px' }}>
            <strong>
              {visiblePlan.watchedCount} of {visiblePlan.totalCount} watched
            </strong>
          </p>
          <progress
            className="rewatch-progress"
            value={visiblePlan.watchedCount}
            max={visiblePlan.totalCount}
            aria-label={`${visiblePlan.watchedCount} of ${visiblePlan.totalCount} prerequisites watched`}
          />
          <p className="muted">
            {visiblePlan.unwatchedCount === 0
              ? `All caught up. You're ready for ${visiblePlan.target.title}!`
              : `${formatRuntime(visiblePlan.remainingRuntimeMinutes)} of watching left before ${visiblePlan.target.title}`}
          </p>

          <ol className="rewatch-list">
            {visiblePlan.order.map((movie) => (
              <li key={movie.id}>
                <div className="rewatch-row">
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => toggleWatched(movie)}
                    aria-pressed={movie.watched}
                    aria-label={
                      movie.watched
                        ? `Mark ${movie.title} as not watched`
                        : `Mark ${movie.title} as watched`
                    }
                  >
                    {movie.watched ? (
                      <CheckCircle2 size={22} color="#1a8f4a" />
                    ) : (
                      <Circle size={22} />
                    )}
                  </button>
                  <span className={movie.watched ? 'watched-title' : undefined}>
                    {movie.title}
                  </span>
                  <span className="muted">
                    ({movie.releaseYear}, {formatRuntime(movie.runtimeMinutes)})
                  </span>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}