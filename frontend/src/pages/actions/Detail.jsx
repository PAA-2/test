import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import api, { getCustomFieldsSchema } from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'
import useRole from '../../hooks/useRole.js'

export default function ActionDetail() {
  const { actId } = useParams()
  const [action, setAction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showReject, setShowReject] = useState(false)
  const [motif, setMotif] = useState('')
  const { show } = useToast()
  const { user, hasRole } = useRole()
  const [schema, setSchema] = useState(null)

  const fetchAction = useCallback(() => {
    setLoading(true)
    api
      .get(`/actions/${actId}`)
      .then((res) => setAction(res.data))
      .catch(() => setError('Action introuvable'))
      .finally(() => setLoading(false))
  }, [actId])

  useEffect(() => {
    fetchAction()
  }, [fetchAction])

  useEffect(() => {
    getCustomFieldsSchema().then(setSchema)
  }, [])

  const handleValidate = async () => {
    try {
      await api.post(`/actions/${actId}/validate`)
      show('Action validée')
      setAction((prev) => ({ ...prev, c: true, a: true }))
      fetchAction()
    } catch {
      show('Erreur de validation', 'error')
    }
  }

  const handleClose = async () => {
    try {
      await api.post(`/actions/${actId}/close`)
      show('Action clôturée')
      fetchAction()
    } catch {
      show('Erreur de clôture', 'error')
    }
  }

  const handleReject = async () => {
    try {
      await api.post(`/actions/${actId}/reject`, { motif })
      show('Action rejetée')
      setShowReject(false)
      setMotif('')
      fetchAction()
    } catch {
      show('Erreur de rejet', 'error')
    }
  }

  if (loading) return <div>Chargement...</div>
  if (error || !action) return <div>{error || 'Action introuvable'}</div>

  const canManage =
    hasRole('SuperAdmin', 'PiloteProcessus') ||
    (hasRole('Pilote') && user?.plans_autorises?.includes(action.plan))

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">{action.titre}</h2>
      <p>
        <strong>ACT-ID:</strong> {action.act_id}
      </p>
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
      <div className="flex gap-2 items-center">
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={action.p} readOnly /> P
        </label>
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={action.d} readOnly /> D
        </label>
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={action.c} readOnly /> C
        </label>
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={action.a} readOnly /> A
        </label>
      </div>
      {canManage && (
        <div className="flex gap-2">
          <Link to={`/actions/${actId}/edit`} className="rounded-2xl px-4 py-2 bg-blue-600 text-white">Modifier</Link>
          <button onClick={handleValidate} className="rounded-2xl px-4 py-2 bg-green-600 text-white">Valider</button>
          <button onClick={handleClose} className="rounded-2xl px-4 py-2 bg-gray-200">Clôturer</button>
          <button onClick={() => setShowReject(true)} className="rounded-2xl px-4 py-2 bg-red-500 text-white">Rejeter</button>
        </div>
      )}

      {schema && action.custom && Object.keys(action.custom).length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Champs personnalisés</h3>
          {schema.fields.map((f) => {
            const val = action.custom[f.key]
            if (val === undefined) return null
            let display = Array.isArray(val) ? val.join(', ') : val
            if (f.type === 'bool') display = val ? 'Oui' : 'Non'
            return (
              <p key={f.key}>
                <strong>{f.label || f.key}:</strong> {display}
              </p>
            )
          })}
        </div>
      )}

      {showReject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-4 rounded-2xl space-y-4 w-80">
            <div>
              <label className="block mb-1">Motif</label>
              <input
                className="w-full border rounded-xl p-2"
                value={motif}
                onChange={(e) => setMotif(e.target.value)}
              />
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowReject(false)}
                className="rounded-2xl px-4 py-2 bg-gray-200"
              >
                Annuler
              </button>
              <button
                onClick={handleReject}
                className="rounded-2xl px-4 py-2 bg-red-600 text-white"
              >
                Rejeter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
