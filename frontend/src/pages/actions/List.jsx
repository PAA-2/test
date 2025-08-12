import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import FilterBar from '../../components/FilterBar.jsx'
import DataTable from '../../components/DataTable.jsx'
import {
  getActions,
  exportExcel,
  exportPdf,
} from '../../lib/api.js'
import { downloadBlob } from '../../lib/download.js'
import { useToast } from '../../components/Toast.jsx'

export default function ActionsList() {
  const [searchParams] = useSearchParams()
  const { show } = useToast()
  const [page, setPage] = useState(1)
  const pageSize = 10
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
  const [ordering, setOrdering] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [downloadingExcel, setDownloadingExcel] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)

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

  const buildFilters = () => {
    const filters = {
      q: searchParams.get('q') || undefined,
      plan: searchParams.get('plan') || undefined,
      statut: searchParams.get('statut') || undefined,
      priorite: searchParams.get('priorite') || undefined,
      responsable: searchParams.get('responsable') || undefined,
      from: searchParams.get('from') || undefined,
      to: searchParams.get('to') || undefined,
    }
    if (ordering) filters.ordering = ordering
    return filters
  }

  const handleExportExcel = async () => {
    const filters = buildFilters()
    setDownloadingExcel(true)
    try {
      const response = await exportExcel(filters)
      if (response?.data instanceof Blob) {
        downloadBlob(response, 'actions.xlsx')
        show('Export lancé. Votre téléchargement va démarrer.')
      } else {
        show("Échec de l'export", 'error')
      }
    } catch (err) {
      const message = err.response?.data?.message || "Échec de l'export"
      show(message, 'error')
    } finally {
      setDownloadingExcel(false)
    }
  }

  const handleExportPdf = async () => {
    const filters = buildFilters()
    setDownloadingPdf(true)
    try {
      const response = await exportPdf(filters)
      if (response?.data instanceof Blob) {
        downloadBlob(response, 'actions.pdf')
        show('Export lancé. Votre téléchargement va démarrer.')
      } else {
        show("Échec de l'export", 'error')
      }
    } catch (err) {
      const message = err.response?.data?.message || "Échec de l'export"
      show(message, 'error')
    } finally {
      setDownloadingPdf(false)
    }
  }

  const columns = [
    { key: 'act_id', label: 'ID' },
    { key: 'titre', label: 'Titre' },
    { key: 'statut', label: 'Statut' },
    { key: 'priorite', label: 'Priorité' },
    { key: 'responsables', label: 'Responsables' },
    { key: 'delais', label: 'Délais' },
    { key: 'J', label: 'J' },
    {
      key: 'actions',
      label: '',
      render: (row) => (
        <Link to={`/actions/${row.act_id}/edit`} className="text-blue-600">
          Modifier
        </Link>
      ),
    },
  ]

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center mb-4 gap-4">
        <FilterBar />
        <div className="flex flex-wrap justify-end items-center gap-3">
          <button
            onClick={handleExportExcel}
            disabled={downloadingExcel}
            className="rounded-2xl px-4 py-2 shadow bg-blue-600 text-white flex items-center gap-2"
          >
            {downloadingExcel && (
              <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            {downloadingExcel ? 'Téléchargement…' : 'Exporter Excel'}
          </button>
          <button
            onClick={handleExportPdf}
            disabled={downloadingPdf}
            className="rounded-2xl px-4 py-2 shadow bg-gray-200 text-gray-800 flex items-center gap-2"
          >
            {downloadingPdf && (
              <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            {downloadingPdf ? 'Téléchargement…' : 'Exporter PDF'}
          </button>
          <Link to="/actions/new" className="rounded-2xl px-4 py-2 bg-blue-600 text-white">
            Nouvelle action
          </Link>
        </div>
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
