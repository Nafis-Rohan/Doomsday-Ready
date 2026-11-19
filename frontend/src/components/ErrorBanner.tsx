import { ApiError, describeError } from '../api/client'

interface Props {
  error: unknown
}

export default function ErrorBanner({ error }: Props) {
  if (!error) return null

  const cycle =
    error instanceof ApiError &&
    error.code === 'CIRCULAR_DEPENDENCY' &&
    Array.isArray(error.details.cycle)
      ? (error.details.cycle as string[])
      : null

  return (
    <div className="error-banner" role="alert">
      <div>{describeError(error)}</div>
      {cycle && <div className="muted">Loop: {cycle.join(' → ')}</div>}
    </div>
  )
}