"use client"

import { useState } from 'react'
import { 
  MapPin, 
  Clock, 
  Star, 
  Camera, 
  Calendar, 
  Users, 
  DollarSign, 
  Route,
  Utensils,
  Hotel,
  Coffee,
  Download,
  Save,
  Share2,
  ArrowRight,
  Timer,
  Target,
  Activity
} from 'lucide-react'

// Type definitions for the backend response
interface Attraction {
  id: string
  name: string
  category: string
  description: string
  region: string
  latitude: number
  longitude: number
  pear_score: number
  visit_order: number
}

interface ClusterInfo {
  cluster_id: number
  region_name: string
  center_lat: number
  center_lng: number
  total_attractions: number
  total_pear_score: number
  estimated_time_hours: number
  travel_time_minutes: number
  value_per_hour: number
  is_balanced: boolean
  optimal_visiting_order: number[]
}

interface PlaceRecommendations {
  day: number
  cluster_center_lat: number
  cluster_center_lng: number
  breakfast_places: any[]
  lunch_places: any[]
  dinner_places: any[]
  accommodation: any[]
  cafes: any[]
}

interface DailyItinerary {
  day: number
  cluster_info: ClusterInfo
  attractions: Attraction[]
  total_travel_distance_km: number
  estimated_total_time_hours: number
  place_recommendations: PlaceRecommendations
}

interface PlacesStats {
  success: boolean
  processing_time_ms: number
  data_added: number
  total_places_added: number
  restaurants: number
  accommodations: number
}

interface TravelPlanData {
  query: string
  total_days: number
  total_attractions: number
  daily_itineraries: DailyItinerary[]
  places_stats: PlacesStats
  processing_time_ms: number
  enhancements_applied: string[]
}

interface TravelPlanDisplayProps {
  planData: TravelPlanData
  onSave?: () => void
  onDownload?: () => void
  onShare?: () => void
  loading?: {
    saving?: boolean
    downloading?: boolean
  }
  isAuthenticated?: boolean
  savedPlanId?: string | null
}

const categoryIcons: { [key: string]: string } = {
  beach: '🏖️',
  nature: '🌿',
  wildlife: '🦎',
  adventure: '🏔️',
  cultural: '🏛️',
  historical: '🏺',
  accommodation: '🏨',
  restaurant: '🍽️',
  default: '📍'
}

const categoryColors: { [key: string]: string } = {
  beach: 'bg-blue-100 text-blue-800',
  nature: 'bg-green-100 text-green-800',
  wildlife: 'bg-yellow-100 text-yellow-800',
  adventure: 'bg-red-100 text-red-800',
  cultural: 'bg-purple-100 text-purple-800',
  historical: 'bg-amber-100 text-amber-800',
  accommodation: 'bg-indigo-100 text-indigo-800',
  restaurant: 'bg-orange-100 text-orange-800',
  default: 'bg-gray-100 text-gray-800'
}

