// Planning and Travel related types

export interface TravelPreferences {
  trip_duration_days: number
  budget_level: 'budget' | 'mid_range' | 'luxury'
  trip_type: 'solo' | 'couple' | 'family' | 'group'
  activity_level: number // 1-5 scale
  daily_travel_preference: 'minimal' | 'moderate' | 'extensive'
  group_size: number
  max_attractions_per_day?: number
  interests: string[]
}

export interface PlanningRequest {
  query: string
  interests: string[]
  trip_duration_days: number
  budget_level: 'budget' | 'mid_range' | 'luxury'
  trip_type?: 'solo' | 'couple' | 'family' | 'group'
  activity_level?: number
  max_attractions_per_day?: number
  daily_travel_preference?: 'minimal' | 'moderate' | 'extensive'
  group_size?: number
}

export interface Attraction {
  id: string
  name: string
  description: string
  location: {
    latitude: number
    longitude: number
    address?: string
    city?: string
    region?: string
  }
  category: string
  rating?: number
  price_level?: 'budget' | 'mid_range' | 'luxury'
  duration_hours?: number
  best_visit_time?: string
  tags?: string[]
  images?: string[]
}

export interface PlaceRecommendation {
  place_id: string
  name: string
  address: string
  location: {
    lat: number
    lng: number
  }
  rating?: number
  price_level?: number
  place_type: string
  opening_hours?: string[]
  photos?: string[]
  phone_number?: string
  website?: string
  reviews?: any[]
}

export interface DailyItinerary {
  day: number
  date?: string
  attractions: Attraction[]
  restaurants?: PlaceRecommendation[]
  accommodation?: PlaceRecommendation[]
  cafes?: PlaceRecommendation[]
  total_travel_time?: number
  total_distance_km?: number
  estimated_cost?: number
  notes?: string
}

export interface GeneratedTravelPlan {
  id: string
  name?: string
  description?: string
  total_days: number
  budget_level: string
  estimated_total_cost?: number
  daily_itineraries: DailyItinerary[]
  route_optimization?: {
    total_distance_km: number
    total_travel_time_hours: number
    optimization_method: string
  }
  created_at?: string
  updated_at?: string
}

export interface ClusteredRecommendation {
  cluster_id: string
  day: number
  attractions: Attraction[]
  center_location: {
    latitude: number
    longitude: number
  }
  radius_km: number
  total_attractions: number
  estimated_time_hours: number
  travel_routes?: any[]
}

export interface IntegratedPlanningResponse {
  plan_id: string
  query: string
  preferences: TravelPreferences
  clustered_plan: ClusteredRecommendation[]
  enhanced_plan?: GeneratedTravelPlan
  places_recommendations?: {
    [key: string]: {
      restaurants: PlaceRecommendation[]
      accommodation: PlaceRecommendation[]
      cafes: PlaceRecommendation[]
    }
  }
  ai_insights?: string
  processing_time_seconds: number
  enhancement_results?: {
    places_status: 'success' | 'error' | 'partial'
    weather_status?: 'success' | 'error' | 'partial'
    transport_status?: 'success' | 'error' | 'partial'
  }
}

export interface EnhancementConfig {
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
  weather?: {
    enabled: boolean
    priority?: number
    config?: {
      forecast_days?: number
    }
  }
  transport?: {
    enabled: boolean
    priority?: number
    config?: {
      include_local_transport?: boolean
    }
  }
}

export interface IntegratedPlanningRequest extends PlanningRequest {
  enhancements?: EnhancementConfig
  async_processing?: boolean
}

export interface PlanningStatus {
  plan_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress_percentage: number
  current_stage?: string
  estimated_completion_time?: string
  error_message?: string
}

// Google Places specific types
export interface PlaceSearchRequest {
  lat: number
  lng: number
  place_type: 'restaurant' | 'lodging' | 'tourist_attraction' | 'cafe'
  budget_level?: 'budget' | 'medium' | 'luxury'
  radius_km?: number
  max_results?: number
  meal_type?: 'breakfast' | 'lunch' | 'dinner'
}

export interface PlaceSearchResponse {
  query: PlaceSearchRequest
  places: PlaceRecommendation[]
  total_found: number
  search_time_ms: number
}

export interface DailyPlaceRecommendations {
  day: number
  date?: string
  breakfast_places: PlaceRecommendation[]
  lunch_places: PlaceRecommendation[]
  dinner_places: PlaceRecommendation[]
  accommodation_options: PlaceRecommendation[]
  cafe_options: PlaceRecommendation[]
  total_places: number
}

// Clustering specific types
export interface GeographicCluster {
  cluster_id: string
  center_lat: number
  center_lng: number
  radius_km: number
  attractions: Attraction[]
  cluster_score: number
  estimated_time_hours: number
  day_assignment?: number
}

export interface ClusteringResult {
  total_clusters: number
  clusters: GeographicCluster[]
  optimization_method: string
  total_attractions: number
  clustering_time_ms: number
}

export interface RouteOptimization {
  route_id: string
  waypoints: Array<{
    attraction_id: string
    order: number
    location: { lat: number; lng: number }
    arrival_time?: string
    departure_time?: string
  }>
  total_distance_km: number
  total_time_hours: number
  optimization_method: string
}
