import { formatInt } from '../lib/format.js'

export default function KpiCards({ data }) {
  const items = [
    { key: 'total', label: 'Total' },
    { key: 'cloturees', label: 'Clôturées' },
    { key: 'en_retard', label: 'En retard' },
    { key: 'en_cours', label: 'En cours' },
  ]
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {items.map(({ key, label }) => (
        <div key={key} className="rounded-2xl shadow p-4 text-center">
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold">{formatInt(data?.[key])}</p>
        </div>
      ))}
    </div>
  )
}
