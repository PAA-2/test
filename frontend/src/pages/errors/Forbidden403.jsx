import { useNavigate } from 'react-router-dom'

export default function Forbidden403() {
  const navigate = useNavigate()
  return (
    <div className="mt-20 text-center space-y-4">
      <h1 className="text-2xl font-bold">403 - Accès interdit</h1>
      <button
        onClick={() => navigate(-1)}
        className="rounded-2xl px-4 py-2 bg-blue-600 text-white"
      >
        Retour
      </button>
    </div>
  )
}
