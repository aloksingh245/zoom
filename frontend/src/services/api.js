const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const token = localStorage.getItem('zoom_scheduler_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const resp = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!resp.ok) {
    const text = await resp.text()
    let errorDetail = text
    try {
      const parsed = JSON.parse(text)
      errorDetail = parsed.detail || text
    } catch (e) {
      // Use raw text if not JSON
    }
    throw new Error(errorDetail || `Request failed: ${resp.status}`)
  }

  if (resp.status === 204) return null
  return resp.json()
}

// Authentication
export async function login(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function signup(payload) {
  return request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function verifyEmail(token) {
  return request(`/auth/verify-email?token=${encodeURIComponent(token)}`, {
    method: 'POST',
  })
}

export async function getMe() {
  return request('/auth/me')
}

export async function getUsersStats() {
  return request('/auth/users/stats')
}

export async function forgotPassword(payload) {
  return request('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function resetPassword(payload) {
  return request('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// Classes
export async function listClasses() {
  return request('/api/classes')
}

export async function createClass(payload) {
  return request('/api/classes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateClass(id, payload) {
  return request(`/api/classes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteClass(id) {
  return request(`/api/classes/${id}`, {
    method: 'DELETE',
  })
}

export async function syncClasses() {
  return request('/api/classes/sync', {
    method: 'POST',
  })
}

export async function syncCalendar() {
  return request('/api/classes/sync/calendar', {
    method: 'POST',
  })
}

export async function getCalendarStatus() {
  return request('/api/classes/sync/calendar/status')
}

export async function getCalendarAuthUrl() {
  return request('/api/classes/sync/calendar/auth')
}

// Courses
export async function listCourses() {
  return request('/api/courses')
}

export async function createCourse(payload) {
  return request('/api/courses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// Settings
export async function getSettings() {
  return request('/api/settings')
}

export async function updateSettings(payload) {
  return request('/api/settings', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// AI Integration
export async function parseAiSchedule(payload) {
  return request('/api/ai/parse', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function chatAi(payload) {
  return request('/api/ai/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// Super Admin Controls
export async function listTenants() {
  return request('/api/super-admin/tenants')
}

export async function toggleTenantActive(id) {
  return request(`/api/super-admin/tenants/${id}/toggle-active`, {
    method: 'POST',
  })
}

export async function deleteTenant(id) {
  return request(`/api/super-admin/tenants/${id}`, {
    method: 'DELETE',
  })
}
