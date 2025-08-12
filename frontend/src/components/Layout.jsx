import { Link, Outlet } from 'react-router-dom'
import { logout } from '../lib/api.js'
import useRole from '../hooks/useRole.js'

export default function Layout() {
  const { user, hasRole, can } = useRole()

  return (
    <>
      <nav className="bg-blue-600 text-white p-4 flex gap-4 items-center">
        <Link to="/" className="font-bold flex items-center gap-2">
          <img src="/vite.svg" alt="Logo" className="h-6 w-6" />
          PAA
        </Link>
        <Link to="/">Dashboard</Link>
        <Link to="/actions">Actions</Link>
        <Link to="/actions/assistant">Assistante</Link>
        <Link to="/plans">Plans</Link>
        {hasRole('SuperAdmin', 'PiloteProcessus', 'Pilote') && <Link to="/quality">Qualité</Link>}
        {hasRole('SuperAdmin', 'PiloteProcessus') && <Link to="/reports">Rapports</Link>}
        {can('access', 'admin') && <Link to="/admin">Admin</Link>}
        {hasRole('SuperAdmin', 'PiloteProcessus') && (
          <Link to="/admin/custom-fields">Champs personnalisés</Link>
        )}
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
