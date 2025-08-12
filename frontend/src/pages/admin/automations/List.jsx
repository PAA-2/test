import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listAutomations, deleteAutomation, runAutomation } from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

export default function AutomationsList() {
  const [items, setItems] = useState([])
  const { toast } = useToast()
  const load = () => listAutomations().then(d => setItems(d))
  useEffect(() => { load() }, [])

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-semibold">Automations</h1>
        <Link to="/admin/automations/new" className="rounded-2xl px-3 py-1 bg-blue-600 text-white">Nouvelle</Link>
      </div>
      <table className="w-full text-left">
        <thead><tr><th>Nom</th><th>Trigger</th><th></th></tr></thead>
        <tbody>
          {items.map(a => (
            <tr key={a.id} className="border-t">
              <td>{a.name}</td>
              <td>{a.trigger}</td>
              <td className="flex gap-2">
                <button onClick={() => runAutomation(a.id).then(r=>toast(r.data.status))} className="text-green-600">Run</button>
                <Link to={`/admin/automations/${a.id}`} className="text-blue-600">Éditer</Link>
                <button onClick={() => {deleteAutomation(a.id); load()}} className="text-red-600">Suppr</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
