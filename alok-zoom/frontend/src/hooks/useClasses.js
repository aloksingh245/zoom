import { useState, useEffect, useMemo } from 'react'
import { listClasses, createClass, updateClass, deleteClass, syncClasses } from '../services/api'
import { getClassStatus } from '../utils/dateUtils'

export function useClasses() {
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchClasses = async () => {
    setLoading(true)
    try {
      const data = await listClasses()
      setClasses(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClasses()
  }, [])

  const addClass = async (payload) => {
    const saved = await createClass(payload)
    setClasses(prev => [...prev, saved])
    return saved
  }

  const editClass = async (id, payload) => {
    const saved = await updateClass(id, payload)
    setClasses(prev => prev.map(item => item.id === id ? saved : item))
    return saved
  }

  const removeClass = async (id) => {
    await deleteClass(id)
    setClasses(prev => prev.filter(item => item.id !== id))
  }

  const syncWithZoom = async () => {
    setLoading(true)
    try {
      const result = await syncClasses()
      await fetchClasses()
      return result
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const classesByDate = useMemo(() => {
    const map = new Map()
    classes.forEach(item => {
      if (!map.has(item.date)) map.set(item.date, [])
      map.get(item.date).push(item)
    })
    map.forEach(list => list.sort((a, b) => a.start_time.localeCompare(b.start_time)))
    return map
  }, [classes])

  return { 
    classes, 
    loading, 
    error, 
    fetchClasses, 
    addClass, 
    editClass, 
    removeClass,
    syncWithZoom,
    classesByDate
  }
}
