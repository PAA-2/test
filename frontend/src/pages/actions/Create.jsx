import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

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

  const handleChange = (e) => {
    const { name, value, checked } = e.target
    if (['P', 'D', 'C', 'A'].includes(name)) {
      setForm({ ...form, pdca: { ...form.pdca, [name]: checked } })
    } else {
      setForm({ ...form, [name]: value })
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log(form)
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
      <div className="md:col-span-2 flex gap-2">
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
