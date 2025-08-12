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

export const getPlans = async (params = {}) => {
  const { data } = await api.get('/plans', { params })
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

let customFieldsSchemaCache = null
let customFieldsSchemaTs = 0
export const getCustomFieldsSchema = async () => {
  const now = Date.now()
  if (customFieldsSchemaCache && now - customFieldsSchemaTs < 60000) {
    return customFieldsSchemaCache
  }
  const { data } = await api.get('/admin/custom-fields/schema')
  customFieldsSchemaCache = data
  customFieldsSchemaTs = now
  return data
}

export const listCustomFields = async (params = {}) => {
  const { data } = await api.get('/admin/custom-fields', { params })
  return data
}

export const createCustomField = async (payload) => {
  const { data } = await api.post('/admin/custom-fields', payload)
  customFieldsSchemaCache = null
  return data
}

export const updateCustomField = async (id, payload) => {
  const { data } = await api.put(`/admin/custom-fields/${id}`, payload)
  customFieldsSchemaCache = null
  return data
}

export const deleteCustomField = async (id) => {
  const { data } = await api.delete(`/admin/custom-fields/${id}`)
  customFieldsSchemaCache = null
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

export const exportExcel = (params = {}) =>
  api.get('/export/excel', { params, responseType: 'blob' })

export const exportPdf = (params = {}) =>
  api.get('/export/pdf', { params, responseType: 'blob' })

export const createCustomReport = (payload, { responseType = 'blob' } = {}) =>
  api.post('/reports/custom', payload, { responseType })

export const assistantSuggestClosures = ({ filters = {}, limit = 20 } = {}) =>
  api.post('/assistant/suggest-closures', { filters, limit })

export const assistantPrioritize = ({ filters = {}, limit = 50 } = {}) =>
  api.post('/assistant/prioritize', { filters, limit })

export const assistantSummarize = ({ filters = {} } = {}) =>
  api.post('/assistant/summarize', { filters })

export const assistantGetScores = () => api.get('/assistant/scores')

export const qualityRun = ({ filters = {}, only_rules = [], dry_run = true } = {}) =>
  api.post('/quality/run', { filters, only_rules, dry_run })

export const qualityListIssues = async (params = {}) => {
  const { data } = await api.get('/quality/issues', { params })
  return data
}

export const qualityResolveIssue = async (id) => {
  const { data } = await api.post(`/quality/issues/${id}/resolve`)
  return data
}

export const qualityIgnoreIssue = async (id) => {
  const { data } = await api.post(`/quality/issues/${id}/ignore`)
  return data
}

export const qualityListRules = async () => {
  const { data } = await api.get('/quality/rules')
  return data
}

export const listTemplates = async () => {
  const { data } = await api.get('/admin/templates')
  return data
}

export const getTemplate = async (id) => {
  const { data } = await api.get(`/admin/templates/${id}`)
  return data
}

export const createTemplate = (payload) => api.post('/admin/templates', payload)
export const updateTemplate = (id, payload) => api.put(`/admin/templates/${id}`, payload)
export const deleteTemplate = (id) => api.delete(`/admin/templates/${id}`)
export const previewTemplate = (id, context = {}) =>
  api.post(`/admin/templates/${id}/preview`, { context })

export const listAutomations = async () => {
  const { data } = await api.get('/admin/automations')
  return data
}
export const getAutomation = async (id) => {
  const { data } = await api.get(`/admin/automations/${id}`)
  return data
}
export const createAutomation = (payload) => api.post('/admin/automations', payload)
export const updateAutomation = (id, payload) => api.put(`/admin/automations/${id}`, payload)
export const deleteAutomation = (id) => api.delete(`/admin/automations/${id}`)
export const runAutomation = (id) => api.post(`/admin/automations/${id}/run`)

export const listMenuItems = async () => {
  const { data } = await api.get('/admin/menus')
  return data
}
export const getMenuItem = async (id) => {
  const { data } = await api.get(`/admin/menus/${id}`)
  return data
}
export const createMenuItem = (payload) => api.post('/admin/menus', payload)
export const updateMenuItem = (id, payload) => api.put(`/admin/menus/${id}`, payload)
export const deleteMenuItem = (id) => api.delete(`/admin/menus/${id}`)
export const getEffectiveMenu = async () => {
  const { data } = await api.get('/menu')
  return data
}

export default api
