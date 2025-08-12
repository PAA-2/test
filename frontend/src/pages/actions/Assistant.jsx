import { useEffect, useState, useCallback, useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api, {
  assistantSuggestClosures,
  assistantPrioritize,
  assistantSummarize,
  assistantGetScores,
  getPlans,
} from '../../lib/api.js'
import Skeleton from '../../components/Skeleton.jsx'
import { useToast } from '../../components/Toast.jsx'
import useRole from '../../hooks/useRole.js'

export default function Assistant() {
  const [params, setParams] = useSearchParams()
  const [plans, setPlans] = useState([])
  const [limit, setLimit] = useState(Number(params.get('limit')) || 20)
  const [suggestions, setSuggestions] = useState([])
  const [priorities, setPriorities] = useState([])
  const [summary, setSummary] = useState(null)
  const [weights, setWeights] = useState(null)
  const [loading, setLoading] = useState(false)
  const [forbidden, setForbidden] = useState(false)
  const { show } = useToast()
  const { user, hasRole } = useRole()

  useEffect(() => {
    getPlans().then(setPlans).catch(() => setPlans([]))
    assistantGetScores().then((r) => setWeights(r.data.weights))
  }, [])

  const allowedPlanNames = useMemo(() => {
    if (!user) return new Set()
    return new Set(
      plans
        .filter((p) => user.plans_autorises?.includes(p.id))
        .map((p) => p.nom),
    )
  }, [plans, user])

  const buildFilters = () => {
    const f = {}
    ;['q', 'plan', 'statut', 'priorite', 'responsable', 'from', 'to'].forEach((k) => {
      const v = params.get(k)
      if (v) f[k] = v
    })
    return f
  }

  const fetchAll = useCallback(() => {
    const filters = buildFilters()
    setLoading(true)
    setForbidden(false)
    Promise.all([
      assistantSuggestClosures({ filters, limit }).then((r) => r.data),
      assistantPrioritize({ filters, limit }).then((r) => r.data),
      assistantSummarize({ filters }).then((r) => r.data),
    ])
      .then(([sc, pr, su]) => {
        setSuggestions(sc)
        setPriorities(pr)
        setSummary(su)
      })
      .catch((err) => {
        if (err.response && err.response.status === 403) setForbidden(true)
        else show('Erreur de chargement', 'error')
      })
      .finally(() => setLoading(false))
  }, [params, limit])

  useEffect(() => {
    fetchAll()
  }, [fetchAll])

  const updateParam = (key) => (e) => {
    const value = e.target.value
    if (value) params.set(key, value)
    else params.delete(key)
    setParams(params)
  }

  const updateLimit = (e) => {
    const v = e.target.value
    setLimit(Number(v))
    params.set('limit', v)
    setParams(params)
  }

  const canManage = (planName) =>
    hasRole('SuperAdmin', 'PiloteProcessus') ||
    (hasRole('Pilote') && allowedPlanNames.has(planName))

  const handleAction = async (actId, type) => {
    try {
      if (type === 'reject') {
        const motif = window.prompt('Motif du rejet')
        if (!motif) return
        await api.post(`/actions/${actId}/reject`, { motif })
      } else {
        await api.post(`/actions/${actId}/${type}`)
      }
      show('Action mise à jour')
      fetchAll()
    } catch (err) {
      if (err.response && err.response.status === 403) show('Accès refusé', 'error')
      else show('Erreur action', 'error')
    }
  }

  if (forbidden) {
    return <div className="p-4">Accès limité (403)</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Assistante locale (PDCA)</h2>
      <div className="flex flex-wrap gap-2 items-end">
        <input
          type="text"
          placeholder="Recherche"
          value={params.get('q') || ''}
          onChange={updateParam('q')}
          className="border rounded-xl p-2"
        />
        <input
          type="text"
          placeholder="Responsable"
          value={params.get('responsable') || ''}
          onChange={updateParam('responsable')}
          className="border rounded-xl p-2"
        />
        <select
          value={params.get('plan') || ''}
          onChange={updateParam('plan')}
          className="border rounded-xl p-2"
        >
          <option value="">Plan</option>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nom}
            </option>
          ))}
        </select>
        <select
          value={params.get('statut') || ''}
          onChange={updateParam('statut')}
          className="border rounded-xl p-2"
        >
          <option value="">Statut</option>
          <option value="En cours">En cours</option>
          <option value="En traitement">En traitement</option>
          <option value="Cloturee">Clôturée</option>
        </select>
        <select
          value={params.get('priorite') || ''}
          onChange={updateParam('priorite')}
          className="border rounded-xl p-2"
        >
          <option value="">Priorité</option>
          <option value="High">High</option>
          <option value="Med">Med</option>
          <option value="Low">Low</option>
        </select>
        <input
          type="date"
          value={params.get('from') || ''}
          onChange={updateParam('from')}
          className="border rounded-xl p-2"
        />
        <input
          type="date"
          value={params.get('to') || ''}
          onChange={updateParam('to')}
          className="border rounded-xl p-2"
        />
        <select
          value={limit}
          onChange={updateLimit}
          className="border rounded-xl p-2"
        >
          {[10, 20, 50].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
        <button
          onClick={fetchAll}
          className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
        >
          Rafraîchir
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="rounded-2xl shadow p-4 space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Suggestions de clôture</h3>
            {weights && (
              <span className="text-xs text-gray-500">
                score = delay×{weights.delay} + priority×{weights.priority} + status×{weights.status} + pdca×{weights.pdca}
              </span>
            )}
          </div>
          {loading ? (
            <Skeleton className="h-32" />
          ) : suggestions.length === 0 ? (
            <p className="text-sm text-gray-500">Aucune suggestion</p>
          ) : (
            suggestions.map((s) => (
              <div key={s.act_id} className="border-b last:border-0 py-2">
                <div className="flex justify-between">
                  <Link
                    to={`/actions/${s.act_id}`}
                    className="font-semibold hover:underline"
                  >
                    {s.act_id} - {s.titre}
                  </Link>
                  <span className="text-sm">{s.score}</span>
                </div>
                <div className="text-sm text-gray-600">
                  Resp: {s.responsables} | Délais: {s.delais} | J: {s.j}
                </div>
                {s.reasons && (
                  <ul className="text-xs text-gray-500 list-disc ml-5">
                    {s.reasons.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                )}
                {canManage(s.plan) && (
                  <div className="flex gap-2 mt-1">
                    <button
                      onClick={() => handleAction(s.act_id, 'validate')}
                      className="rounded-2xl px-3 py-1 bg-green-600 text-white text-sm"
                    >
                      Valider
                    </button>
                    <button
                      onClick={() => handleAction(s.act_id, 'close')}
                      className="rounded-2xl px-3 py-1 bg-gray-200 text-sm"
                    >
                      Clôturer
                    </button>
                    <button
                      onClick={() => handleAction(s.act_id, 'reject')}
                      className="rounded-2xl px-3 py-1 bg-red-500 text-white text-sm"
                    >
                      Rejeter
                    </button>
                  </div>
                )}
                <Link
                  to={`/actions/${s.act_id}`}
                  className="text-blue-600 text-sm"
                >
                  Voir dans la fiche
                </Link>
              </div>
            ))
          )}
        </div>

        <div className="rounded-2xl shadow p-4 space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Priorisation</h3>
            {weights && (
              <span className="text-xs text-gray-500">
                score = delay×{weights.delay} + priority×{weights.priority} + status×{weights.status} + pdca×{weights.pdca}
              </span>
            )}
          </div>
          {loading ? (
            <Skeleton className="h-32" />
          ) : priorities.length === 0 ? (
            <p className="text-sm text-gray-500">Aucune action</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th>ACT-ID</th>
                  <th>Titre</th>
                  <th>Priorité</th>
                  <th>J</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {priorities.map((p) => (
                  <tr key={p.act_id} className="border-b last:border-0">
                    <td>
                      <Link to={`/actions/${p.act_id}`} className="text-blue-600 underline">
                        {p.act_id}
                      </Link>
                    </td>
                    <td>{p.titre}</td>
                    <td>{p.priorite}</td>
                    <td>{p.j}</td>
                    <td>{p.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="rounded-2xl shadow p-4 space-y-4 md:col-span-2">
          <h3 className="text-lg font-semibold">Résumé</h3>
          {loading ? (
            <Skeleton className="h-32" />
          ) : summary ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="rounded-2xl shadow p-4">
                  <p className="text-sm text-gray-500">Total</p>
                  <p className="text-2xl font-bold">{summary.total}</p>
                </div>
                <div className="rounded-2xl shadow p-4">
                  <p className="text-sm text-gray-500">En retard</p>
                  <p className="text-2xl font-bold">{summary.en_retard}</p>
                </div>
                <div className="rounded-2xl shadow p-4">
                  <p className="text-sm text-gray-500">À clôturer</p>
                  <p className="text-2xl font-bold">{summary.a_cloturer}</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Par priorité</h4>
                  <table className="w-full text-sm">
                    <tbody>
                      {Object.entries(summary.par_priorite || {}).map(([k, v]) => (
                        <tr key={k} className="border-b last:border-0">
                          <td>{k || 'N/A'}</td>
                          <td className="text-right">{v}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Par statut</h4>
                  <table className="w-full text-sm">
                    <tbody>
                      {Object.entries(summary.par_statut || {}).map(([k, v]) => (
                        <tr key={k} className="border-b last:border-0">
                          <td>{k || 'N/A'}</td>
                          <td className="text-right">{v}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="md:col-span-2">
                  <h4 className="font-semibold mb-2">Top responsables</h4>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left border-b">
                        <th>Nom</th>
                        <th>Actions</th>
                        <th>Retards</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.top_responsables.map((r) => (
                        <tr key={r.name} className="border-b last:border-0">
                          <td>{r.name}</td>
                          <td>{r.count}</td>
                          <td>{r.retard}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <p className="text-sm text-gray-500">Aucune donnée</p>
          )}
        </div>
      </div>
    </div>
  )
}

