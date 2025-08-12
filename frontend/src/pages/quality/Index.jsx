import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  qualityRun,
  qualityListIssues,
  qualityResolveIssue,
  qualityIgnoreIssue,
  qualityListRules,
  getPlans,
} from '../../lib/api.js'
import DataTable from '../../components/DataTable.jsx'
import Skeleton from '../../components/Skeleton.jsx'
import { useToast } from '../../components/Toast.jsx'
import useRole from '../../hooks/useRole.js'

export default function QualityIndex() {
  const [params, setParams] = useSearchParams()
  const [plans, setPlans] = useState([])
  const [rules, setRules] = useState([])
  const [issues, setIssues] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [dryRun, setDryRun] = useState(true)
  const [selectedRules, setSelectedRules] = useState([])
  const [forbidden, setForbidden] = useState(false)
  const { show } = useToast()
  const { user, hasRole } = useRole()

  useEffect(() => {
    getPlans().then(setPlans).catch(() => setPlans([]))
    qualityListRules().then(setRules).catch(() => setRules([]))
  }, [])

  const page = Number(params.get('page')) || 1
  const pageSize = Number(params.get('page_size')) || 20
  const ordering = params.get('ordering') || '-detected_at'

  const buildQuery = () => {
    const q = { page, page_size: pageSize, ordering }
    ;['status', 'severity', 'rule_key', 'plan', 'act_id', 'from', 'to', 'q'].forEach((k) => {
      const v = params.get(k)
      if (v) q[k] = v
    })
    return q
  }

  const fetchIssues = useCallback(() => {
    setLoading(true)
    setForbidden(false)
    qualityListIssues(buildQuery())
      .then((data) => {
        if (Array.isArray(data.results)) {
          setIssues(data.results)
          setTotal(data.count)
        } else if (Array.isArray(data)) {
          setIssues(data)
          setTotal(data.length)
        } else {
          setIssues(data.results || [])
          setTotal(data.count || 0)
        }
      })
      .catch((err) => {
        if (err.response && err.response.status === 403) setForbidden(true)
        else show('Erreur de chargement', 'error')
      })
      .finally(() => setLoading(false))
  }, [params])

  useEffect(() => {
    fetchIssues()
  }, [fetchIssues])

  const update = (key) => (e) => {
    const value = e.target.value
    if (value) params.set(key, value)
    else params.delete(key)
    params.set('page', 1)
    setParams(params)
  }

  const reset = () => {
    setParams({})
  }

  const onPageChange = (p) => {
    params.set('page', p)
    setParams(params)
  }

  const onSort = (key) => {
    const current = params.get('ordering')
    let next = key
    if (current === key) next = `-${key}`
    else if (current === `-${key}`) next = ''
    params.set('ordering', next || '-detected_at')
    setParams(params)
  }

  const canManage = (planId) =>
    hasRole('SuperAdmin', 'PiloteProcessus') ||
    (hasRole('Pilote') && user?.plans_autorises?.includes(planId))

  const handleResolve = async (id) => {
    try {
      await qualityResolveIssue(id)
      show('Anomalie résolue')
      fetchIssues()
    } catch (err) {
      if (err.response && err.response.status === 403) show('Accès refusé', 'error')
      else show('Erreur', 'error')
    }
  }

  const handleIgnore = async (id) => {
    try {
      await qualityIgnoreIssue(id)
      show('Anomalie ignorée')
      fetchIssues()
    } catch (err) {
      if (err.response && err.response.status === 403) show('Accès refusé', 'error')
      else show('Erreur', 'error')
    }
  }

  const runChecks = async () => {
    try {
      const filters = {}
      ;['plan', 'responsable', 'priorite', 'q', 'from', 'to'].forEach((k) => {
        const v = params.get(k)
        if (v) filters[k] = v
      })
      const data = await qualityRun({
        filters,
        only_rules: selectedRules,
        dry_run: dryRun,
      })
      setSummary(data)
      show('Contrôles exécutés')
      setShowModal(false)
      if (!dryRun) fetchIssues()
    } catch (err) {
      if (err.response && err.response.status === 403) show('Accès refusé', 'error')
      else show('Erreur exécution', 'error')
    }
  }

  const columns = [
    { key: 'rule_key', label: 'Règle' },
    {
      key: 'severity',
      label: 'Sévérité',
      render: (row) => (
        <span
          className={`px-2 py-1 rounded text-xs ${
            {
              LOW: 'bg-gray-200 text-gray-800',
              MED: 'bg-amber-200 text-amber-800',
              HIGH: 'bg-orange-200 text-orange-800',
              CRITICAL: 'bg-red-200 text-red-800',
            }[row.severity] || 'bg-gray-200'
          }`}
        >
          {row.severity}
        </span>
      ),
    },
    {
      label: 'ACT-ID / Plan',
      render: (row) =>
        row.act_id ? (
          <Link to={`/actions/${row.act_id}`} className="text-blue-600 underline">
            {row.act_id}
          </Link>
        ) : (
          row.plan || ''
        ),
    },
    { key: 'message', label: 'Message' },
    { key: 'detected_at', label: 'Detected at' },
    { key: 'status', label: 'Status' },
    {
      label: 'Actions',
      render: (row) =>
        row.status === 'OPEN' && canManage(row.plan) ? (
          <div className="flex gap-2">
            <button
              onClick={() => handleResolve(row.id)}
              className="text-green-600"
            >
              Resolve
            </button>
            <button
              onClick={() => handleIgnore(row.id)}
              className="text-gray-600"
            >
              Ignore
            </button>
          </div>
        ) : null,
    },
  ]

  if (forbidden) {
    return <div className="p-4">Accès limité (403)</div>
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl shadow p-4 space-y-4">
        {hasRole('SuperAdmin', 'PiloteProcessus') && (
          <button
            onClick={() => setShowModal(true)}
            className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
          >
            Run checks
          </button>
        )}
        {summary && (
          <div className="text-sm space-y-1">
            <div>Total: {summary.total}</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(summary.by_severity || {}).map(([k, v]) => (
                <span key={k} className="px-2 py-1 bg-gray-100 rounded">
                  {k}: {v}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="rounded-2xl shadow p-4 space-y-4">
        <div className="flex flex-wrap gap-2">
          <input
            type="text"
            placeholder="Recherche"
            value={params.get('q') || ''}
            onChange={update('q')}
            className="border rounded-xl p-2"
          />
          <select
            value={params.get('plan') || ''}
            onChange={update('plan')}
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
            value={params.get('severity') || ''}
            onChange={update('severity')}
            className="border rounded-xl p-2"
          >
            <option value="">Sévérité</option>
            <option value="LOW">LOW</option>
            <option value="MED">MED</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          <select
            value={params.get('rule_key') || ''}
            onChange={update('rule_key')}
            className="border rounded-xl p-2"
          >
            <option value="">Règle</option>
            {rules.map((r) => (
              <option key={r.key} value={r.key}>
                {r.name || r.key}
              </option>
            ))}
          </select>
          <select
            value={params.get('status') || ''}
            onChange={update('status')}
            className="border rounded-xl p-2"
          >
            <option value="">Status</option>
            <option value="OPEN">OPEN</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="IGNORED">IGNORED</option>
          </select>
          <input
            type="date"
            value={params.get('from') || ''}
            onChange={update('from')}
            className="border rounded-xl p-2"
          />
          <input
            type="date"
            value={params.get('to') || ''}
            onChange={update('to')}
            className="border rounded-xl p-2"
          />
          <button onClick={reset} className="rounded-2xl px-4 py-2 bg-gray-200">
            Réinitialiser
          </button>
        </div>
        {loading ? (
          <Skeleton />
        ) : issues.length ? (
          <DataTable
            columns={columns}
            rows={issues}
            page={page}
            pageSize={pageSize}
            total={total}
            onSort={onSort}
            onPageChange={onPageChange}
          />
        ) : (
          <div>Aucune anomalie</div>
        )}
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-4 rounded-2xl shadow space-y-4 max-w-md w-full">
            <h3 className="text-lg font-semibold">Run checks</h3>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
              />
              Dry run
            </label>
            <select
              multiple
              value={selectedRules}
              onChange={(e) =>
                setSelectedRules(Array.from(e.target.selectedOptions).map((o) => o.value))
              }
              className="border rounded-xl p-2 w-full h-40"
            >
              {rules.map((r) => (
                <option key={r.key} value={r.key}>
                  {r.name || r.key}
                </option>
              ))}
            </select>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowModal(false)}
                className="rounded-2xl px-4 py-2 bg-gray-200"
              >
                Annuler
              </button>
              <button
                onClick={runChecks}
                className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
              >
                Lancer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
