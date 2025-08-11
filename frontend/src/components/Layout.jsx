import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  return (
    <>
      <nav className="bg-blue-600 text-white p-4 flex gap-4">
        <Link to="/" className="font-bold">PAA</Link>
        <Link to="/">Dashboard</Link>
        <Link to="/actions">Actions</Link>
        <Link to="/plans">Plans</Link>
        <Link to="/admin">Admin</Link>
      </nav>
      <main className="max-w-7xl mx-auto p-4">
        {children}
      </main>
    </>
  )
}
