import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface UseDestinationTypesReturn {
  destinationTypes: string[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useDestinationTypes(): UseDestinationTypesReturn {
  const [destinationTypes, setDestinationTypes] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDestinationTypes = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.getDestinationTypes()
      setDestinationTypes(response.data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch destination types')
      console.error('Error fetching destination types:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDestinationTypes()
  }, [])

  return {
    destinationTypes,
    loading,
    error,
    refetch: fetchDestinationTypes
  }
}
