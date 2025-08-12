import { useEffect, useState, useCallback, useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api, {
  assistantSuggestClosures,
  assistantPrioritize,
  assistantSummarize,
  assistantGetScores,
  assistantExplain,
  assistantBatchValidate,
  assistantBatchClose,
  assistantBatchReject,
  assistantSuggestFields,
  assistantPutScores,
  assistantScheduleReminders,
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
  const [selected, setSelected] = useState([])
  const [pdca, setPdca] = useState({ C: true, A: true })
  const [comment, setComment] = useState('')
  const { show } = useToast()
  const { user, hasRole } = useRole()

  useEffect(() => {
    getPlans().then(setPlans).catch(() => setPlans([]))
    assistantGetScores().then((r) => setWeights(r.data.weights))
  }, [])

  const allowedPlanNames = useMemo(() => {
    if (!user) return new Set()
    return new Set(plans.filter((p) => user.plans_autorises?.includes(p.id)).map((p) => p.nom))
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

  const toggleSelect = (actId) => {
    setSelected((prev) =>
      prev.includes(actId) ? prev.filter((id) => id !== actId) : [...prev, actId],
    )
  }

  const handleBatch = async (type, dryRun = false) => {
    const payload = {
      act_ids: selected,
      filters: buildFilters(),
      dry_run: dryRun,
      pdca,
      comment,
    }
    try {
      const fn =
        type === 'validate'
          ? assistantBatchValidate
          : type === 'close'
          ? assistantBatchClose
          : assistantBatchReject
      const { data } = await fn(payload)
      if (!dryRun) {
        show(`${data.success} actions traitées`)
        fetchAll()
        setSelected([])
      } else {
        show(`Simulation: ${data.success}/${data.total} ok`)
      }
    } catch (err) {
      if (err.response && err.response.status === 403) show('Accès refusé', 'error')
      else show('Erreur batch', 'error')
    }
  }

  const handleExplain = async (actId) => {
    try {
      const { data } = await assistantExplain({ act_ids: [actId], filters: buildFilters() })
      alert(JSON.stringify(data[0], null, 2))
    } catch {
      show('Erreur explicabilité', 'error')
    }
  }

  const handleSuggestFields = async (actId) => {
    try {
      const { data } = await assistantSuggestFields({ act_id: actId })
      await api.put(`/actions/${actId}`, { pdca: data.suggest.pdca })
      show('Suggestion appliquée')
      fetchAll()
    } catch {
      show('Erreur suggestion', 'error')
    }
  }

  const handleWeights = async (newW) => {
    try {
      await assistantPutScores(newW)
      setWeights(newW)
      show('Poids mis à jour')
      fetchAll()
    } catch {
      show('Erreur poids', 'error')
    }
  }

  const handleScheduleReminders = async () => {
    const to = window.prompt('Destinataires (séparés par ,)')
    if (!to) return
    try {
      await assistantScheduleReminders({ to: to.split(',') })
      show('Rappels programmés')
    } catch {
      show('Erreur rappel', 'error')
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
        <select value={params.get('plan') || ''} onChange={updateParam('plan')} className="border rounded-xl p-2">
          <option value="">Plan</option>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nom}
            </option>
          ))}
        </select>
        <select value={params.get('statut') || ''} onChange={updateParam('statut')} className="border rounded-xl p-2">
          <option value="">Statut</option>
          <option value="En cours">En cours</option>
          <option value="En traitement">En traitement</option>
          <option value="Cloturee">Clôturée</option>
        </select>
        <select value={params.get('priorite') || ''} onChange={updateParam('priorite')} className="border rounded-xl p-2">
          <option value="">Priorité</option>
          <option value="High">High</option>
          <option value="Med">Med</option>
          <option value="Low">Low</option>
        </select>
        <input type="date" value={params.get('from') || ''} onChange={updateParam('from')} className="border rounded-xl p-2" />
        <input type="date" value={params.get('to') || ''} onChange={updateParam('to')} className="border rounded-xl p-2" />
        <select value={limit} onChange={updateLimit} className="border rounded-xl p-2">
          {[10, 20, 50].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
        <button onClick={fetchAll} className="rounded-2xl px-4 py-2 bg-blue-600 text-white">
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
                <div className="flex gap-2">
                  <input
                    type="checkbox"
                    checked={selected.includes(s.act_id)}
                    onChange={() => toggleSelect(s.act_id)}
                  />
                  <div className="flex-1">
                    <div className="flex justify-between">
                      <Link to={`/actions/${s.act_id}`} className="font-semibold hover:underline">
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
                    <div className="flex gap-2 mt-1 flex-wrap">
                      <button onClick={() => handleExplain(s.act_id)} className="text-xs text-gray-500 underline">
                        explications
                      </button>
                      {canManage(s.plan) && (
                        <button onClick={() => handleSuggestFields(s.act_id)} className="text-xs text-blue-600 underline">
                          appliquer suggestion
                        </button>
                      )}
                      <Link to={`/actions/${s.act_id}`} className="text-blue-600 text-sm">
                        Voir dans la fiche
                      </Link>
                    </div>
                  </div>
                </div>
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
                  <th></th>
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
                      <input
                        type="checkbox"
                        checked={selected.includes(p.act_id)}
                        onChange={() => toggleSelect(p.act_id)}
                      />
                    </td>
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
      {selected.length > 0 && (
        <div className="fixed bottom-4 left-0 right-0 flex justify-center">
          <div className="rounded-2xl shadow px-4 py-2 bg-white flex gap-2 items-center">
            <span className="text-sm">{selected.length} sélectionnées</span>
            <label className="text-xs flex items-center gap-1">
              <input
                type="checkbox"
                checked={pdca.C}
                onChange={(e) => setPdca({ ...pdca, C: e.target.checked })}
              />
              C
            </label>
            <label className="text-xs flex items-center gap-1">
              <input
                type="checkbox"
                checked={pdca.A}
                onChange={(e) => setPdca({ ...pdca, A: e.target.checked })}
              />
              A
            </label>
            <input
              type="text"
              placeholder="Commentaire"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="border rounded-xl p-1 text-xs"
            />
            <button onClick={() => handleBatch('validate')} className="rounded-2xl px-3 py-1 bg-green-600 text-white text-sm">
              Valider
            </button>
            <button onClick={() => handleBatch('close')} className="rounded-2xl px-3 py-1 bg-gray-200 text-sm">
              Clôturer
            </button>
            <button onClick={() => handleBatch('reject')} className="rounded-2xl px-3 py-1 bg-red-500 text-white text-sm">
              Rejeter
            </button>
            <button onClick={() => handleBatch('close', true)} className="rounded-2xl px-3 py-1 bg-blue-200 text-sm">
              Simuler
            </button>
          </div>
        </div>
      )}
      {hasRole('SuperAdmin', 'PiloteProcessus') && weights && (
        <div className="fixed top-4 right-4 rounded-2xl shadow p-4 bg-white space-y-2 w-52">
          <p className="text-sm font-semibold">Poids scoring</p>
          {Object.entries(weights).map(([k, v]) => (
            <label key={k} className="block text-xs">
              {k}
              <input
                type="range"
                min="0"
                max="5"
                value={v}
                onChange={(e) => handleWeights({ ...weights, [k]: Number(e.target.value) })}
              />
            </label>
          ))}
          <button onClick={handleScheduleReminders} className="mt-2 text-xs text-blue-600 underline">
            Programmer rappels
          </button>
        </div>
      )}
    </div>
  )
}
