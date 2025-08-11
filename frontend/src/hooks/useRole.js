import { useState, useEffect } from 'react'
import { getCurrentUser } from '../lib/api.js'

export default function useRole() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })

  useEffect(() => {
    if (!user && localStorage.getItem('token')) {
      getCurrentUser().then(setUser).catch(() => {})
    }
  }, [user])

  const hasRole = (...roles) => (user ? roles.includes(user.role) : false)

  const can = (action, resource) => {
    if (!user) return false
    const matrix = {
      action: {
        manage: ['SuperAdmin', 'PiloteProcessus'],
        validate: ['SuperAdmin', 'PiloteProcessus'],
        close: ['SuperAdmin', 'PiloteProcessus'],
        reject: ['SuperAdmin', 'PiloteProcessus'],
      },
      admin: { access: ['SuperAdmin'] },
    }
    return matrix[resource]?.[action]?.includes(user.role) || false
  }

  return { user, hasRole, can }
}
