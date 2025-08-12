import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  qualityRun,
  qualityListIssues,
  qualityResolveIssue,
  qualityIgnoreIssue,
  qualityListRules,
  getPlans,
} from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'
import useRole from '../../hooks/useRole.js'
import DataTable from '../../components/DataTable.jsx'
import Skeleton from '../../components/Skeleton.jsx'

export default function QualityIndex() {
  const { show } = useToast()
  const { hasRole, user } = useRole()
  const [searchParams, setSearchParams] = useSearchParams()
  const [issues, setIssues] = useState({ results: [], count: 0 })
  const [loading, setLoading] = useState(false)
  const [plans, setPlans] = useState([])
  const [rules, setRules] = useState([])
  const [runStats, setRunStats] = useState(null)
  const [showRun, setShowRun] = useState(false)
  const [runDry, setRunDry] = useState(true)
  const [runOnlyRules, setRunOnlyRules] = useState([])

  const page = Number(searchParams.get('page')) || 1
  const pageSize = Number(searchParams.get('page_size')) || 20
  const ordering = searchParams.get('ordering') || '-detected_at'

  const filters = {
    q: searchParams.get('q') || '',
    plan: searchParams.get('plan') || '',
    severity: searchParams.get('severity') || '',
    rule_key: searchParams.get('rule_key') || '',
    status: searchParams.get('status') || '',
    from: searchParams.get('from') || '',
    to: searchParams.get('to') || '',
  }

  const loadIssues = async () => {
    setLoading(true)
    try {
      const params = { ...filters, page, page_size: pageSize, ordering }
      const data = await qualityListIssues(params)
      setIssues(data)
    } catch (e) {
      show('Erreur chargement anomalies', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadIssues()
  }, [page, pageSize, ordering, filters.q, filters.plan, filters.severity, filters.rule_key, filters.status, filters.from, filters.to])

  useEffect(() => {
    getPlans().then((d) => setPlans(d.results || d))
    qualityListRules().then(setRules)
  }, [])

  const updateParam = (key, value) => {
    const params = new URLSearchParams(searchParams)
    if (value) params.set(key, value)
    else params.delete(key)
    if (key !== 'page') params.delete('page')
    setSearchParams(params)
  }

  const handleResolve = async (id) => {
    try {
      await qualityResolveIssue(id)
      show('Anomalie résolue')
      loadIssues()
    } catch {
      show('Erreur résolution', 'error')
    }
  }

  const handleIgnore = async (id) => {
    try {
      await qualityIgnoreIssue(id)
      show('Anomalie ignorée')
      loadIssues()
    } catch {
      show('Erreur ignore', 'error')
    }
  }

  const canManage = (row) => {
    if (hasRole('SuperAdmin', 'PiloteProcessus')) return true
    if (hasRole('Pilote')) return user?.plans_autorises?.includes(row.plan)
    return false
  }

  const handleRun = async () => {
    try {
      const stats = await qualityRun({ filters, only_rules: runOnlyRules, dry_run: runDry })
      setRunStats(stats)
      show('Contrôles exécutés')
      if (!runDry) loadIssues()
    } catch {
      show('Erreur exécution', 'error')
    } finally {
      setShowRun(false)
    }
  }

  const columns = [
    { key: 'rule_key', label: 'Règle' },
    {
      key: 'severity',
      label: 'Sévérité',
      render: (r) => (
        <span
          className={`px-2 py-1 rounded text-xs font-semibold ${
            r.severity === 'CRITICAL'
              ? 'bg-red-100 text-red-800'
              : r.severity === 'HIGH'
              ? 'bg-orange-100 text-orange-800'
              : r.severity === 'MED'
              ? 'bg-amber-100 text-amber-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {r.severity}
        </span>
      ),
    },
    {
      key: 'entity',
      label: 'ACT-ID / Plan',
      render: (r) => r.act_id || r.plan,
    },
    { key: 'message', label: 'Message' },
    { key: 'detected_at', label: 'Detected' },
    { key: 'status', label: 'Status' },
    {
      label: 'Actions',
      render: (r) => (
        <div className="flex gap-2">
          {canManage(r) && r.status === 'OPEN' && (
            <>
              <button onClick={() => handleResolve(r.id)} title="Resolve" className="text-green-600">✓</button>
              <button onClick={() => handleIgnore(r.id)} title="Ignore" className="text-gray-500">👁‍✗</button>
            </>
          )}
          {r.act_id && <Link className="text-blue-600" to={`/actions/${r.act_id}`}>Voir</Link>}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="rounded-2xl shadow p-4 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Contrôles</h2>
          {hasRole('SuperAdmin', 'PiloteProcessus') && (
            <button
              onClick={() => setShowRun(true)}
              className="bg-blue-600 text-white rounded-2xl px-4 py-2"
            >
              Run checks
            </button>
          )}
        </div>
        {runStats && (
          <div className="text-sm space-y-1">
            <div>Total: {runStats.total}</div>
            <div>CRITICAL: {runStats.by_severity?.CRITICAL || 0}</div>
            <div>HIGH: {runStats.by_severity?.HIGH || 0}</div>
            <div>MED: {runStats.by_severity?.MED || 0}</div>
            <div>LOW: {runStats.by_severity?.LOW || 0}</div>
          </div>
        )}
      </div>

      <div className="rounded-2xl shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-2 mb-4">
          <input
            className="rounded-xl border p-2"
            placeholder="Recherche"
            value={filters.q}
            onChange={(e) => updateParam('q', e.target.value)}
          />
          <select
            className="rounded-xl border p-2"
            value={filters.plan}
            onChange={(e) => updateParam('plan', e.target.value)}
          >
            <option value="">Plan</option>
            {plans.map((p) => (
              <option key={p.id} value={p.id}>{p.nom || p.name || p.title || p.id}</option>
            ))}
          </select>
          <select
            className="rounded-xl border p-2"
            value={filters.severity}
            onChange={(e) => updateParam('severity', e.target.value)}
          >
            <option value="">Sévérité</option>
            <option value="LOW">LOW</option>
            <option value="MED">MED</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          <select
            className="rounded-xl border p-2"
            value={filters.rule_key}
            onChange={(e) => updateParam('rule_key', e.target.value)}
          >
            <option value="">Règle</option>
            {rules.map((r) => (
              <option key={r.key} value={r.key}>{r.name || r.key}</option>
            ))}
          </select>
          <select
            className="rounded-xl border p-2"
            value={filters.status}
            onChange={(e) => updateParam('status', e.target.value)}
          >
            <option value="">Status</option>
            <option value="OPEN">OPEN</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="IGNORED">IGNORED</option>
          </select>
          <button
            className="rounded-2xl px-4 py-2 bg-gray-200"
            onClick={() => {
              const params = new URLSearchParams()
              setSearchParams(params)
            }}
          >
            Réinitialiser
          </button>
        </div>
        {loading ? (
          <Skeleton className="h-40" />
        ) : issues.results.length === 0 ? (
          <div>Aucune anomalie</div>
        ) : (
          <DataTable
            columns={columns}
            rows={issues.results}
            page={page}
            pageSize={pageSize}
            total={issues.count}
            onSort={(key) => updateParam('ordering', ordering === key ? '-' + key : key)}
            onPageChange={(p) => updateParam('page', p)}
          />
        )}
      </div>

      {showRun && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-4 rounded-2xl w-96 space-y-4">
            <h3 className="text-lg font-semibold">Run checks</h3>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={runDry}
                onChange={(e) => setRunDry(e.target.checked)}
              />
              Dry run
            </label>
            <div>
              <div className="text-sm mb-1">Règles</div>
              <div className="border rounded p-2 max-h-40 overflow-y-auto space-y-1">
                {rules.map((r) => (
                  <label key={r.key} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={runOnlyRules.includes(r.key)}
                      onChange={(e) => {
                        if (e.target.checked)
                          setRunOnlyRules([...runOnlyRules, r.key])
                        else
                          setRunOnlyRules(runOnlyRules.filter((k) => k !== r.key))
                      }}
                    />
                    {r.name || r.key}
                  </label>
                ))}
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button
                className="rounded-2xl px-4 py-2 bg-gray-200"
                onClick={() => setShowRun(false)}
              >
                Annuler
              </button>
              <button
                className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
                onClick={handleRun}
              >
                Exécuter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
