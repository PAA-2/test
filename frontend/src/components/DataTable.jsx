export default function DataTable({ columns, rows, page, pageSize, total, onSort, onPageChange }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => onSort && col.key && onSort(col.key)}
                className="cursor-pointer px-3 py-2 text-left text-sm font-medium text-gray-700"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col.key || col.label} className="px-3 py-2 text-sm">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => onPageChange && onPageChange(page - 1)}
          disabled={page <= 1}
          className="rounded-2xl px-4 py-2 bg-gray-200 disabled:opacity-50"
        >
          Précédent
        </button>
        <span>
          Page {page} / {Math.ceil(total / pageSize) || 1}
        </span>
        <button
          onClick={() => onPageChange && onPageChange(page + 1)}
          disabled={page * pageSize >= total}
          className="rounded-2xl px-4 py-2 bg-gray-200 disabled:opacity-50"
        >
          Suivant
        </button>
      </div>
    </div>
  )
}
