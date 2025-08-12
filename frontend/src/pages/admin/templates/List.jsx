import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listTemplates, deleteTemplate } from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

export default function TemplatesList() {
  const [items, setItems] = useState([])
  const { toast } = useToast()

  const load = () => listTemplates().then(d => setItems(d))
  useEffect(() => { load() }, [])

  const handleDelete = async (id) => {
    await deleteTemplate(id)
    toast('Supprimé')
    load()
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-semibold">Templates</h1>
        <Link className="rounded-2xl px-3 py-1 bg-blue-600 text-white" to="/admin/templates/new">Nouveau</Link>
      </div>
      <table className="w-full text-left">
        <thead><tr><th>Nom</th><th>Kind</th><th></th></tr></thead>
        <tbody>
          {items.map(t => (
            <tr key={t.id} className="border-t">
              <td>{t.name}</td>
              <td>{t.kind}</td>
              <td className="flex gap-2">
                <Link to={`/admin/templates/${t.id}`} className="text-blue-600">Éditer</Link>
                <button onClick={() => handleDelete(t.id)} className="text-red-600">Suppr</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
