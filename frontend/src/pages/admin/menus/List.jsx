import { useEffect, useState } from 'react'
import { listMenuItems, createMenuItem, updateMenuItem, deleteMenuItem } from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

export default function MenusList() {
  const [items, setItems] = useState([])
  const { toast } = useToast()
  const load = () => listMenuItems().then(d => setItems(d))
  useEffect(() => { load() }, [])

  const save = async (item) => {
    if (item.id) await updateMenuItem(item.id, item)
    else await createMenuItem(item)
    toast('Sauvé')
    load()
  }

  const remove = async (id) => { await deleteMenuItem(id); load() }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Menus</h1>
      <button onClick={() => setItems([...items, { key:'', label:'', path:'/', visible_for_roles:['SuperAdmin'], order:items.length }])} className="rounded-2xl px-3 py-1 bg-blue-600 text-white">Ajouter</button>
      <table className="w-full text-left">
        <thead><tr><th>Label</th><th>Path</th><th>Roles</th><th></th></tr></thead>
        <tbody>
          {items.map((m, idx) => (
            <tr key={idx} className="border-t">
              <td><input className="border p-1" value={m.label} onChange={e=>setItems(items.map((it,i)=>i===idx?{...it,label:e.target.value}:it))}/></td>
              <td><input className="border p-1" value={m.path} onChange={e=>setItems(items.map((it,i)=>i===idx?{...it,path:e.target.value}:it))}/></td>
              <td><input className="border p-1" value={(m.visible_for_roles||[]).join(',')} onChange={e=>setItems(items.map((it,i)=>i===idx?{...it,visible_for_roles:e.target.value.split(',')}:it))}/></td>
              <td className="flex gap-2">
                <button onClick={()=>save(m)} className="text-blue-600">Save</button>
                {m.id && <button onClick={()=>remove(m.id)} className="text-red-600">Del</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
