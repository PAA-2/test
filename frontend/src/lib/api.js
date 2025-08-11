import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const getPlans = async () => {
  const { data } = await api.get('/plans')
  return data
}

export const getActions = async ({ page = 1, pageSize = 10, ordering = '', filters = {} } = {}) => {
  const params = {
    page,
    page_size: pageSize,
  }
  if (ordering) params.ordering = ordering
  if (filters.q) params.q = filters.q
  if (filters.plan) params.plan = filters.plan
  if (filters.statut) params.statut = filters.statut
  if (filters.priorite) params.priorite = filters.priorite

  const { data } = await api.get('/actions', { params })
  return data
}

export const createAction = async (payload) => {
  const { data } = await api.post('/actions', payload)
  return data
}

export default api
