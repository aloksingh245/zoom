import { useState, useEffect } from 'react'
import { getUsersStats } from '../services/api'

export function useUsersStats(isAuthenticated) {
  const [stats, setStats] = useState({ students: 0, mentors: 0, total: 0 })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchStats = async () => {
    setLoading(true)
    try {
      const data = await getUsersStats()
      setStats(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats()
    } else {
      setStats({ students: 0, mentors: 0, total: 0 })
      setError(null)
    }
  }, [isAuthenticated])

  return { stats, loading, error, fetchStats }
}
