import { useParams } from 'react-router-dom'
import actions from '../../mocks/actions.json'

export default function ActionDetail() {
  const { actId } = useParams()
  const action = actions.find((a) => a.act_id === actId)

  if (!action) {
    return <div>Action introuvable</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">{action.titre}</h2>
      <p><strong>Statut:</strong> {action.statut}</p>
      <p><strong>Priorité:</strong> {action.priorite}</p>
      <p><strong>Responsables:</strong> {action.responsables}</p>
      <p><strong>Délais:</strong> {action.delais}</p>
      <p><strong>J:</strong> {action.J}</p>
      <div className="flex gap-2">
        <button className="rounded-2xl px-4 py-2 bg-blue-600 text-white">Modifier</button>
        <button className="rounded-2xl px-4 py-2 bg-green-600 text-white">Valider</button>
        <button className="rounded-2xl px-4 py-2 bg-gray-200">Clôturer</button>
      </div>
    </div>
  )
}
