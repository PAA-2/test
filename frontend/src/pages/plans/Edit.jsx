import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createPlan, updatePlan, getPlan } from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'

export default function PlanEdit() {
  const { planId } = useParams()
  const isEdit = Boolean(planId)
  const navigate = useNavigate()
  const { show } = useToast()
  const [form, setForm] = useState({
    nom: '',
    excel_path: '',
    excel_sheet: "plan d’action",
    header_row_index: 11,
    actif: true,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isEdit) {
      getPlan(planId).then((data) => setForm(data))
    }
  }, [isEdit, planId])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.nom || !form.excel_path || form.header_row_index < 1) {
      show('Champs invalides', 'error')
      return
    }
    setLoading(true)
    try {
      if (isEdit) {
        await updatePlan(planId, form)
      } else {
        await createPlan(form)
      }
      show('Plan enregistré', 'success')
      navigate('/plans')
    } catch {
      show('Erreur enregistrement', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">{isEdit ? 'Éditer' : 'Nouveau'} plan</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex flex-col">
          <label className="mb-1">Nom</label>
          <input
            name="nom"
            value={form.nom}
            onChange={handleChange}
            className="border p-2 rounded-xl"
            required
          />
        </div>
        <div className="flex flex-col md:col-span-2">
          <label className="mb-1">
            Chemin Excel
            <span className="block text-sm text-gray-500">ex: D:\monprojet\pa\backend\F-ELK-494 Plan d'action HSE.xlsx</span>
          </label>
          <input
            name="excel_path"
            value={form.excel_path}
            onChange={handleChange}
            className="border p-2 rounded-xl"
            required
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Feuille</label>
          <input
            name="excel_sheet"
            value={form.excel_sheet}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Ligne entête</label>
          <input
            type="number"
            name="header_row_index"
            value={form.header_row_index}
            onChange={handleChange}
            className="border p-2 rounded-xl"
            min={1}
          />
        </div>
        <div className="flex items-center gap-2">
          <label>Actif</label>
          <input
            type="checkbox"
            name="actif"
            checked={form.actif}
            onChange={handleChange}
          />
        </div>
        <div className="col-span-full flex gap-2 mt-4">
          <button
            type="button"
            onClick={() => navigate('/plans')}
            className="px-4 py-2 rounded-2xl border"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded-2xl bg-blue-600 text-white"
          >
            Enregistrer
          </button>
        </div>
      </form>
    </div>
  )
}
