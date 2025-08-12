import { Navigate, Outlet } from 'react-router-dom'
import Forbidden403 from '../pages/errors/Forbidden403.jsx'
import useRole from '../hooks/useRole.js'

export default function ProtectedRoute({ children, roles }) {
  const token = localStorage.getItem('token')
  const { user, hasRole } = useRole()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (!user) {
    return <div>Chargement...</div>
  }

  if (roles && !hasRole(...roles)) {
    return <Forbidden403 />
  }

  return children ? children : <Outlet />
}
