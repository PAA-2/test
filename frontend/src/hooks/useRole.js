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

  const hasRole = (...roles) => {
    return user ? roles.includes(user.role) : false
  }

  const can = () => {
    return hasRole('SuperAdmin')
  }

  return { user, hasRole, can }
}
