import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import FilterBar from '../../components/FilterBar.jsx'
import DataTable from '../../components/DataTable.jsx'
import actionsData from '../../mocks/actions.json'

export default function ActionsList() {
  const [page, setPage] = useState(1)
  const pageSize = 10
  const [rows, setRows] = useState([])

  useEffect(() => {
    setRows(actionsData)
  }, [])

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
      <DataTable
        columns={columns}
        rows={rows.slice((page - 1) * pageSize, page * pageSize)}
        page={page}
        pageSize={pageSize}
        total={rows.length}
        onPageChange={setPage}
      />
    </div>
  )
}
