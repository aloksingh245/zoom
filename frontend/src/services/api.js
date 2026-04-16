const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  if (token) {
    return { 'Authorization': `Bearer ${token}` }
  }
  return {}
}

async function request(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!resp.ok) {
    // If unauthorized, clear token and maybe redirect
    if (resp.status === 401) {
      localStorage.removeItem('token')
      window.location.reload()
    }
    
    let text = ''
    try {
      const data = await resp.json()
      text = data.detail || JSON.stringify(data)
    } catch {
      text = await resp.text()
    }
    
    throw new Error(text || `Request failed: ${resp.status}`)
  }

  if (resp.status === 204) return null
  return resp.json()
}

export async function requestOtp(payload) {
  return request('/api/auth/request-otp', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function signup(payload) {
  return request('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function login(payload) {
  return request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

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

export async function listCourses() {
  return request('/api/courses')
}

export async function createCourse(payload) {
  return request('/api/courses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function chatWithAI(payload) {
  return request('/api/ai/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
