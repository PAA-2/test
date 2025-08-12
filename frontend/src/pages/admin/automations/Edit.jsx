import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createAutomation, getAutomation, updateAutomation } from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

export default function AutomationEdit() {
  const { id } = useParams()
  const isNew = !id
  const [form, setForm] = useState({ name: '', trigger: 'manual', action: 'run_quality', enabled: true })
  const nav = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    if (!isNew) getAutomation(id).then(setForm)
  }, [id])

  const save = async () => {
    if (isNew) await createAutomation(form)
    else await updateAutomation(id, form)
    toast('Enregistré')
    nav('/admin/automations')
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{isNew ? 'Nouvelle' : 'Éditer'} automation</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input className="border p-2 rounded-xl" placeholder="Nom" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} />
        <select className="border p-2 rounded-xl" value={form.trigger} onChange={e=>setForm({...form,trigger:e.target.value})}>
          <option value="manual">manual</option>
          <option value="cron">cron</option>
          <option value="sync_fail">sync_fail</option>
          <option value="quality_threshold">quality_threshold</option>
          <option value="action_overdue">action_overdue</option>
        </select>
        <select className="border p-2 rounded-xl" value={form.action} onChange={e=>setForm({...form,action:e.target.value})}>
          <option value="notify_email">notify_email</option>
          <option value="run_quality">run_quality</option>
          <option value="run_sync">run_sync</option>
          <option value="export_report">export_report</option>
        </select>
        <label className="flex items-center gap-2"><input type="checkbox" checked={form.enabled} onChange={e=>setForm({...form,enabled:e.target.checked})}/> Enabled</label>
        <input className="border p-2 rounded-xl md:col-span-2" placeholder="Cron" value={form.cron||''} onChange={e=>setForm({...form,cron:e.target.value})} />
      </div>
      <button onClick={save} className="rounded-2xl px-3 py-1 bg-blue-600 text-white">Enregistrer</button>
    </div>
  )
}
