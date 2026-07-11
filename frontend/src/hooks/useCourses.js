import { useState, useEffect } from 'react'
import { listCourses, createCourse } from '../services/api'

export function useCourses(isAuthenticated) {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchCourses = async () => {
    setLoading(true)
    try {
      const data = await listCourses()
      setCourses(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchCourses()
    } else {
      setCourses([])
      setError(null)
    }
  }, [isAuthenticated])

  const addCourse = async (payload) => {
    const saved = await createCourse(payload)
    setCourses(prev => [...prev, saved])
    return saved
  }


  return { courses, loading, error, fetchCourses, addCourse }
}
