import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createTemplate, getTemplate, updateTemplate, previewTemplate } from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

export default function TemplateEdit() {
  const { id } = useParams()
  const isNew = !id
  const [form, setForm] = useState({ name: '', kind: 'email', subject: '', body_html: '', body_text: '' })
  const [preview, setPreview] = useState(null)
  const nav = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    if (!isNew) getTemplate(id).then(setForm)
  }, [id])

  const save = async () => {
    if (isNew) await createTemplate(form)
    else await updateTemplate(id, form)
    toast('Enregistré')
    nav('/admin/templates')
  }

  const handlePreview = async () => {
    const { data } = await previewTemplate(id, { name: 'Test' })
    setPreview(data)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{isNew ? 'Nouveau' : 'Éditer'} template</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input className="border p-2 rounded-xl" placeholder="Nom" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
        <select className="border p-2 rounded-xl" value={form.kind} onChange={e => setForm({ ...form, kind: e.target.value })}>
          <option value="email">email</option>
          <option value="report">report</option>
        </select>
        {form.kind === 'email' && (
          <input className="border p-2 rounded-xl" placeholder="Subject" value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} />
        )}
        <textarea className="border p-2 rounded-xl md:col-span-2" rows="6" placeholder="HTML" value={form.body_html} onChange={e => setForm({ ...form, body_html: e.target.value })} />
        <textarea className="border p-2 rounded-xl md:col-span-2" rows="4" placeholder="Text" value={form.body_text} onChange={e => setForm({ ...form, body_text: e.target.value })} />
      </div>
      <div className="flex gap-2">
        <button onClick={save} className="rounded-2xl px-3 py-1 bg-blue-600 text-white">Enregistrer</button>
        {!isNew && <button onClick={handlePreview} className="rounded-2xl px-3 py-1 bg-gray-600 text-white">Prévisualiser</button>}
      </div>
      {preview && (
        <div className="border p-4 rounded-2xl" dangerouslySetInnerHTML={{ __html: preview.body_html }} />
      )}
    </div>
  )
}
