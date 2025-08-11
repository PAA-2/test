import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { getCurrentUser } from '../../lib/api.js'
import { useToast } from '../../components/Toast.jsx'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const { show } = useToast()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const { data } = await api.post('/auth/login', { username, password })
      localStorage.setItem('token', data.access)
      if (data.refresh) localStorage.setItem('refresh', data.refresh)
      await getCurrentUser()
      navigate('/')
    } catch {
      show('Identifiants invalides', 'error')
    }
  }

  return (
    <div className="max-w-md mx-auto mt-20 p-6 bg-white rounded-2xl shadow">
      <h1 className="text-2xl mb-4 text-center">Connexion</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1" htmlFor="username">Nom d'utilisateur</label>
          <input
            id="username"
            className="w-full border rounded-xl p-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label className="block mb-1" htmlFor="password">Mot de passe</label>
          <input
            id="password"
            type="password"
            className="w-full border rounded-xl p-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit" className="w-full rounded-2xl px-4 py-2 bg-blue-600 text-white">
          Se connecter
        </button>
      </form>
    </div>
  )
}
