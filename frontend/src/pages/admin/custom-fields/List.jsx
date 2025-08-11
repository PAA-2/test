import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  listCustomFields,
  updateCustomField,
  deleteCustomField,
} from '../../../lib/api.js'
import useRole from '../../../hooks/useRole.js'
import { useToast } from '../../../components/Toast.jsx'

export default function CustomFieldsList() {
  const { hasRole } = useRole()
  const { show } = useToast()
  const [fields, setFields] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('')

  const fetchFields = () => {
    setLoading(true)
    const params = {}
    if (activeFilter !== 'all') params.active = activeFilter === 'yes'
    listCustomFields(params)
      .then((data) => setFields(data))
      .catch(() => show('Erreur chargement', 'error'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchFields()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFilter])

  const handleToggle = async (field) => {
    try {
      await updateCustomField(field.id, { active: !field.active })
      show('Champ mis à jour', 'success')
      fetchFields()
    } catch {
      show('Erreur mise à jour', 'error')
    }
  }

  const handleDelete = async (field) => {
    if (field.active) {
      show('Désactivez avant suppression', 'error')
      return
    }
    if (!confirm('Supprimer ce champ ?')) return
    try {
      await deleteCustomField(field.id)
      show('Champ supprimé', 'success')
      fetchFields()
    } catch {
      show('Erreur suppression', 'error')
    }
  }

  const filtered = typeFilter
    ? fields.filter((f) => f.type === typeFilter)
    : fields

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Champs personnalisés</h2>
        {hasRole('SuperAdmin', 'PiloteProcessus') && (
          <Link
            to="/admin/custom-fields/new"
            className="bg-blue-600 text-white rounded-2xl px-4 py-2"
          >
            Nouveau champ
          </Link>
        )}
      </div>
      <div className="flex gap-4 mb-4">
        <select
          value={activeFilter}
          onChange={(e) => setActiveFilter(e.target.value)}
          className="border p-2 rounded-xl"
        >
          <option value="all">Actif: tous</option>
          <option value="yes">Actif: oui</option>
          <option value="no">Actif: non</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border p-2 rounded-xl"
        >
          <option value="">Type: tous</option>
          <option value="text">text</option>
          <option value="number">number</option>
          <option value="date">date</option>
          <option value="select">select</option>
          <option value="tags">tags</option>
          <option value="bool">bool</option>
        </select>
      </div>
      {loading ? (
        <div className="animate-pulse space-y-2">
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
        </div>
      ) : (
        <table className="min-w-full bg-white rounded-2xl shadow">
          <thead>
            <tr className="text-left border-b">
              <th className="p-2">Nom</th>
              <th className="p-2">Clé</th>
              <th className="p-2">Type</th>
              <th className="p-2">Requis</th>
              <th className="p-2">Visibilité</th>
              <th className="p-2">Actif</th>
              <th className="p-2">Options</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((field) => (
              <tr key={field.id} className="border-b last:border-0">
                <td className="p-2">{field.name}</td>
                <td className="p-2">{field.key}</td>
                <td className="p-2">{field.type}</td>
                <td className="p-2">{field.required ? 'Oui' : 'Non'}</td>
                <td className="p-2">{field.role_visibility}</td>
                <td className="p-2">{field.active ? 'Oui' : 'Non'}</td>
                <td className="p-2">{field.options.length}</td>
                <td className="p-2 space-x-2">
                  <Link
                    to={`/admin/custom-fields/${field.id}`}
                    className="px-2 py-1 bg-yellow-400 rounded-2xl"
                  >
                    Éditer
                  </Link>
                  <button
                    onClick={() => handleToggle(field)}
                    className="px-2 py-1 bg-purple-500 text-white rounded-2xl"
                  >
                    {field.active ? 'Désactiver' : 'Activer'}
                  </button>
                  <button
                    onClick={() => handleDelete(field)}
                    className="px-2 py-1 bg-red-500 text-white rounded-2xl"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

