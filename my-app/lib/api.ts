const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error("API request failed:", error)
      throw error
    }
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

  // Search
  async searchContent(query: string, type?: string, limit = 10) {
    const searchParams = new URLSearchParams({ q: query, limit: limit.toString() })
    if (type) {
      searchParams.append("type", type)
    }

    return this.request(`/api/search?${searchParams}`)
  }
}

export const apiClient = new ApiClient()
export default apiClient
