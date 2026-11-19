import { Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { getBookingQuote, listCinemas } from '../api/cinemas'
import CinemaForm from '../components/CinemaForm'
import ErrorBanner from '../components/ErrorBanner'
import Modal from '../components/Modal'
import type { BookingQuote, Cinema } from '../types'

function sizesLabel(cinema: Cinema): string {
  return [...cinema.bundleSizes].sort((a, b) => a - b).join(', ')
}

export default function BookingPage() {
  const [cinemas, setCinemas] = useState<Cinema[]>([])
  const [loading, setLoading] = useState(true)
  const [cinemaId, setCinemaId] = useState<number | null>(null)
  const [groupSize, setGroupSize] = useState('')
  const [quote, setQuote] = useState<BookingQuote | null>(null)
  const [quoting, setQuoting] = useState(false)
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    listCinemas()
      .then(setCinemas)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  const cinema = cinemas.find((c) => c.id === cinemaId) ?? cinemas[0]

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!cinema) return
    setError(null)
    setQuote(null)
    setQuoting(true)
    try {
      setQuote(await getBookingQuote(cinema.id, Number(groupSize)))
    } catch (err) {
      setError(err)
    } finally {
      setQuoting(false)
    }
  }

  function handleCreated(created: Cinema) {
    setCinemas((current) => [...current, created])
    setCinemaId(created.id)
    setQuote(null)
    setAdding(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1>Booking</h1>
        <button type="button" onClick={() => setAdding(true)}>
          <Plus size={16} style={{ verticalAlign: '-3px' }} /> Add cinema
        </button>
      </div>

      <ErrorBanner error={error} />

      {loading ? (
        <p className="muted">Loading cinemas…</p>
      ) : !cinema ? (
        <p className="muted">No cinemas yet. Click “Add cinema” to create one.</p>
      ) : (
        <form className="card" onSubmit={handleSubmit}>
          <div className="row">
            <div className="field">
              <label htmlFor="cinema">Cinema</label>
              <select
                id="cinema"
                value={cinema.id}
                onChange={(e) => {
                  setCinemaId(Number(e.target.value))
                  setQuote(null)
                }}
              >
                {cinemas.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <span className="muted">Bundle sizes: {sizesLabel(cinema)}</span>
            </div>

            <div className="field">
              <label htmlFor="group-size">Group size</label>
              <input
                id="group-size"
                type="number"
                value={groupSize}
                onChange={(e) => {
                  setGroupSize(e.target.value)
                  setQuote(null)
                }}
                min={1}
                max={10000}
                step={1}
                required
              />
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <button type="submit" disabled={quoting}>
              {quoting ? 'Working it out…' : 'Get quote'}
            </button>
          </div>
        </form>
      )}

      <div aria-live="polite">
        {quote && quote.possible && (
          <div className="card">
            <h2 style={{ marginTop: 0 }}>
              {quote.totalBundles} {quote.totalBundles === 1 ? 'bundle' : 'bundles'}
            </h2>
            <p className="muted">
              Fewest bundles for a group of {quote.groupSize} at{' '}
              {quote.cinema.name}:
            </p>
            <div className="chips">
              {quote.bundles.map((bundle) => (
                <span key={bundle.size} className="chip">
                  {bundle.count} × {bundle.size}
                </span>
              ))}
            </div>
          </div>
        )}

        {quote && !quote.possible && (
          <div className="card">
            <h2 style={{ marginTop: 0 }}>Not possible</h2>
            <p className="muted">
              {quote.message ??
                `${quote.cinema.name} can't seat exactly ${quote.groupSize} people with its bundle sizes.`}
            </p>
          </div>
        )}
      </div>

      {adding && (
        <Modal title="Add a cinema" onClose={() => setAdding(false)}>
          <CinemaForm
            onCreated={handleCreated}
            onCancel={() => setAdding(false)}
          />
        </Modal>
      )}
    </div>
  )
}