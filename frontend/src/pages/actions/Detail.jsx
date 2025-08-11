import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../lib/api.js'

export default function ActionDetail() {
  const { actId } = useParams()
  const [action, setAction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    api
      .get(`/actions/${actId}`)
      .then((res) => setAction(res.data))
      .catch(() => setError('Action introuvable'))
      .finally(() => setLoading(false))
  }, [actId])

  if (loading) return <div>Chargement...</div>
  if (error || !action) return <div>{error || 'Action introuvable'}</div>

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">{action.titre}</h2>
      <p>
        <strong>Statut:</strong> {action.statut}
      </p>
      <p>
        <strong>Priorité:</strong> {action.priorite}
      </p>
      <p>
        <strong>Responsables:</strong> {(action.responsables || []).join(', ')}
      </p>
      <p>
        <strong>Délais:</strong> {action.delais}
      </p>
      <p>
        <strong>J:</strong> {action.j}
      </p>
      <div className="flex gap-2">
        <button className="rounded-2xl px-4 py-2 bg-blue-600 text-white">Modifier</button>
        <button className="rounded-2xl px-4 py-2 bg-green-600 text-white">Valider</button>
        <button className="rounded-2xl px-4 py-2 bg-gray-200">Clôturer</button>
      </div>
    </div>
  )
}
