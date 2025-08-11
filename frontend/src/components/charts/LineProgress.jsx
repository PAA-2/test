import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { formatMonth } from '../../lib/format.js'

export default function LineProgress({ data }) {
  if (!data?.labels?.length) {
    return <p className="text-center text-sm text-gray-500">Aucune donnée</p>
  }
  const chartData = data.labels.map((label, i) => ({
    month: formatMonth(label),
    created: data.created_per_month[i] || 0,
    closed: data.closed_per_month[i] || 0,
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="created" stroke="#8884d8" name="Créées" />
        <Line type="monotone" dataKey="closed" stroke="#82ca9d" name="Clôturées" />
      </LineChart>
    </ResponsiveContainer>
  )
}
