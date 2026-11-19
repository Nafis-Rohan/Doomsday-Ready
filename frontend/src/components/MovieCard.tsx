import { CheckCircle2, Circle, Pencil } from 'lucide-react'
import type { Movie } from '../types'
import { formatRuntime } from '../utils/formatRuntime'

interface Props {
  movie: Movie
  onToggleWatched: (movie: Movie) => void
  onEdit: (movie: Movie) => void
}

export default function MovieCard({ movie, onToggleWatched, onEdit }: Props) {
  return (
    <article className={movie.watched ? 'movie-card is-watched' : 'movie-card'}>
      <div className="movie-card-top">
        <h3 className={movie.watched ? 'watched-title' : undefined}>
          {movie.title}
        </h3>
        <div className="movie-card-actions">
          <button
            type="button"
            className="icon-button"
            onClick={() => onToggleWatched(movie)}
            aria-pressed={movie.watched}
            aria-label={
              movie.watched
                ? `Mark ${movie.title} as not watched`
                : `Mark ${movie.title} as watched`
            }
            title={movie.watched ? 'Watched' : 'Not watched'}
          >
            {movie.watched ? (
              <CheckCircle2 size={22} color="#1a8f4a" />
            ) : (
              <Circle size={22} />
            )}
          </button>
          <button
            type="button"
            className="icon-button"
            onClick={() => onEdit(movie)}
            aria-label={`Edit prerequisites of ${movie.title}`}
            title="Edit prerequisites"
          >
            <Pencil size={18} />
          </button>
        </div>
      </div>

      <p className="muted movie-card-meta">
        {movie.releaseYear} · {formatRuntime(movie.runtimeMinutes)}
      </p>

      <div className="movie-card-prereqs">
        <span className="muted">Watch first:</span>
        {movie.prerequisites.length === 0 ? (
          <span className="muted"> None</span>
        ) : (
          <div className="chips">
            {movie.prerequisites.map((prereq) => (
              <span key={prereq.id} className="chip">
                {prereq.title}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}