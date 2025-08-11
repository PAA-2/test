import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { getCurrentUser, logout } from '../lib/api.js'

export default function Layout() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => {})
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <>
      <nav className="bg-blue-600 text-white p-4 flex gap-4 items-center">
        <Link to="/" className="font-bold">PAA</Link>
        <Link to="/">Dashboard</Link>
        <Link to="/actions">Actions</Link>
        <Link to="/plans">Plans</Link>
        <Link to="/admin">Admin</Link>
        <div className="ml-auto flex items-center gap-4">
          {user && <span>{user.username}</span>}
          <button onClick={handleLogout} className="rounded-2xl px-3 py-1 bg-red-500 text-white">Déconnexion</button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto p-4">
        <Outlet />
      </main>
    </>
  )
}
