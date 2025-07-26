"use client"

import { useState, useEffect } from "react"
import { Search, MapPin, Star, Clock, Phone, Globe, DollarSign, Filter, X } from "lucide-react"
import { apiClient } from "@/lib/api"
import { PlaceRecommendation } from "@/lib/types"
import ClientOnly from "../ClientOnly"
import HydrationSafeInput from "../HydrationSafeInput"

interface PlacesSearchProps {
  defaultLocation?: { lat: number; lng: number; name?: string }
  placeTypes?: string[]
  onPlaceSelect?: (place: PlaceRecommendation) => void
}

const placeTypeOptions = [
  { value: "restaurant", label: "Restaurants", icon: "🍽️" },
  { value: "lodging", label: "Hotels", icon: "🏨" },
  { value: "tourist_attraction", label: "Attractions", icon: "🏛️" },
  { value: "cafe", label: "Cafes", icon: "☕" },
]

const budgetLevels = [
  { value: "budget", label: "Budget", icon: "💰" },
  { value: "medium", label: "Medium", icon: "💎" },
  { value: "luxury", label: "Luxury", icon: "✨" },
]

const mealTypes = [
  { value: "breakfast", label: "Breakfast" },
  { value: "lunch", label: "Lunch" },
  { value: "dinner", label: "Dinner" },
]

