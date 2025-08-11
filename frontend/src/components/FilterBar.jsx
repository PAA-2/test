import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getPlans } from '../lib/api.js'

export default function FilterBar() {
  const [params, setParams] = useSearchParams()
  const [plans, setPlans] = useState([])

  useEffect(() => {
    getPlans()
      .then((data) => setPlans(data))
      .catch(() => setPlans([]))
  }, [])

  const update = (key) => (e) => {
    const value = e.target.value
    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }
    setParams(params)
  }

  const reset = () => setParams({})

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      <input
        type="text"
        placeholder="Recherche"
        value={params.get('q') || ''}
        onChange={update('q')}
        className="border rounded-xl p-2"
      />
        <select
          value={params.get('plan') || ''}
          onChange={update('plan')}
          className="border rounded-xl p-2"
        >
          <option value="">Plan</option>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nom}
            </option>
          ))}
        </select>
      <select
        value={params.get('statut') || ''}
        onChange={update('statut')}
        className="border rounded-xl p-2"
      >
        <option value="">Statut</option>
      </select>
      <select
        value={params.get('priorite') || ''}
        onChange={update('priorite')}
        className="border rounded-xl p-2"
      >
        <option value="">Priorité</option>
      </select>
      <button onClick={reset} className="rounded-2xl px-4 py-2 bg-gray-200">
        Réinitialiser
      </button>
    </div>
  )
}
