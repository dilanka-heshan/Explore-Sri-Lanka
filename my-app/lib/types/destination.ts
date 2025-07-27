export interface Destination {
  id: string
  name: string
  slug: string
  description?: string
  long_description?: string
  image_url?: string
  gallery_images?: string[]
  rating?: number
  review_count?: number
  region: string
  destination_type: string
  best_season?: string
  highlights?: string[]
  latitude?: number
  longitude?: number
  entry_fee?: number
  opening_hours?: any
  facilities?: string[]
  nearby_attractions?: string[]
  created_at: string
  updated_at?: string

  // Legacy support for existing components
  image?: string
  category?: string
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
  destination_type?: string
  type?: string
  province?: string
  minRating?: number
  maxRating?: number
  activities?: string[]
  page?: number
  limit?: number
  offset?: number
  search?: string
  sortBy?: 'rating' | 'name' | 'popularity'
  sortOrder?: 'asc' | 'desc'
}