export default function PlacesSearch({ 
  defaultLocation, 
  placeTypes = ["restaurant", "lodging", "tourist_attraction", "cafe"],
  onPlaceSelect 
}: PlacesSearchProps) {
  const [location, setLocation] = useState(defaultLocation || { lat: 7.2906, lng: 80.6337, name: "Kandy" })
  const [selectedType, setSelectedType] = useState("restaurant")
  const [budgetLevel, setBudgetLevel] = useState("medium")
  const [mealType, setMealType] = useState("")
  const [radius, setRadius] = useState(5)
  const [maxResults, setMaxResults] = useState(10)
  const [places, setPlaces] = useState<PlaceRecommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    if (location.lat && location.lng) {
      searchPlaces()
    }
  }, [location, selectedType, budgetLevel, mealType, radius])

  const searchPlaces = async () => {
    setLoading(true)
    setError(null)

    try {
      let response
      
      if (selectedType === "restaurant") {
        response = await apiClient.getRestaurants({
          lat: location.lat,
          lng: location.lng,
          budget_level: budgetLevel,
          meal_type: mealType || undefined,
          radius_km: radius,
          max_results: maxResults
        })
      } else if (selectedType === "lodging") {
        response = await apiClient.getHotels({
          lat: location.lat,
          lng: location.lng,
          budget_level: budgetLevel,
          radius_km: radius,
          max_results: maxResults
        })
      } else if (selectedType === "cafe") {
        response = await apiClient.getCafes({
          lat: location.lat,
          lng: location.lng,
          budget_level: budgetLevel,
          radius_km: radius,
          max_results: maxResults
        })
      } else {
        response = await apiClient.searchPlaces({
          lat: location.lat,
          lng: location.lng,
          place_type: selectedType,
          budget_level: budgetLevel,
          radius_km: radius,
          max_results: maxResults
        })
      }

      setPlaces((response as any)?.places || (response as any)?.restaurants || (response as any)?.hotels || (response as any)?.cafes || [])
    } catch (err) {
      console.error("Places search error:", err)
      setError("Failed to search places. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      setLoading(true)
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            name: "Current Location"
          })
        },
        (error) => {
          console.error("Geolocation error:", error)
          setError("Could not get current location")
          setLoading(false)
        }
      )
    } else {
      setError("Geolocation is not supported by this browser")
    }
  }

  const filteredPlaces = places.filter(place =>
    place.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    place.address.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const renderStarRating = (rating?: number) => {
    if (!rating) return null
    
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 >= 0.5

    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />)
    }

    if (hasHalfStar) {
      stars.push(<Star key="half" className="w-4 h-4 fill-yellow-400/50 text-yellow-400" />)
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />)
    }

    return (
      <div className="flex items-center space-x-1">
        {stars}
        <span className="text-sm text-gray-600 ml-1">({rating.toFixed(1)})</span>
      </div>
    )
  }

  const renderPriceLevel = (priceLevel?: number) => {
    if (!priceLevel) return null
    
    const dollarSigns = []
    for (let i = 0; i < priceLevel; i++) {
      dollarSigns.push(<DollarSign key={i} className="w-3 h-3 fill-green-500 text-green-500" />)
    }
    
    const emptyDollarSigns = 4 - priceLevel
    for (let i = 0; i < emptyDollarSigns; i++) {
      dollarSigns.push(<DollarSign key={`empty-${i}`} className="w-3 h-3 text-gray-300" />)
    }

    return <div className="flex">{dollarSigns}</div>
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white p-6">
        <h2 className="text-2xl font-poppins font-bold mb-2">Discover Places</h2>
        <p className="text-teal-100">Find restaurants, hotels, and attractions near you</p>
      </div>

      {/* Filters */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Search Filters</h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary text-sm"
          >
            <Filter className="w-4 h-4 mr-2" />
            {showFilters ? "Hide" : "Show"} Filters
          </button>
        </div>

        {/* Location Input */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
            <div className="flex space-x-2">
              <ClientOnly>
                <HydrationSafeInput
                  type="text"
                  value={location.name || `${location.lat}, ${location.lng}`}
                  onChange={(e) => setLocation({ ...location, name: e.target.value })}
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="Enter location"
                />
              </ClientOnly>
              <button
                onClick={getCurrentLocation}
                className="px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                title="Use current location"
              >
                <MapPin className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <ClientOnly>
                <HydrationSafeInput
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="Search places..."
                />
              </ClientOnly>
            </div>
          </div>
        </div>

        {/* Place Type Selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {placeTypeOptions
              .filter(type => placeTypes.includes(type.value))
              .map((type) => (
                <button
                  key={type.value}
                  onClick={() => setSelectedType(type.value)}
                  className={`p-3 rounded-lg border text-sm font-medium transition-all duration-200 ${
                    selectedType === type.value
                      ? "bg-teal-500 text-white border-teal-500"
                      : "bg-white text-gray-700 border-gray-300 hover:border-teal-300"
                  }`}
                >
                  <span className="mr-2">{type.icon}</span>
                  {type.label}
                </button>
              ))}
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="space-y-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Budget Level</label>
                <select
                  value={budgetLevel}
                  onChange={(e) => setBudgetLevel(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  {budgetLevels.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.icon} {level.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Radius (km)</label>
                <select
                  value={radius}
                  onChange={(e) => setRadius(parseInt(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  {[1, 2, 5, 10, 15, 20].map((km) => (
                    <option key={km} value={km}>{km} km</option>
                  ))}
                </select>
              </div>

              {selectedType === "restaurant" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Meal Type</label>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="">Any meal</option>
                    {mealTypes.map((meal) => (
                      <option key={meal.value} value={meal.value}>
                        {meal.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div className="p-6">
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          </div>
        )}

        {error && (
          <div className="text-center py-12">
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={searchPlaces}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        )}

        {!loading && !error && filteredPlaces.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No places found. Try adjusting your search criteria.</p>
          </div>
        )}

        {!loading && !error && filteredPlaces.length > 0 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-gray-900">
                Found {filteredPlaces.length} places
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredPlaces.map((place) => (
                <div
                  key={place.place_id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200 cursor-pointer"
                  onClick={() => onPlaceSelect?.(place)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-semibold text-gray-900 pr-2">{place.name}</h4>
                    {renderPriceLevel(place.price_level)}
                  </div>

                  <div className="space-y-2">
                    {place.rating && renderStarRating(place.rating)}

                    <div className="flex items-start text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      <span>{place.address}</span>
                    </div>

                    {place.phone_number && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Phone className="w-4 h-4 mr-2 flex-shrink-0" />
                        <span>{place.phone_number}</span>
                      </div>
                    )}

                    {place.website && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Globe className="w-4 h-4 mr-2 flex-shrink-0" />
                        <a 
                          href={place.website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-teal-600 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Visit Website
                        </a>
                      </div>
                    )}

                    {place.opening_hours && place.opening_hours.length > 0 && (
                      <div className="flex items-start text-sm text-gray-600">
                        <Clock className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <div>
                          <div>{place.opening_hours[0]}</div>
                          {place.opening_hours.length > 1 && (
                            <div className="text-xs text-gray-500">
                              +{place.opening_hours.length - 1} more
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <span className="inline-block px-2 py-1 bg-teal-50 text-teal-700 text-xs rounded-full">
                      {place.place_type?.replace("_", " ") || "Place"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
