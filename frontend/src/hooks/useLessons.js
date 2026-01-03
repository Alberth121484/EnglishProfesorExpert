import { useState, useEffect } from 'react'
import { api } from '../api/client'

export function useLessons(limit = 10) {
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    fetchLessons()
  }, [])

  const fetchLessons = async (reset = false) => {
    try {
      setLoading(true)
      const currentOffset = reset ? 0 : offset
      const response = await api.getLessons(limit, currentOffset)
      
      if (reset) {
        setLessons(response.data)
        setOffset(limit)
      } else {
        setLessons(prev => [...prev, ...response.data])
        setOffset(prev => prev + limit)
      }
      
      setHasMore(response.data.length === limit)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchLessons()
    }
  }

  return { lessons, loading, error, hasMore, loadMore, refetch: () => fetchLessons(true) }
}
