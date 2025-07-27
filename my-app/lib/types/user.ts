export interface User {
  id: string | number
  name: string
  email: string
  avatar?: string
  bio?: string
  preferences?: UserPreferences
  createdAt: string
  updatedAt?: string
  isVerified?: boolean
  role?: 'user' | 'admin' | 'moderator'
}

export interface UserPreferences {
  language: string
  currency: string
  travelStyle: 'budget' | 'mid-range' | 'luxury'
  interests: string[]
  notifications: {
    email: boolean
    push: boolean
    marketing: boolean
  }
}

export interface TravelPlan {
  id: string | number
  userId: string | number
  title: string
  description?: string
  destinations: string[]
  startDate: string
  endDate: string
  budget?: number
  currency?: string
  travelers: number
  status: 'planning' | 'booked' | 'completed'
  itinerary?: ItineraryDay[]
  createdAt: string
  updatedAt?: string
}

export interface ItineraryDay {
  day: number
  date: string
  destination: string
  activities: Activity[]
  accommodation?: string
  notes?: string
}

export interface Activity {
  id: string | number
  name: string
  type: string
  duration: string
  cost?: number
  description?: string
  startTime?: string
  endTime?: string
}
