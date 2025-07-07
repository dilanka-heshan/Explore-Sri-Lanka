// Re-export all types for easy importing
export * from './destination'
export * from './blog'
export * from './api'
export * from './user'
export * from './ui'

// Common utility types
export interface BaseEntity {
  id: string | number
  createdAt?: string
  updatedAt?: string
}

export interface Location {
  latitude: number
  longitude: number
  address?: string
  city?: string
  country?: string
}

export interface Image {
  id?: string | number
  url: string
  alt: string
  caption?: string
  width?: number
  height?: number
}

export interface Tag {
  id: string | number
  name: string
  slug: string
  color?: string
}

export interface Category {
  id: string | number
  name: string
  slug: string
  description?: string
  image?: string
  parent?: string | number
}

// Form types
export interface FormState {
  isLoading: boolean
  errors: Record<string, string>
  success?: boolean
  message?: string
}

// Filter and search types
export interface FilterOption {
  value: string
  label: string
  count?: number
}

export interface SortOption {
  value: string
  label: string
  order: 'asc' | 'desc'
}

// Weather and climate types
export interface WeatherInfo {
  temperature: {
    min: number
    max: number
    unit: 'C' | 'F'
  }
  humidity: number
  rainfall: number
  season: 'dry' | 'wet' | 'monsoon'
  description: string
}

// Travel season types
export interface Season {
  name: string
  months: string[]
  weather: WeatherInfo
  crowds: 'low' | 'moderate' | 'high'
  prices: 'low' | 'moderate' | 'high'
  highlights: string[]
}
