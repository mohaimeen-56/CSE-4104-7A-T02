import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('salesiq_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Handle errors globally
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      // If token expired, clear and redirect if not on login/register
      const isAuthPath = window.location.pathname.includes('/login') || window.location.pathname.includes('/register')
      if (!isAuthPath) {
        localStorage.removeItem('salesiq_token')
        localStorage.removeItem('salesiq_user')
        window.location.href = '/login'
      }
    }
    if (error.response?.status === 503 && error.response?.data?.error?.code === 'MAINTENANCE_MODE') {
      window.dispatchEvent(new CustomEvent('salesiq:maintenance', { detail: error.response.data.error.message }))
    }
    const message =
      error.response?.data?.error?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/users/me', data),
}

export const salesApi = {
  list: (params) => api.get('/sales', { params }),
  getById: (id) => api.get(`/sales/${id}`),
  create: (data) => api.post('/sales', data),
  update: (id, data) => api.put(`/sales/${id}`, data),
  delete: (id) => api.delete(`/sales/${id}`),
  uploadCsv: (formData) =>
    api.post('/sales/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}

export const productsApi = {
  list: () => api.get('/products'),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
}

export const regionsApi = {
  list: () => api.get('/regions'),
  getById: (id) => api.get(`/regions/${id}`),
  create: (data) => api.post('/regions', data),
  update: (id, data) => api.put(`/regions/${id}`, data),
  delete: (id) => api.delete(`/regions/${id}`),
}

export const analyticsApi = {
  getOverview: (params) => api.get('/analytics/overview', { params }),
  getSummary: (params) => api.get('/analytics/summary', { params }),
  getRevenueTrend: (params) => api.get('/analytics/revenue-trend', { params }),
  getSalesByProduct: (params) => api.get('/analytics/by-product', { params }),
  getSalesByCategory: (params) => api.get('/analytics/by-category', { params }),
  getSalesByRegion: (params) => api.get('/analytics/by-region', { params }),
  getTopProducts: (params) => api.get('/analytics/top-products', { params }),
  getMonthlyComparison: (params) => api.get('/analytics/monthly-comparison', { params }),
  getHourly: (params) => api.get('/analytics/hourly', { params }),
  getPeakHours: (params) => api.get('/analytics/peak-hours', { params }),
  getByDayOfWeek: (params) => api.get('/analytics/by-day-of-week', { params }),
  getTimeOfDay: (params) => api.get('/analytics/time-of-day', { params }),
  getDataQuality: () => api.get('/analytics/data-quality'),
  getDecisionSignals: () => api.get('/analytics/decision-signals'),
  getExecutiveSummary: () => api.get('/analytics/executive-summary'),
  dataExplorer: (params) => api.get('/analytics/data-explorer', { params }),
}

export const adminApi = {
  getMaintenanceStatus: () => api.get('/admin/maintenance'),
  enableMaintenance: (data) => api.post('/admin/maintenance/enable', data),
  disableMaintenance: (data) => api.post('/admin/maintenance/disable', data),
  getMaintenanceAuditLog: () => api.get('/admin/maintenance/audit-log'),
  generateInviteCode: () => api.post('/admin/invite-codes'),
  listInviteCodes: () => api.get('/admin/invite-codes'),
  revokeInviteCode: (id) => api.delete(`/admin/invite-codes/${id}`),
}

export const aiApi = {
  getInsights: (data) => api.post('/ai/insights', data),
  getForecast: () => api.get('/ai/forecast'),
  getAnomalies: (params) => api.get('/ai/anomalies', { params }),
  getRecommendations: () => api.get('/ai/recommendations'),
  chat: (data) => api.post('/ai/chat', data),
}

// Downloads a file via an authenticated axios request (plain <a href> / window.open can't
// carry the Authorization header, and export endpoints require auth). The response
// interceptor below unwraps axios responses to `response.data`, which for
// responseType:'blob' is already the Blob itself.
async function downloadAuthenticated(url, params, filenameFallback) {
  const blob = await api.get(url, { params, responseType: 'blob' })
  const objectUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filenameFallback
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(objectUrl)
}

export const reportsApi = {
  getMonthlyData: (params) => api.get('/reports/monthly', { params }),
  buildReport: (params) => api.get('/reports/builder', { params }),
  downloadBuilderCsv: (params) => downloadAuthenticated('/reports/builder/export/csv', params, 'salesiq_report.csv'),
  downloadBuilderPdf: (params) => downloadAuthenticated('/reports/builder/export/pdf', params, 'salesiq_report.pdf'),
  downloadCsv: (params) => downloadAuthenticated('/reports/export/csv', params, 'sales_export.csv'),
  downloadPdf: (params) => downloadAuthenticated('/reports/export/pdf', params, 'sales_report.pdf'),
}

export const notificationsApi = {
  list: (params) => api.get('/notifications', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markAsRead: (id) => api.put(`/notifications/${id}/read`),
  markAllAsRead: () => api.put('/notifications/read-all'),
}

export default api
