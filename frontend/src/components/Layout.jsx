import { Link, Outlet } from 'react-router-dom'
import { logout, getEffectiveMenu } from '../lib/api.js'
import useRole from '../hooks/useRole.js'
import { useEffect, useState } from 'react'

export default function Layout() {
  const { user } = useRole()
  const [menu, setMenu] = useState([])

  useEffect(() => {
    getEffectiveMenu()
      .then((d) => setMenu(d.items))
      .catch(() => setMenu([{ label: 'Dashboard', path: '/' }, { label: 'Actions', path: '/actions' }]))
  }, [])

  return (
    <>
      <nav className="bg-blue-600 text-white p-4 flex gap-4 items-center">
        <Link to="/" className="font-bold flex items-center gap-2">
          <img src="/vite.svg" alt="Logo" className="h-6 w-6" />
          PAA
        </Link>
        {menu.map((m) => (
          <Link key={m.key} to={m.path}>
            {m.label}
          </Link>
        ))}
        <div className="ml-auto flex items-center gap-4">
          {user && <span>{user.username}</span>}
          <button onClick={logout} className="rounded-2xl px-3 py-1 bg-red-500 text-white">Déconnexion</button>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto p-4">
        <Outlet />
      </main>
    </>
  )
}
