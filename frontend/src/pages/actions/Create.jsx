import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createAction, getCustomFieldsSchema } from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'
import FormBuilder from '../../components/formbuilder/FormBuilder.jsx'
import { validateAll } from '../../components/formbuilder/validate.js'
import Skeleton from '../../components/Skeleton.jsx'

export default function ActionCreate() {
    const [form, setForm] = useState({
      titre: '',
      theme: '',
      priorite: '',
      budget: '',
      responsables: '',
      delais: '',
      pdca: { P: false, D: false, C: false, A: false },
      commentaire: '',
    })
    const navigate = useNavigate()
    const [error, setError] = useState(null)
    const { show } = useToast()
    const [schema, setSchema] = useState(null)
    const [customValues, setCustomValues] = useState({})
    const [customErrors, setCustomErrors] = useState({})
    const [loadingSchema, setLoadingSchema] = useState(true)

    useEffect(() => {
      let mounted = true
      getCustomFieldsSchema()
        .then((data) => {
          if (!mounted) return
          setSchema(data)
          const initial = {}
          data.fields?.forEach((f) => {
            if (f.type === 'tags') initial[f.key] = []
            else if (f.type === 'bool') initial[f.key] = false
            else initial[f.key] = ''
          })
          setCustomValues(initial)
        })
        .finally(() => setLoadingSchema(false))
      return () => {
        mounted = false
      }
    }, [])

    const handleChange = (e) => {
      const { name, value, checked } = e.target
      if (['P', 'D', 'C', 'A'].includes(name)) {
        setForm({ ...form, pdca: { ...form.pdca, [name]: checked } })
      } else {
        setForm({ ...form, [name]: value })
      }
    }

    const handleSubmit = async (e) => {
      e.preventDefault()
      setError(null)
      const { errors, isValid } = validateAll(schema, customValues)
      if (!isValid) {
        setCustomErrors(errors)
        show('Erreur de validation', 'error')
        return
      }
      const customPayload = {}
      Object.entries(customValues).forEach(([k, v]) => {
        if (v === '' || v === null || (Array.isArray(v) && v.length === 0)) return
        customPayload[k] = v
      })
      const payload = {
        titre: form.titre,
        theme: form.theme,
        priorite: form.priorite,
        budget_dzd: form.budget ? Number(form.budget) : null,
        responsables: form.responsables
          .split(',')
          .map((r) => r.trim())
          .filter(Boolean),
        delais: form.delais || null,
        p: form.pdca.P,
        d: form.pdca.D,
        c: form.pdca.C,
        a: form.pdca.A,
        commentaire: form.commentaire,
        custom: customPayload,
      }
      try {
        const data = await createAction(payload)
        show('Action créée')
        navigate(`/actions/${data.act_id}`)
      } catch (err) {
        if (err.response && err.response.status === 400) {
          const serverErrors = err.response.data?.errors?.custom || {}
          setCustomErrors(serverErrors)
          setError('Erreur de validation')
          show('Erreur de validation', 'error')
        } else {
          setError('Erreur de création')
          show('Erreur de création', 'error')
        }
      }
    }

  return (
      <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label className="block mb-1">Titre</label>
        <input name="titre" value={form.titre} onChange={handleChange} className="w-full border rounded-xl p-2" />
      </div>
      <div>
        <label className="block mb-1">Thème</label>
        <input name="theme" value={form.theme} onChange={handleChange} className="w-full border rounded-xl p-2" />
      </div>
      <div>
        <label className="block mb-1">Priorité</label>
        <select name="priorite" value={form.priorite} onChange={handleChange} className="w-full border rounded-xl p-2">
          <option value="">--</option>
          <option value="Haute">Haute</option>
          <option value="Moyenne">Moyenne</option>
          <option value="Basse">Basse</option>
        </select>
      </div>
      <div>
        <label className="block mb-1">Budget</label>
        <input type="number" name="budget" value={form.budget} onChange={handleChange} className="w-full border rounded-xl p-2" />
      </div>
      <div>
        <label className="block mb-1">Responsables</label>
        <input name="responsables" value={form.responsables} onChange={handleChange} className="w-full border rounded-xl p-2" />
      </div>
      <div>
        <label className="block mb-1">Délais</label>
        <input type="date" name="delais" value={form.delais} onChange={handleChange} className="w-full border rounded-xl p-2" />
      </div>
      <div className="md:col-span-2 flex gap-4">
        {['P', 'D', 'C', 'A'].map((step) => (
          <label key={step} className="flex items-center gap-1">
            <input type="checkbox" name={step} checked={form.pdca[step]} onChange={handleChange} />
            {step}
          </label>
        ))}
      </div>
      <div className="md:col-span-2">
        <label className="block mb-1">Commentaire</label>
        <textarea name="commentaire" value={form.commentaire} onChange={handleChange} className="w-full border rounded-xl p-2" rows="4" />
      </div>
      </div>

      {loadingSchema && <Skeleton className="h-32" />}
      {!loadingSchema && schema && (
        <FormBuilder
          schema={schema}
          values={customValues}
          onChange={(key, val) => {
            setCustomValues((prev) => ({ ...prev, [key]: val }))
            setCustomErrors((prev) => ({ ...prev, [key]: undefined }))
          }}
          errors={customErrors}
        />
      )}
      {error && <div className="text-red-600">{error}</div>}
      <div className="flex gap-2">
        <button type="button" onClick={() => navigate(-1)} className="rounded-2xl px-4 py-2 bg-gray-200">
          Annuler
        </button>
        <button type="submit" className="rounded-2xl px-4 py-2 bg-blue-600 text-white">
          Enregistrer
        </button>
      </div>
    </form>
  )
}
