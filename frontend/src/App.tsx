import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import BookingPage from './pages/BookingPage'
import MoviesPage from './pages/MoviesPage'
import RewatchPlanPage from './pages/RewatchPlanPage'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <span className="app-title">Doomsday Ready</span>
        <nav className="app-nav">
          <NavLink to="/movies">Movies</NavLink>
          <NavLink to="/rewatch">Rewatch Plan</NavLink>
          <NavLink to="/booking">Booking</NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/movies" replace />} />
          <Route path="/movies" element={<MoviesPage />} />
          <Route path="/rewatch" element={<RewatchPlanPage />} />
          <Route path="/booking" element={<BookingPage />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </div>
  )
}