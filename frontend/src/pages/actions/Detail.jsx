import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'

export default function ActionDetail() {
  const { actId } = useParams()
  const [action, setAction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showReject, setShowReject] = useState(false)
  const [motif, setMotif] = useState('')
  const { show } = useToast()

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

  const handleValidate = async () => {
    try {
      await api.post(`/actions/${actId}/validate`)
      show('Action validée')
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
        <button onClick={handleValidate} className="rounded-2xl px-4 py-2 bg-green-600 text-white">Valider</button>
        <button onClick={handleClose} className="rounded-2xl px-4 py-2 bg-gray-200">Clôturer</button>
        <button onClick={() => setShowReject(true)} className="rounded-2xl px-4 py-2 bg-red-500 text-white">Rejeter</button>
      </div>

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
