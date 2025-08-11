import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import FilterBar from '../../components/FilterBar.jsx'
import DataTable from '../../components/DataTable.jsx'
import { getActions } from '../../lib/api.js'

export default function ActionsList() {
  const [searchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const pageSize = 10
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
  const [ordering, setOrdering] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const filters = {
      q: searchParams.get('q') || undefined,
      plan: searchParams.get('plan') || undefined,
      statut: searchParams.get('statut') || undefined,
      priorite: searchParams.get('priorite') || undefined,
    }
    setLoading(true)
    setError(null)
    getActions({ page, pageSize, ordering, filters })
      .then((data) => {
        setRows(data.results || [])
        setTotal(data.count || 0)
      })
      .catch(() => setError('Erreur de chargement'))
      .finally(() => setLoading(false))
  }, [searchParams, page, ordering])

  const handleSort = (key) => {
    setPage(1)
    setOrdering((prev) =>
      prev === key ? `-${key}` : prev === `-${key}` ? '' : key
    )
  }

  const columns = [
    { key: 'act_id', label: 'ID' },
    { key: 'titre', label: 'Titre' },
    { key: 'statut', label: 'Statut' },
    { key: 'priorite', label: 'Priorité' },
    { key: 'responsables', label: 'Responsables' },
    { key: 'delais', label: 'Délais' },
    { key: 'J', label: 'J' },
  ]

    return (
      <div>
        <div className="flex justify-between items-center mb-4">
          <FilterBar />
          <Link to="/actions/new" className="rounded-2xl px-4 py-2 bg-blue-600 text-white">
            Nouvelle action
          </Link>
        </div>
        {loading && <div>Chargement...</div>}
        {error && <div className="text-red-600">{error}</div>}
        {!loading && !error && rows.length === 0 && <div>Aucune action</div>}
        {!loading && !error && rows.length > 0 && (
          <DataTable
            columns={columns}
            rows={rows}
            page={page}
            pageSize={pageSize}
            total={total}
            onSort={handleSort}
            onPageChange={setPage}
          />
        )}
      </div>
    )
}
