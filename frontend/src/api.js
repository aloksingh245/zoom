const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(text || `Request failed: ${resp.status}`)
  }

  if (resp.status === 204) return null
  return resp.json()
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

export async function listCourses() {
  return request('/api/courses')
}

export async function createCourse(payload) {
  return request('/api/courses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
