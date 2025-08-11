import axios from 'axios'

export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh')
  localStorage.removeItem('user')
  window.location.href = '/login'
}

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

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh')
      if (refresh) {
        try {
          const { data } = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`, { refresh })
          localStorage.setItem('token', data.access)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        } catch {
          logout()
        }
      } else {
        logout()
      }
    }
    return Promise.reject(error)
  },
)

export const getCurrentUser = async () => {
  const { data } = await api.get('/users/me')
  localStorage.setItem('user', JSON.stringify(data))
  return data
}

export const getPlans = async () => {
  const { data } = await api.get('/plans')
  return data
}

export const getPlan = async (id) => {
  const { data } = await api.get(`/plans/${id}`)
  return data
}

export const createPlan = async (payload) => {
  const { data } = await api.post('/plans', payload)
  return data
}

export const updatePlan = async (id, payload) => {
  const { data } = await api.put(`/plans/${id}`, payload)
  return data
}

export const rescanPlan = async (id) => {
  const { data } = await api.post(`/plans/${id}/rescan`)
  return data
}

export const previewPlan = async (id) => {
  const { data } = await api.get('/excel/preview', { params: { plan: id } })
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

export const getCounters = async (params = {}, signal) => {
  const { data } = await api.get('/dashboard/counters', { params, signal })
  return data
}

export const getProgress = async (params = {}, signal) => {
  const { data } = await api.get('/charts/progress', { params, signal })
  return data
}

export const getComparePlans = async (params = {}, signal) => {
  const { data } = await api.get('/charts/compare-plans', { params, signal })
  return data
}

export const exportActionsExcel = (params = {}) =>
  api.get('/export/excel', { params, responseType: 'blob' })

export const exportActionsPdf = (params = {}) =>
  api.get('/export/pdf', { params, responseType: 'blob' })

export default api
