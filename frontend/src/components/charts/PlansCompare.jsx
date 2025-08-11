import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

export default function PlansCompare({ data }) {
  if (!data?.length) {
    return <p className="text-center text-sm text-gray-500">Aucune donnée</p>
  }
  const chartData = data.map((p) => ({
    plan: p.plan,
    total: p.total || 0,
    en_retard: p.en_retard || 0,
    cloturees: p.cloturees || 0,
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <XAxis dataKey="plan" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="total" fill="#8884d8" name="Total" />
        <Bar dataKey="en_retard" fill="#f87171" name="En retard" />
        <Bar dataKey="cloturees" fill="#34d399" name="Clôturées" />
      </BarChart>
    </ResponsiveContainer>
  )
}
