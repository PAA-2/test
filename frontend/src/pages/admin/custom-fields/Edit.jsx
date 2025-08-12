import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import {
  listCustomFields,
  createCustomField,
  updateCustomField,
} from '../../../lib/api.js'
import { useToast } from '../../../components/Toast.jsx'

const emptyField = {
  name: '',
  key: '',
  type: 'text',
  required: false,
  min: '',
  max: '',
  regex: '',
  help_text: '',
  role_visibility: 'All',
  active: true,
  options: [],
}

const slugify = (str) =>
  str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')

export default function CustomFieldEdit() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const location = useLocation()
  const { show } = useToast()
  const [form, setForm] = useState(emptyField)
  const [errors, setErrors] = useState({})
  const [initialType, setInitialType] = useState('text')

  useEffect(() => {
    if (isEdit) {
      listCustomFields().then((data) => {
        const f = data.find((cf) => String(cf.id) === id)
        if (f) {
          setForm({ ...emptyField, ...f })
          setInitialType(f.type)
        }
      })
    } else if (location.state) {
      setForm({ ...emptyField, ...location.state })
    }
  }, [isEdit, id, location.state])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
    if (name === 'name' && !isEdit) {
      setForm((f) => ({ ...f, key: slugify(value) }))
    }
  }

  const handleOptionChange = (index, field, value) => {
    setForm((f) => {
      const options = [...f.options]
      options[index] = { ...options[index], [field]: value }
      return { ...f, options }
    })
  }

  const addOption = () => {
    setForm((f) => ({
      ...f,
      options: [...f.options, { label: '', value: '', order: f.options.length + 1 }],
    }))
  }

  const removeOption = (idx) => {
    setForm((f) => ({
      ...f,
      options: f.options.filter((_, i) => i !== idx),
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    try {
      if (isEdit) {
        await updateCustomField(id, form)
      } else {
        await createCustomField(form)
      }
      show('Champ enregistré', 'success')
      navigate('/admin/custom-fields')
    } catch (err) {
      if (err.response && err.response.status === 400 && err.response.data) {
        setErrors(err.response.data)
      } else {
        show('Erreur enregistrement', 'error')
      }
    }
  }

  const duplicate = () => {
    const clone = { ...form, id: undefined, key: '' }
    navigate('/admin/custom-fields/new', { state: clone })
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">
        {isEdit ? 'Éditer' : 'Nouveau'} champ personnalisé
      </h2>
      {isEdit && form.type !== initialType && (
        <div className="p-2 bg-yellow-200 mb-4 rounded">
          Changer le type peut rendre les anciennes valeurs invalides.
        </div>
      )}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex flex-col">
          <label className="mb-1">Nom</label>
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            className="border p-2 rounded-xl"
            required
          />
          {errors.name && <p className="text-sm text-red-600">{errors.name}</p>}
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Clé</label>
          <input
            name="key"
            value={form.key}
            onChange={handleChange}
            className="border p-2 rounded-xl"
            readOnly={isEdit}
            required
          />
          {errors.key && <p className="text-sm text-red-600">{errors.key}</p>}
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Type</label>
          <select
            name="type"
            value={form.type}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          >
            <option value="text">text</option>
            <option value="number">number</option>
            <option value="date">date</option>
            <option value="select">select</option>
            <option value="tags">tags</option>
            <option value="bool">bool</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label>Requis</label>
          <input
            type="checkbox"
            name="required"
            checked={form.required}
            onChange={handleChange}
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Min</label>
          <input
            name="min"
            type="number"
            value={form.min}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Max</label>
          <input
            name="max"
            type="number"
            value={form.max}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Regex</label>
          <input
            name="regex"
            value={form.regex}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          />
        </div>
        <div className="flex flex-col md:col-span-2">
          <label className="mb-1">Aide</label>
          <textarea
            name="help_text"
            value={form.help_text}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          />
        </div>
        <div className="flex flex-col">
          <label className="mb-1">Visibilité</label>
          <select
            name="role_visibility"
            value={form.role_visibility}
            onChange={handleChange}
            className="border p-2 rounded-xl"
          >
            <option value="All">All</option>
            <option value="SA_PP">SA_PP</option>
            <option value="Pilote">Pilote</option>
            <option value="Utilisateur">Utilisateur</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label>Actif</label>
          <input
            type="checkbox"
            name="active"
            checked={form.active}
            onChange={handleChange}
          />
        </div>

        {(form.type === 'select' || form.type === 'tags') && (
          <div className="md:col-span-2">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold">Options</h3>
              <button
                type="button"
                onClick={addOption}
                className="px-2 py-1 bg-blue-600 text-white rounded-2xl"
              >
                Ajouter
              </button>
            </div>
            {form.options.map((opt, idx) => (
              <div key={idx} className="grid grid-cols-3 gap-2 mb-2 items-center">
                <input
                  placeholder="Label"
                  value={opt.label}
                  onChange={(e) => handleOptionChange(idx, 'label', e.target.value)}
                  className="border p-2 rounded-xl"
                />
                <input
                  placeholder="Value"
                  value={opt.value}
                  onChange={(e) => handleOptionChange(idx, 'value', e.target.value)}
                  className="border p-2 rounded-xl"
                />
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    placeholder="Ordre"
                    value={opt.order}
                    onChange={(e) => handleOptionChange(idx, 'order', e.target.value)}
                    className="border p-2 rounded-xl w-full"
                  />
                  <button
                    type="button"
                    onClick={() => removeOption(idx)}
                    className="px-2 py-1 bg-red-500 text-white rounded-2xl"
                  >
                    -
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="col-span-full flex gap-2 mt-4">
          {isEdit && (
            <button
              type="button"
              onClick={duplicate}
              className="px-4 py-2 rounded-2xl border"
            >
              Dupliquer
            </button>
          )}
          <button
            type="button"
            onClick={() => navigate('/admin/custom-fields')}
            className="px-4 py-2 rounded-2xl border"
          >
            Annuler
          </button>
          <button
            type="submit"
            className="px-4 py-2 rounded-2xl bg-blue-600 text-white"
          >
            Enregistrer
          </button>
        </div>
      </form>
    </div>
  )
}

