import type { Movie } from '../types'

interface Props {
  movies: Movie[]
  selected: number[]
  onChange: (ids: number[]) => void
  excludeId?: number // a movie can't be its own prerequisite
  disabled?: boolean
}

export default function PrerequisitePicker({
  movies,
  selected,
  onChange,
  excludeId,
  disabled,
}: Props) {
  const options = movies.filter((movie) => movie.id !== excludeId)

  function toggle(id: number) {
    onChange(
      selected.includes(id)
        ? selected.filter((selectedId) => selectedId !== id)
        : [...selected, id],
    )
  }

  if (options.length === 0) {
    return <p className="muted">No other movies yet.</p>
  }

  return (
    <div className="picker">
      {options.map((movie) => (
        <label key={movie.id}>
          <input
            type="checkbox"
            checked={selected.includes(movie.id)}
            disabled={disabled}
            onChange={() => toggle(movie.id)}
          />
          {movie.title} <span className="muted">({movie.releaseYear})</span>
        </label>
      ))}
    </div>
  )
}