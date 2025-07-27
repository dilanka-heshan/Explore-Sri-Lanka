const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private getAuthToken(): string | null {
    // Only access localStorage on the client side
    if (typeof window !== 'undefined') {
      try {
        return localStorage.getItem('authToken')
      } catch (error) {
        console.error('Error accessing localStorage:', error)
        return null
      }
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

  // ========== AUTH ENDPOINTS ==========
  
  // Auth - Registration & Login
  async register(userData: {
    email: string
    password: string
    full_name: string
    phone?: string
    date_of_birth?: string
    preferences?: any
  }) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }

  async login(credentials: { email: string; password: string }) {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    })
  }

  async logout() {
    return this.request("/api/auth/logout", {
      method: "POST",
    })
  }

  async refreshToken() {
    return this.request("/api/auth/refresh-token", {
      method: "POST",
    })
  }

  // Auth - Profile Management
  async getUserProfile() {
    return this.request("/api/auth/me")
  }

  async updateProfile(profileData: {
    full_name?: string
    phone?: string
    date_of_birth?: string
    preferences?: any
  }) {
    return this.request("/api/auth/me", {
      method: "PUT",
      body: JSON.stringify(profileData),
    })
  }

  async updatePassword(passwordData: {
    current_password: string
    new_password: string
  }) {
    return this.request("/api/auth/me/password", {
      method: "PUT",
      body: JSON.stringify(passwordData),
    })
  }

  // Auth - Saved Destinations
  async saveDestination(destinationId: string) {
    return this.request(`/api/auth/me/saved-destinations/${destinationId}`, {
      method: "POST",
    })
  }

  async unsaveDestination(destinationId: string) {
    return this.request(`/api/auth/me/saved-destinations/${destinationId}`, {
      method: "DELETE",
    })
  }

  async getSavedDestinations() {
    return this.request("/api/auth/me/saved-destinations")
  }

  // Auth - Password Reset
  async forgotPassword(email: string) {
    return this.request("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    })
  }

  async resetPassword(resetData: {
    token: string
    new_password: string
  }) {
    return this.request("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(resetData),
    })
  }

  // Auth - Email Verification
  async verifyEmail(token: string) {
    return this.request("/api/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
  }

  async resendVerification(email: string) {
    return this.request("/api/auth/resend-verification", {
      method: "POST",
      body: JSON.stringify({ email }),
    })
  }

  // ========== DESTINATIONS ENDPOINTS ==========
  
  async searchDestinations(query: string) {
    return this.request(`/api/destinations/search/${encodeURIComponent(query)}`)
  }

  async getDestinationCategories() {
    return this.request("/api/destinations/categories/list")
  }

  // ========== CHATBOT ENDPOINTS ==========
  
  async sendChatMessage(message: string, context?: any) {
    return this.request("/api/chatbot/chat", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    })
  }

  async getChatbotHealth() {
    return this.request("/api/chatbot/health")
  }

  // ========== GALLERY ENDPOINTS ==========
  
  async getGallery(params?: {
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

    return this.request(`/api/gallery?${searchParams}`)
  }

  async getDestinationGallery(destinationId: string) {
    return this.request(`/api/gallery/destination/${destinationId}`)
  }

  async getFeaturedGallery() {
    return this.request("/api/gallery/featured")
  }

  async getGalleryHealth() {
    return this.request("/api/gallery/health")
  }

  // ========== STORIES/BLOG ENDPOINTS ==========
  
  async getStories(params?: {
    category?: string
    tag?: string
    search?: string
    featured?: boolean
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

    return this.request(`/api/stories?${searchParams}`)
  }

  async getFeaturedStories() {
    return this.request("/api/stories/featured")
  }

  async getTrendingStories() {
    return this.request("/api/stories/trending")
  }

  async getStoryBySlug(slug: string) {
    return this.request(`/api/stories/${slug}`)
  }

  async getStoriesHealth() {
    return this.request("/api/stories/health")
  }

  // ========== NEWSLETTER ENDPOINTS ==========
  
  async subscribeToNewsletter(email: string) {
    return this.request("/api/newsletter/subscribe", {
      method: "POST",
      body: JSON.stringify({ email }),
    })
  }

  async unsubscribeFromNewsletter(email: string, token?: string) {
    return this.request("/api/newsletter/unsubscribe", {
      method: "POST",
      body: JSON.stringify({ email, token }),
    })
  }

  // ========== TRAVEL PLANNING ENDPOINTS ==========
  
  // Legacy Planner
  async createTravelPlan(planData: {
    preferences: any
    trip_duration: number
    budget_range?: string
    interests?: string[]
  }) {
    return this.request("/api/planning/plan_trip", {
      method: "POST",
      body: JSON.stringify(planData),
    })
  }

  async createTravelPlanSync(planData: any) {
    return this.request("/api/planning/plan_trip_sync", {
      method: "POST",
      body: JSON.stringify(planData),
    })
  }

  async getTravelPlan(planId: string) {
    return this.request(`/api/planning/plan/${planId}`)
  }

  async refineTravelPlan(planId: string, refinements: any) {
    return this.request(`/api/planning/refine_plan/${planId}`, {
      method: "POST",
      body: JSON.stringify(refinements),
    })
  }

  async getPlanningStatus(planId: string) {
    return this.request(`/api/planning/status/${planId}`)
  }

  async getSimilarRecommendations(planId: string) {
    return this.request(`/api/planning/recommendations/similar/${planId}`)
  }

  async deleteTravelPlan(planId: string) {
    return this.request(`/api/planning/plan/${planId}`, {
      method: "DELETE",
    })
  }

  async getPlannerHealth() {
    return this.request("/api/planning/health")
  }

  // Advanced Clustered Planning
  async planTripClustered(planningData: {
    query: string
    interests: string[]
    trip_duration_days: number
    budget_level: 'budget' | 'mid_range' | 'luxury'
    max_attractions_per_day?: number
    daily_travel_preference?: 'minimal' | 'moderate' | 'extensive'
    trip_type?: 'solo' | 'couple' | 'family' | 'group'
    activity_level?: number
    group_size?: number
  }) {
    return this.request("/clustered-recommendations/plan", {
      method: "POST",
      body: JSON.stringify(planningData),
    })
  }

  async testClustering() {
    return this.request("/clustered-recommendations/test-clustering")
  }

  // Integrated Planning (with Places & AI)
  async planTripIntegratedFull(planningData: {
    query: string
    interests: string[]
    trip_duration_days: number
    budget_level: 'budget' | 'mid_range' | 'luxury'
    trip_type?: 'solo' | 'couple' | 'family' | 'group'
    activity_level?: number
    max_attractions_per_day?: number
    daily_travel_preference?: 'minimal' | 'moderate' | 'extensive'
    group_size?: number
    enhancements?: {
      places?: {
        enabled: boolean
        priority?: number
        config?: {
          search_radius_km?: number
          include_breakfast?: boolean
          include_lunch?: boolean
          include_dinner?: boolean
          include_accommodation?: boolean
          include_cafes?: boolean
        }
      }
    }
    async_processing?: boolean
  }) {
    return this.request("/integrated-planning/plan", {
      method: "POST",
      body: JSON.stringify(planningData),
    })
  }

  async planTripWithPlaces(params: {
    query: string
    interests: string[]
    trip_duration_days: number
    budget_level?: string
    daily_travel_preference?: string
    max_attractions_per_day?: number
    group_size?: number
    places_search_radius_km?: number
    include_breakfast?: boolean
    include_lunch?: boolean
    include_dinner?: boolean
    include_accommodation?: boolean
    include_cafes?: boolean
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v.toString()))
        } else {
          searchParams.append(key, value.toString())
        }
      }
    })

    return this.request(`/integrated-planning/plan-with-places?${searchParams}`, {
      method: "POST",
    })
  }

  async getEnhancementModules() {
    return this.request("/integrated-planning/enhancement-modules")
  }

  async testEnhancements() {
    return this.request("/integrated-planning/test-enhancements")
  }

  async validatePlanningRequest(requestData: any) {
    return this.request("/integrated-planning/validate-request", {
      method: "POST",
      body: JSON.stringify(requestData),
    })
  }

  // ========== GOOGLE PLACES ENDPOINTS ==========
  
  async searchPlaces(searchData: {
    lat: number
    lng: number
    place_type: string
    budget_level?: string
    radius_km?: number
    max_results?: number
    meal_type?: string
  }) {
    return this.request("/google-places/search", {
      method: "POST",
      body: JSON.stringify(searchData),
    })
  }

  async getRestaurants(params: {
    lat: number
    lng: number
    budget_level?: string
    meal_type?: string
    radius_km?: number
    max_results?: number
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    return this.request(`/google-places/restaurants?${searchParams}`)
  }

  async getHotels(params: {
    lat: number
    lng: number
    budget_level?: string
    radius_km?: number
    max_results?: number
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    return this.request(`/google-places/hotels?${searchParams}`)
  }

  async getCafes(params: {
    lat: number
    lng: number
    budget_level?: string
    radius_km?: number
    max_results?: number
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    return this.request(`/google-places/cafes?${searchParams}`)
  }

  async getDailyRecommendations(params: {
    lat: number
    lng: number
    budget_level?: string
    date?: string
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    return this.request(`/google-places/daily-recommendations?${searchParams}`)
  }

  async getPlaceDetails(placeId: string) {
    return this.request(`/google-places/place-details/${placeId}`)
  }

  async testGooglePlacesConnection() {
    return this.request("/google-places/test-connection")
  }

  // ========== PLACES ENHANCEMENT ENDPOINTS ==========
  
  async enhanceClusterWithPlaces(clusterData: {
    cluster_id: string
    center_lat: number
    center_lng: number
    attractions: any[]
    budget_level?: string
    day_number?: number
  }) {
    return this.request("/places-enhancement/enhance-cluster", {
      method: "POST",
      body: JSON.stringify(clusterData),
    })
  }

  async addPlacesToDay(params: {
    day: number
    center_lat: number
    center_lng: number
    budget_level?: string
    radius_km?: number
    include_breakfast?: boolean
    include_lunch?: boolean
    include_dinner?: boolean
    include_accommodation?: boolean
    include_cafes?: boolean
  }) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString())
      }
    })

    return this.request(`/places-enhancement/add-places-to-day?${searchParams}`, {
      method: "POST",
    })
  }

  async getPlacesForCoordinates(lat: number, lng: number, params?: {
    budget_level?: string
    radius_km?: number
    max_results?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/places-enhancement/places-for-coordinates/${lat}/${lng}?${searchParams}`)
  }

  async bulkEnhanceClusters(clusterPlans: any[], params?: {
    budget_level?: string
    radius_km?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/places-enhancement/bulk-enhance-clusters?${searchParams}`, {
      method: "POST",
      body: JSON.stringify(clusterPlans),
    })
  }

  async getEnhancementStats(clusterId: string) {
    return this.request(`/places-enhancement/enhancement-stats/${clusterId}`)
  }

  async testPlacesApi() {
    return this.request("/places-enhancement/test-places-api")
  }

  // ========== MY TRIPS ENDPOINTS ==========
  
  // Save a travel plan to user's trips
  async saveTravelPlan(planData: {
    title: string
    description?: string
    travel_plan_data: any
    original_query: string
    interests: string[]
    trip_duration_days: number
    budget_level: string
    trip_type: string
    planned_start_date?: string
    privacy?: 'private' | 'public' | 'shared'
  }) {
    return this.request("/api/my-trips/save-plan", {
      method: "POST",
      body: JSON.stringify(planData),
    })
  }

  // Get user's travel plans
  async getMyTravelPlans(params?: {
    status_filter?: 'draft' | 'active' | 'completed' | 'cancelled' | 'archived'
    privacy_filter?: 'private' | 'public' | 'shared'
    favorite_only?: boolean
    search?: string
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  }) {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString())
        }
      })
    }

    return this.request(`/api/my-trips?${searchParams}`)
  }

  // Get a specific travel plan
  async getTravelPlan(planId: string) {
    return this.request(`/api/my-trips/${planId}`)
  }

  // Update a travel plan
  async updateTravelPlan(planId: string, updates: {
    title?: string
    description?: string
    status?: 'draft' | 'active' | 'completed' | 'cancelled' | 'archived'
    privacy?: 'private' | 'public' | 'shared'
    user_rating?: number
    user_notes?: string
    favorite?: boolean
    planned_start_date?: string
    actual_start_date?: string
    actual_end_date?: string
  }) {
    return this.request(`/api/my-trips/${planId}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    })
  }

  // Delete (archive) a travel plan
  async deleteTravelPlan(planId: string) {
    return this.request(`/api/my-trips/${planId}`, {
      method: "DELETE",
    })
  }

  // Get travel plan statistics
  async getTravelPlanStats() {
    return this.request("/api/my-trips/stats/overview")
  }

  // Generate PDF for a travel plan
  async generateTravelPlanPDF(planId: string, options?: {
    include_maps?: boolean
    include_photos?: boolean
    include_weather?: boolean
    custom_title?: string
  }) {
    const pdfRequest = {
      travel_plan_id: planId,
      include_maps: options?.include_maps ?? true,
      include_photos: options?.include_photos ?? true,
      include_weather: options?.include_weather ?? true,
      custom_title: options?.custom_title
    }

    return this.request(`/api/my-trips/${planId}/generate-pdf`, {
      method: "POST",
      body: JSON.stringify(pdfRequest),
    })
  }

  // Download PDF for a travel plan
  async downloadTravelPlanPDF(planId: string) {
    const url = `${this.baseURL}/api/my-trips/${planId}/download-pdf`
    const token = this.getAuthToken()

    const response = await fetch(url, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to download PDF: ${response.status}`)
    }

    return response.blob()
  }

  // Toggle favorite status
  async toggleTravelPlanFavorite(planId: string) {
    return this.request(`/api/my-trips/${planId}/toggle-favorite`, {
      method: "POST",
    })
  }

  // Auto-save from planning (called automatically after plan generation)
  async autoSaveFromPlanning(planData: any) {
    return this.request("/api/my-trips/auto-save-from-planning", {
      method: "POST",
      body: JSON.stringify(planData),
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient
