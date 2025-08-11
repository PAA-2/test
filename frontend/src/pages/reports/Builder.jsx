import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getPlans, postCustomReport } from '../../lib/api.js'
import { downloadBlob } from '../../lib/download.js'
import { useToast } from '../../components/Toast.jsx'
import Skeleton from '../../components/Skeleton.jsx'

export default function ReportsBuilder() {
  const { show } = useToast()
  const [params, setParams] = useSearchParams()
  const [plans, setPlans] = useState([])
  const [preview, setPreview] = useState(null)
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [loadingPdf, setLoadingPdf] = useState(false)

  useEffect(() => {
    getPlans().then(setPlans).catch(() => setPlans([]))
  }, [])

  const update = (key) => (e) => {
    const value = e.target.value
    if (value) params.set(key, value)
    else params.delete(key)
    setParams(params)
  }

  const updateCheckbox = (key) => (e) => {
    if (e.target.checked) params.set(key, '1')
    else params.delete(key)
    setParams(params)
  }

  const buildPayload = () => {
    const filters = {}
    if (params.get('q')) filters.q = params.get('q')
    if (params.get('plan')) filters.plan = params.get('plan')
    if (params.get('responsable')) filters.responsable = params.get('responsable')
    if (params.get('priorite')) filters.priorite = params.get('priorite')
    if (params.get('from')) filters.from = params.get('from')
    if (params.get('to')) filters.to = params.get('to')

    const layout = {}
    if (params.get('paper')) layout.paper = params.get('paper')
    if (params.get('orientation')) layout.orientation = params.get('orientation')
    if (params.get('logo')) layout.logo = params.get('logo')
    if (params.get('footer')) layout.footer = params.get('footer')

    const sections = []
    if (params.get('summary_kpis')) sections.push({ type: 'summary_kpis' })
    if (params.get('grouped_table')) {
      const section = { type: 'grouped_table' }
      if (params.get('group_by')) section.group_by = params.get('group_by')
      if (params.get('columns')) section.columns = params.get('columns').split(',').map((c) => c.trim()).filter(Boolean)
      sections.push(section)
    }
    if (params.get('top_late')) {
      const limit = parseInt(params.get('top_late_limit') || '20', 10)
      sections.push({ type: 'top_late', limit })
    }
    const charts = []
    if (params.get('charts_progress')) charts.push('progress')
    if (params.get('charts_compare_plans')) charts.push('compare_plans')
    if (charts.length) sections.push({ type: 'charts', include: charts })

    return {
      title: params.get('title') || 'Rapport PAA',
      filters,
      layout,
      sections,
      dry_run: false,
    }
  }

  const handleDryRun = async () => {
    setLoadingPreview(true)
    setPreview(null)
    try {
      const payload = buildPayload()
      payload.dry_run = true
      const { data } = await postCustomReport(payload, { responseType: 'json' })
      setPreview(data)
      show('Prévisualisation générée')
    } catch (err) {
      show(err.response?.data?.detail || 'Erreur lors de la prévisualisation', 'error')
    } finally {
      setLoadingPreview(false)
    }
  }

  const handleGenerate = async () => {
    setLoadingPdf(true)
    try {
      const payload = buildPayload()
      const response = await postCustomReport(payload)
      downloadBlob(response, 'rapport_paa.pdf')
      show('Export lancé. Votre téléchargement va démarrer.')
    } catch (err) {
      show(err.response?.data?.detail || "Échec de l'export", 'error')
    } finally {
      setLoadingPdf(false)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Titre</label>
          <input
            type="text"
            value={params.get('title') || 'Rapport PAA'}
            onChange={update('title')}
            className="border rounded-xl p-2 w-full"
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Recherche</label>
          <input type="text" value={params.get('q') || ''} onChange={update('q')} className="border rounded-xl p-2 w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Plan</label>
          <select value={params.get('plan') || ''} onChange={update('plan')} className="border rounded-xl p-2 w-full">
            <option value="">Tous</option>
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nom}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium">Responsable</label>
          <input
            type="text"
            value={params.get('responsable') || ''}
            onChange={update('responsable')}
            className="border rounded-xl p-2 w-full"
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Priorité</label>
          <select value={params.get('priorite') || ''} onChange={update('priorite')} className="border rounded-xl p-2 w-full">
            <option value="">Toutes</option>
            <option value="High">High</option>
            <option value="Med">Med</option>
            <option value="Low">Low</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm font-medium">Du</label>
            <input type="date" value={params.get('from') || ''} onChange={update('from')} className="border rounded-xl p-2 w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium">Au</label>
            <input type="date" value={params.get('to') || ''} onChange={update('to')} className="border rounded-xl p-2 w-full" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm font-medium">Format papier</label>
            <select value={params.get('paper') || 'A4'} onChange={update('paper')} className="border rounded-xl p-2 w-full">
              <option value="A4">A4</option>
              <option value="A3">A3</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium">Orientation</label>
            <select value={params.get('orientation') || 'portrait'} onChange={update('orientation')} className="border rounded-xl p-2 w-full">
              <option value="portrait">Portrait</option>
              <option value="landscape">Landscape</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium">Logo (chemin)</label>
          <input type="text" value={params.get('logo') || ''} onChange={update('logo')} className="border rounded-xl p-2 w-full" />
        </div>
        <div>
          <label className="block text-sm font-medium">Pied de page</label>
          <input type="text" value={params.get('footer') || ''} onChange={update('footer')} className="border rounded-xl p-2 w-full" />
        </div>
        <fieldset className="border rounded-xl p-4">
          <legend className="font-semibold">Sections</legend>
          <label className="block">
            <input type="checkbox" checked={!!params.get('summary_kpis')} onChange={updateCheckbox('summary_kpis')} className="mr-2" />
            KPIs
          </label>
          <label className="block">
            <input type="checkbox" checked={!!params.get('grouped_table')} onChange={updateCheckbox('grouped_table')} className="mr-2" />
            Tableau groupé
          </label>
          {params.get('grouped_table') && (
            <div className="ml-4 space-y-2">
              <select value={params.get('group_by') || 'plan'} onChange={update('group_by')} className="border rounded-xl p-2 w-full">
                <option value="plan">plan</option>
                <option value="statut">statut</option>
                <option value="priorite">priorite</option>
                <option value="responsable">responsable</option>
              </select>
              <input
                type="text"
                placeholder="Colonnes séparées par des virgules"
                value={params.get('columns') || ''}
                onChange={update('columns')}
                className="border rounded-xl p-2 w-full"
              />
            </div>
          )}
          <label className="block mt-2">
            <input type="checkbox" checked={!!params.get('top_late')} onChange={updateCheckbox('top_late')} className="mr-2" />
            Top en retard
          </label>
          {params.get('top_late') && (
            <div className="ml-4">
              <input
                type="number"
                min="1"
                value={params.get('top_late_limit') || '20'}
                onChange={update('top_late_limit')}
                className="border rounded-xl p-2 w-full"
              />
            </div>
          )}
          <label className="block mt-2">Charts</label>
          <div className="ml-4">
            <label className="block">
              <input
                type="checkbox"
                checked={!!params.get('charts_progress')}
                onChange={updateCheckbox('charts_progress')}
                className="mr-2"
              />
              Progress
            </label>
            <label className="block">
              <input
                type="checkbox"
                checked={!!params.get('charts_compare_plans')}
                onChange={updateCheckbox('charts_compare_plans')}
                className="mr-2"
              />
              Compare plans
            </label>
          </div>
        </fieldset>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleDryRun}
            disabled={loadingPdf || loadingPreview}
            className="rounded-2xl px-4 py-2 bg-gray-200"
          >
            Dry-run
          </button>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loadingPdf || loadingPreview}
            className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
          >
            {loadingPdf ? 'Téléchargement…' : 'Générer PDF'}
          </button>
        </div>
      </form>
      <div className="p-4 rounded-2xl shadow bg-white">
        {loadingPreview ? (
          <Skeleton className="h-64" />
        ) : preview ? (
          <pre className="text-sm overflow-auto h-64">{JSON.stringify(preview, null, 2)}</pre>
        ) : (
          <p className="text-gray-500">Utilisez le dry-run pour voir un aperçu.</p>
        )}
      </div>
    </div>
  )
}

