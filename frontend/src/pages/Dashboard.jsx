import { Link } from 'react-router-dom'

export default function Dashboard() {
  const cards = [
    { label: 'Total', value: 0 },
    { label: 'Clôturées', value: 0 },
    { label: 'En retard', value: 0 },
    { label: 'En cours', value: 0 },
  ]
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        {cards.map((c) => (
          <div key={c.label} className="rounded-2xl shadow p-4 text-center">
            <p className="text-sm">{c.label}</p>
            <p className="text-2xl font-bold">{c.value}</p>
          </div>
        ))}
      </div>
      <div className="text-right">
        <Link to="/actions" className="text-blue-600">
          Voir actions
        </Link>
      </div>
    </div>
  )
}
