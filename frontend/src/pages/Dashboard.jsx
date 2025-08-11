import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import StatsFilterBar from '../components/StatsFilterBar.jsx'
import KpiCards from '../components/KpiCards.jsx'
import LineProgress from '../components/charts/LineProgress.jsx'
import PlansCompare from '../components/charts/PlansCompare.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { getCounters, getProgress, getComparePlans } from '../lib/api.js'
import { useToast } from '../components/Toast.jsx'

export default function Dashboard() {
  const [params] = useSearchParams()
  const [counters, setCounters] = useState(null)
  const [progress, setProgress] = useState(null)
  const [compare, setCompare] = useState(null)
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  useEffect(() => {
    const controller = new AbortController()
    const query = Object.fromEntries(params.entries())
    const { only_active, ...filters } = query
    setLoading(true)
    setCounters(null)
    setProgress(null)
    setCompare(null)
    Promise.all([
      getCounters(filters, controller.signal),
      getProgress(filters, controller.signal),
      getComparePlans({ only_active: only_active ?? true, ...filters }, controller.signal),
    ])
      .then(([c, p, cp]) => {
        setCounters(c)
        setProgress(p)
        setCompare(cp)
      })
      .catch(() => toast.show('Erreur de chargement', 'error'))
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [params, toast])

  return (
    <div className="max-w-7xl mx-auto p-4">
      <StatsFilterBar />
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
      ) : (
        <KpiCards data={counters} />
      )}
      <div className="grid md:grid-cols-2 gap-4 mt-4">
        {loading ? (
          <Skeleton className="h-72 rounded-2xl" />
        ) : (
          <div className="rounded-2xl shadow p-4">
            <h2 className="text-xl font-semibold mb-2">Évolution</h2>
            <LineProgress data={progress} />
          </div>
        )}
        {loading ? (
          <Skeleton className="h-72 rounded-2xl" />
        ) : (
          <div className="rounded-2xl shadow p-4">
            <h2 className="text-xl font-semibold mb-2">Comparatif plans</h2>
            <PlansCompare data={compare} />
          </div>
        )}
      </div>
    </div>
  )
}
