export interface Destination {
  id: string | number
  name: string
  description: string
  image: string
  category: string
  rating: number
  region?: string
  type?: string
  province?: string
  district?: string
  location?: {
    latitude: number
    longitude: number
  }
  attractions?: string[]
  bestTimeToVisit?: string
  activities?: string[]
  difficulty?: 'Easy' | 'Moderate' | 'Challenging'
  duration?: string
  cost?: {
    budget: number
    currency: string
  }
  tags?: string[]
}

export interface DestinationFilters {
  regions: string[]
  types: string[]
  categories: string[]
  provinces: string[]
  activities: string[]
}

export interface DestinationSearchParams {
  query?: string
  category?: string
  region?: string
  type?: string
  province?: string
  minRating?: number
  maxRating?: number
  activities?: string[]
  page?: number
  limit?: number
  sortBy?: 'rating' | 'name' | 'popularity'
  sortOrder?: 'asc' | 'desc'
}