export default function TravelPlanDisplay({ 
  planData, 
  onSave, 
  onDownload, 
  onShare,
  loading = {},
  isAuthenticated = false,
  savedPlanId = null
}: TravelPlanDisplayProps) {
  const [selectedDay, setSelectedDay] = useState<number | null>(null)
  const [showPlaces, setShowPlaces] = useState(false)

  const formatTime = (hours: number) => {
    const h = Math.floor(hours)
    const m = Math.round((hours - h) * 60)
    return h > 0 ? `${h}h ${m}m` : `${m}m`
  }

  const formatDistance = (km: number) => {
    return km > 1 ? `${km.toFixed(1)}km` : `${(km * 1000).toFixed(0)}m`
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score >= 0.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const renderOverviewStats = () => (
    <div className="bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl p-6 mb-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="w-12 h-12 bg-teal-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <Calendar className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{planData.total_days}</div>
          <div className="text-sm text-gray-600">Days</div>
        </div>
        
        <div className="text-center">
          <div className="w-12 h-12 bg-cyan-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <MapPin className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{planData.total_attractions}</div>
          <div className="text-sm text-gray-600">Attractions</div>
        </div>
        
        <div className="text-center">
          <div className="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <Timer className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatTime(planData.daily_itineraries.reduce((sum, day) => sum + day.estimated_total_time_hours, 0))}
          </div>
          <div className="text-sm text-gray-600">Total Time</div>
        </div>
        
        <div className="text-center">
          <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <Route className="w-6 h-6 text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatDistance(planData.daily_itineraries.reduce((sum, day) => sum + day.total_travel_distance_km, 0))}
          </div>
          <div className="text-sm text-gray-600">Total Distance</div>
        </div>
      </div>
    </div>
  )

  const renderDayOverview = () => (
    <div className="mb-8">
      <h3 className="text-xl font-semibold mb-4">Trip Overview</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {planData.daily_itineraries.map((day) => (
          <div 
            key={day.day}
            className={`bg-white border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedDay === day.day 
                ? 'border-teal-500 bg-teal-50' 
                : 'border-gray-200 hover:border-teal-300'
            }`}
            onClick={() => setSelectedDay(selectedDay === day.day ? null : day.day)}
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold">Day {day.day}</h4>
              <div className="text-sm text-gray-600">
                {day.cluster_info.region_name}
              </div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Attractions:</span>
                <span className="font-medium">{day.attractions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Duration:</span>
                <span className="font-medium">{formatTime(day.estimated_total_time_hours)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Travel:</span>
                <span className="font-medium">{formatDistance(day.total_travel_distance_km)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Score:</span>
                <span className={`font-medium ${getScoreColor(day.cluster_info.value_per_hour)}`}>
                  {day.cluster_info.value_per_hour.toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex flex-wrap gap-1">
                {day.attractions.slice(0, 3).map((attraction) => (
                  <span 
                    key={attraction.id}
                    className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                      categoryColors[attraction.category] || categoryColors.default
                    }`}
                  >
                    {categoryIcons[attraction.category] || categoryIcons.default}
                    <span className="ml-1">{attraction.category}</span>
                  </span>
                ))}
                {day.attractions.length > 3 && (
                  <span className="text-xs text-gray-500">+{day.attractions.length - 3}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderDayDetails = (dayData: DailyItinerary) => (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">Day {dayData.day}</h3>
          <p className="text-gray-600">{dayData.cluster_info.region_name}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">Efficiency Score</div>
          <div className={`text-2xl font-bold ${getScoreColor(dayData.cluster_info.value_per_hour)}`}>
            {dayData.cluster_info.value_per_hour.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Day Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">{dayData.attractions.length}</div>
          <div className="text-sm text-gray-600">Attractions</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">{formatTime(dayData.estimated_total_time_hours)}</div>
          <div className="text-sm text-gray-600">Total Time</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-900">{formatDistance(dayData.total_travel_distance_km)}</div>
          <div className="text-sm text-gray-600">Travel Distance</div>
        </div>
      </div>

      {/* Attractions List */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold">Attractions ({dayData.attractions.length})</h4>
        {dayData.attractions
          .sort((a, b) => a.visit_order - b.visit_order)
          .map((attraction, index) => (
          <div key={attraction.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-10 h-10 bg-teal-500 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">
              {attraction.visit_order}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h5 className="text-lg font-semibold text-gray-900 mb-1">{attraction.name}</h5>
                  {attraction.description && (
                    <p className="text-gray-600 text-sm mb-2">{attraction.description}</p>
                  )}
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      {attraction.region || 'Unknown region'}
                    </div>
                    <div className="flex items-center">
                      <Target className="w-4 h-4 mr-1" />
                      Score: {attraction.pear_score.toFixed(3)}
                    </div>
                  </div>
                </div>
                
                <div className="shrink-0 ml-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                    categoryColors[attraction.category] || categoryColors.default
                  }`}>
                    {categoryIcons[attraction.category] || categoryIcons.default}
                    <span className="ml-1 capitalize">{attraction.category}</span>
                  </span>
                </div>
              </div>
              
              {index < dayData.attractions.length - 1 && (
                <div className="mt-3 flex items-center text-sm text-gray-500">
                  <ArrowRight className="w-4 h-4 mr-2" />
                  <span>Next destination</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Places Recommendations */}
      {(dayData.place_recommendations.breakfast_places.length > 0 ||
        dayData.place_recommendations.lunch_places.length > 0 ||
        dayData.place_recommendations.dinner_places.length > 0 ||
        dayData.place_recommendations.accommodation.length > 0 ||
        dayData.place_recommendations.cafes.length > 0) && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold">Place Recommendations</h4>
            <button
              onClick={() => setShowPlaces(!showPlaces)}
              className="text-teal-600 hover:text-teal-700 text-sm font-medium"
            >
              {showPlaces ? 'Hide' : 'Show'} Places
            </button>
          </div>
          
          {showPlaces && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {dayData.place_recommendations.breakfast_places.length > 0 && (
                <div className="bg-amber-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Utensils className="w-4 h-4 text-amber-600 mr-2" />
                    <span className="font-medium text-amber-800">Breakfast</span>
                  </div>
                  <div className="text-sm text-amber-700">
                    {dayData.place_recommendations.breakfast_places.length} options
                  </div>
                </div>
              )}
              
              {dayData.place_recommendations.lunch_places.length > 0 && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Utensils className="w-4 h-4 text-green-600 mr-2" />
                    <span className="font-medium text-green-800">Lunch</span>
                  </div>
                  <div className="text-sm text-green-700">
                    {dayData.place_recommendations.lunch_places.length} options
                  </div>
                </div>
              )}
              
              {dayData.place_recommendations.dinner_places.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Utensils className="w-4 h-4 text-red-600 mr-2" />
                    <span className="font-medium text-red-800">Dinner</span>
                  </div>
                  <div className="text-sm text-red-700">
                    {dayData.place_recommendations.dinner_places.length} options
                  </div>
                </div>
              )}
              
              {dayData.place_recommendations.accommodation.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Hotel className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="font-medium text-blue-800">Hotels</span>
                  </div>
                  <div className="text-sm text-blue-700">
                    {dayData.place_recommendations.accommodation.length} options
                  </div>
                </div>
              )}
              
              {dayData.place_recommendations.cafes.length > 0 && (
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Coffee className="w-4 h-4 text-purple-600 mr-2" />
                    <span className="font-medium text-purple-800">Cafes</span>
                  </div>
                  <div className="text-sm text-purple-700">
                    {dayData.place_recommendations.cafes.length} options
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )

  const renderEnhancementStats = () => (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4">Plan Enhancement Stats</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {planData.places_stats.success ? '✓' : '✗'}
          </div>
          <div className="text-sm text-gray-600">Places Enhancement</div>
        </div>
        
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(planData.places_stats.processing_time_ms)}ms
          </div>
          <div className="text-sm text-gray-600">Processing Time</div>
        </div>
        
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {planData.places_stats.restaurants}
          </div>
          <div className="text-sm text-gray-600">Restaurants</div>
        </div>
        
        <div className="text-center p-4 bg-indigo-50 rounded-lg">
          <div className="text-2xl font-bold text-indigo-600">
            {planData.places_stats.accommodations}
          </div>
          <div className="text-sm text-gray-600">Hotels</div>
        </div>
      </div>
      
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Enhancements Applied:</span>
          <div className="flex space-x-2">
            {planData.enhancements_applied.map((enhancement) => (
              <span 
                key={enhancement}
                className="px-2 py-1 bg-teal-100 text-teal-800 rounded-full text-xs"
              >
                {enhancement}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const renderActionButtons = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex flex-col sm:flex-row gap-4">
        {isAuthenticated ? (
          <>
            {onSave && !savedPlanId && (
              <button
                onClick={onSave}
                disabled={loading.saving}
                className="btn-primary flex items-center justify-center space-x-2"
              >
                {loading.saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save Plan</span>
                  </>
                )}
              </button>
            )}
            
            {onDownload && savedPlanId && (
              <button
                onClick={onDownload}
                disabled={loading.downloading}
                className="btn-secondary flex items-center justify-center space-x-2"
              >
                {loading.downloading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-teal-600 border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating PDF...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Download PDF</span>
                  </>
                )}
              </button>
            )}
            
            {onShare && (
              <button
                onClick={onShare}
                className="btn-secondary flex items-center justify-center space-x-2"
              >
                <Share2 className="w-4 h-4" />
                <span>Share Plan</span>
              </button>
            )}
          </>
        ) : (
          <div className="text-center p-4 bg-blue-50 rounded-lg w-full">
            <p className="text-blue-800 text-sm mb-2">
              <strong>Sign in to save your plans and generate PDFs!</strong>
            </p>
            <button className="btn-primary">
              Sign In
            </button>
          </div>
        )}
      </div>
      
      {savedPlanId && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg text-center">
          <p className="text-green-800 text-sm">
            ✅ Plan saved successfully! You can find it in your trips.
          </p>
        </div>
      )}
    </div>
  )

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-poppins font-bold mb-4">Your Personalized Travel Plan</h2>
        <p className="text-gray-600 text-lg">
          Generated in {Math.round(planData.processing_time_ms / 1000)}s • Based on: "{planData.query}"
        </p>
      </div>

      {/* Overview Stats */}
      {renderOverviewStats()}

      {/* Enhancement Stats */}
      {renderEnhancementStats()}

      {/* Day Overview */}
      {renderDayOverview()}

      {/* Detailed Day Plans */}
      <div>
        <h3 className="text-xl font-semibold mb-6">Detailed Itinerary</h3>
        {selectedDay ? (
          <div>
            {renderDayDetails(planData.daily_itineraries.find(d => d.day === selectedDay)!)}
            <div className="text-center">
              <button
                onClick={() => setSelectedDay(null)}
                className="btn-secondary"
              >
                Show All Days
              </button>
            </div>
          </div>
        ) : (
          planData.daily_itineraries.map((dayData) => renderDayDetails(dayData))
        )}
      </div>

      {/* Action Buttons */}
      {renderActionButtons()}
    </div>
  )
}
