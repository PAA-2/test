import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
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

  useEffect(() => {
    getPlans()
      .then((data) => {
        let items = data
        if (hasRole('Pilote')) {
          items = items.filter((p) => user.plans_autorises.includes(p.id))
        }
        setPlans(items)
      })
      .catch(() => show('Erreur de chargement', 'error'))
      .finally(() => setLoading(false))
  }, [user, hasRole, show])

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
      setPreview(data)
    } catch {
      show('Erreur preview', 'error')
    } finally {
      setPreviewLoading(false)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Plans</h2>
        {hasRole('SuperAdmin', 'PiloteProcessus') && (
          <Link
            to="/plans/new"
            className="bg-blue-600 text-white rounded-2xl px-4 py-2"
          >
            Ajouter
          </Link>
        )}
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
              <th className="p-2">Chemin</th>
              <th className="p-2">Feuille</th>
              <th className="p-2">Ligne entête</th>
              <th className="p-2">Actif</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((plan) => (
              <tr key={plan.id} className="border-b last:border-0">
                <td className="p-2">{plan.nom}</td>
                <td className="p-2 break-all">{plan.excel_path}</td>
                <td className="p-2">{plan.excel_sheet}</td>
                <td className="p-2">{plan.header_row_index}</td>
                <td className="p-2">{plan.actif ? 'Oui' : 'Non'}</td>
                <td className="p-2 space-x-2">
                  {hasRole('SuperAdmin', 'PiloteProcessus') && (
                    <Link
                      to={`/plans/${plan.id}/edit`}
                      className="px-2 py-1 bg-yellow-400 rounded-2xl"
                    >
                      Éditer
                    </Link>
                  )}
                  {hasRole('SuperAdmin', 'PiloteProcessus') && (
                    <button
                      onClick={() => handleRescan(plan.id)}
                      className="px-2 py-1 bg-purple-500 text-white rounded-2xl"
                    >
                      Rescan
                    </button>
                  )}
                  {(hasRole('SuperAdmin', 'PiloteProcessus') ||
                    (hasRole('Pilote') && user.plans_autorises.includes(plan.id))) && (
                    <button
                      onClick={() => handlePreview(plan.id)}
                      className="px-2 py-1 bg-green-500 text-white rounded-2xl"
                    >
                      Preview
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
