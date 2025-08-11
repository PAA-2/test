import { Link } from 'react-router-dom'

export default function AdminIndex() {
  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Admin</h2>
      <ul className="list-disc pl-5 space-y-2">
        <li>
          <Link className="text-blue-600" to="/admin/custom-fields">
            Champs personnalisés
          </Link>
        </li>
      </ul>
    </div>
  )
}
