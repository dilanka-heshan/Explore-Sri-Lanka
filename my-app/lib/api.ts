const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken')
    }
    return null
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getAuthToken()

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("API request failed:", error)
      throw error
    }
  }

  // Health check
  async healthCheck() {
    return this.request("/health")
  }

  // Destinations
  async getDestinations(params?: {
    region?: string
    destination_type?: string
    search?: string
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/destinations?${searchParams}`)
  }

  async getDestinationTypes() {
    return this.request(`/api/destinations/types`)
  }

  async getDestinationBySlug(slug: string) {
    return this.request(`/api/destinations/${slug}`)
  }

  async getDestinationReviews(destinationId: string, limit = 10, offset = 0) {
    return this.request(`/api/destinations/${destinationId}/reviews?limit=${limit}&offset=${offset}`)
  }

  async createReview(destinationId: string, review: any) {
    return this.request(`/api/destinations/${destinationId}/reviews`, {
      method: "POST",
      body: JSON.stringify(review),
    })
  }

  // Experiences
  async getExperiences(params?: {
    category?: string
    destination_id?: string
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/experiences?${searchParams}`)
  }

  async getExperienceBySlug(slug: string) {
    return this.request(`/api/experiences/${slug}`)
  }

  // Itineraries
  async getItineraries(params?: {
    trip_type?: string
    duration_min?: number
    duration_max?: number
    price_min?: number
    price_max?: number
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/itineraries?${searchParams}`)
  }

  async getItineraryBySlug(slug: string) {
    return this.request(`/api/itineraries/${slug}`)
  }

  // Blog
  async getBlogPosts(params?: {
    category?: string
    tag?: string
    search?: string
    published_only?: boolean
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/blog?${searchParams}`)
  }

  async getBlogPostBySlug(slug: string) {
    return this.request(`/api/blog/${slug}`)
  }

  // Bookings
  async createBooking(booking: any) {
    return this.request("/api/bookings", {
      method: "POST",
      body: JSON.stringify(booking),
    })
  }

  async getBooking(bookingId: string) {
    return this.request(`/api/bookings/${bookingId}`)
  }

  // Newsletter
  async subscribeNewsletter(email: string) {
    return this.request("/api/newsletter/subscribe", {
      method: "POST",
      body: JSON.stringify({ email }),
    })
  }

  // Contact
  async submitContactMessage(message: any) {
    return this.request("/api/contact", {
      method: "POST",
      body: JSON.stringify(message),
    })
  }

  // Media
  async getMediaGallery(params?: {
    category?: string
    destination_id?: string
    featured_only?: boolean
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/media?${searchParams}`)
  }

  // Travel Planning
  async planTrip(planningData: {
    query: string
    interests: string[]
    trip_duration_days: number
    budget_level: 'budget' | 'mid_range' | 'luxury'
    max_attractions_per_day?: number
    daily_travel_preference?: 'minimal' | 'moderate' | 'extensive'
  }) {
    return this.request("/clustered-recommendations/plan", {
      method: "POST",
      body: JSON.stringify(planningData),
    })
  }

  // Integrated Planning (Enhanced)
  async planTripIntegrated(planningData: {
    query: string
    interests: string[]
    trip_duration_days: number
    budget_level: 'budget' | 'mid_range' | 'luxury'
    trip_type?: 'solo' | 'couple' | 'family' | 'group'
    activity_level?: number
    max_attractions_per_day?: number
    daily_travel_preference?: 'minimal' | 'moderate' | 'extensive'
    enable_google_places?: boolean
    enable_llm_enhancement?: boolean
  }) {
    return this.request("/integrated-planning/plan", {
      method: "POST",
      body: JSON.stringify(planningData),
    })
  }

  // Search
  async searchContent(query: string, type?: string, limit = 10) {
    const searchParams = new URLSearchParams({ q: query, limit: limit.toString() })
    if (type) searchParams.append('type', type)
    
    return this.request(`/api/search?${searchParams}`)
  }
}

export const apiClient = new ApiClient()
export default apiClient
