import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import DataTable from '../../components/DataTable.jsx'
import { getPlans, rescanPlan, previewPlan } from '../../lib/api.js'
import useRole from '../../hooks/useRole.js'
import { useToast } from '../../components/Toast.jsx'

export default function PlansIndex() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [preview, setPreview] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const { user, hasRole } = useRole()
  const { show } = useToast()
  const [searchParams, setSearchParams] = useSearchParams()
  const q = searchParams.get('q') || ''

  useEffect(() => {
    setLoading(true)
    getPlans(q ? { q } : {})
      .then((data) => {
        let items = data
        if (hasRole('Pilote', 'Utilisateur')) {
          items = items.filter((p) => user.plans_autorises.includes(p.id))
        }
        setPlans(items)
      })
      .catch(() => show('Erreur de chargement', 'error'))
      .finally(() => setLoading(false))
  }, [user, hasRole, show, q])

  const handleRescan = async (id) => {
    try {
      await rescanPlan(id)
      show('Plan rescanné', 'success')
    } catch {
      show('Erreur rescan', 'error')
    }
  }

  const handlePreview = async (id) => {
    setPreviewLoading(true)
    setPreview(null)
    try {
      const data = await previewPlan(id)
      const rows = data.rows || []
      const headers = rows.length ? Object.keys(rows[0]) : []
      const mappedRows = rows.map((r) => headers.map((h) => r[h]))
      setPreview({ headers, rows: mappedRows })
    } catch {
      show('Erreur preview', 'error')
    } finally {
      setPreviewLoading(false)
    }
  }

  const columns = [
    { key: 'nom', label: 'Nom' },
    {
      key: 'excel_path',
      label: 'Chemin',
      render: (row) => <span className="break-all">{row.excel_path}</span>,
    },
    { key: 'excel_sheet', label: 'Feuille' },
    { key: 'header_row_index', label: 'Ligne entête' },
    { key: 'actif', label: 'Actif', render: (row) => (row.actif ? 'Oui' : 'Non') },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="space-x-2">
          {hasRole('SuperAdmin', 'PiloteProcessus') && (
            <Link
              to={`/plans/${row.id}/edit`}
              className="px-2 py-1 bg-yellow-400 rounded-2xl"
            >
              Éditer
            </Link>
          )}
          {hasRole('SuperAdmin', 'PiloteProcessus') && (
            <button
              onClick={() => handleRescan(row.id)}
              className="px-2 py-1 bg-purple-500 text-white rounded-2xl"
            >
              Rescan
            </button>
          )}
          {(hasRole('SuperAdmin', 'PiloteProcessus') ||
            (hasRole('Pilote') && user.plans_autorises.includes(row.id))) && (
            <button
              onClick={() => handlePreview(row.id)}
              className="px-2 py-1 bg-green-500 text-white rounded-2xl"
            >
              Preview
            </button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Plans</h2>
        {hasRole('SuperAdmin', 'PiloteProcessus') && (
          <Link to="/plans/new" className="bg-blue-600 text-white rounded-2xl px-4 py-2">
            Ajouter
          </Link>
        )}
      </div>
      <div className="mb-4 flex items-center gap-2">
        <input
          type="text"
          value={q}
          onChange={(e) => setSearchParams(e.target.value ? { q: e.target.value } : {})}
          placeholder="Rechercher"
          className="border p-2 rounded-xl"
        />
        {q && (
          <button
            onClick={() => setSearchParams({})}
            className="px-3 py-2 rounded-2xl border"
          >
            Réinitialiser
          </button>
        )}
      </div>
      {loading ? (
        <div className="animate-pulse space-y-2">
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
          <div className="h-6 bg-gray-200 rounded" />
        </div>
      ) : plans.length ? (
        <DataTable
          columns={columns}
          rows={plans}
          page={1}
          pageSize={plans.length || 1}
          total={plans.length}
        />
      ) : (
        <p>Aucun plan</p>
      )}

      {(previewLoading || preview) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-4 rounded-2xl max-w-3xl w-full">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Prévisualisation</h3>
              <button onClick={() => setPreview(null)}>Fermer</button>
            </div>
            {previewLoading ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-200 rounded" />
                <div className="h-4 bg-gray-200 rounded" />
                <div className="h-4 bg-gray-200 rounded" />
              </div>
            ) : preview ? (
              <table className="min-w-full border">
                <thead>
                  <tr>
                    {preview.headers.map((h) => (
                      <th key={h} className="border p-1 text-left">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((row, idx) => (
                    <tr key={idx}>
                      {row.map((cell, i) => (
                        <td key={i} className="border p-1">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : null}
          </div>
        </div>
      )}
    </div>
  )
}
