import { Link, Navigate, useLocation } from 'react-router-dom'
import './auth.css'

function WelcomePage() {
  const { state } = useLocation()
  const username = state?.username

  if (typeof username !== 'string') return <Navigate to="/login" replace />

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="welcome-heading">
        <p className="auth-brand">mémoire</p>
        <h1 id="welcome-heading">Welcome, {username}!</h1>
        <p>You signed in successfully. Your memories will appear here.</p>
        <Link to="/login" replace>Back to login</Link>
      </section>
    </main>
  )
}

export default WelcomePage
