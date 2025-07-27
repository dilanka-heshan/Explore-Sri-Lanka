"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Search, Filter, MapPin, Star, Map } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useDestinationTypes } from "@/lib/hooks/useDestinationTypes"
import { Destination } from "@/lib/types"

const staticFilters = {
  regions: ["All", "Central", "Southern", "Northern", "Eastern", "Western", "North Central"],
  seasons: ["All", "Year-round", "Nov-Apr", "Apr-Oct", "Feb-Jul", "May-Sep"],
}

export default function DestinationsPage() {
  const [destinations, setDestinations] = useState<Destination[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedRegion, setSelectedRegion] = useState("All")
  const [selectedType, setSelectedType] = useState("All")
  const [selectedSeason, setSelectedSeason] = useState("All")
  const [showMap, setShowMap] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  
  // Get dynamic destination types from database
  const { destinationTypes, loading: typesLoading } = useDestinationTypes()
  
  // Create dynamic filters object
  const filters = {
    regions: staticFilters.regions,
    types: ["All", ...destinationTypes],
    seasons: staticFilters.seasons,
  }

  useEffect(() => {
    fetchDestinations()
  }, [selectedRegion, selectedType, searchTerm])

  const fetchDestinations = async () => {
    try {
      setLoading(true)
      const params = {
        region: selectedRegion !== "All" ? selectedRegion : undefined,
        destination_type: selectedType !== "All" ? selectedType : undefined,
        search: searchTerm || undefined,
        limit: 50,
      }

      const data = await apiClient.getDestinations(params) as Destination[]
      setDestinations(data)
    } catch (error) {
      console.error("Failed to fetch destinations:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredDestinations = destinations.filter((destination) => {
    const matchesSeason = selectedSeason === "All" || destination.bestTimeToVisit === selectedSeason
    return matchesSeason
  })

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading destinations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="relative py-24 bg-gradient-to-r from-teal-600 to-cyan-600 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20" />
        <div className="container-custom relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-poppins font-bold mb-6 animate-fade-in">Discover Sri Lanka</h1>
            <p className="text-xl md:text-2xl text-teal-100 animate-slide-up animation-delay-200">
              From ancient wonders to pristine beaches, explore the pearl of the Indian Ocean
            </p>
          </div>
        </div>
      </section>

      {/* Search and Filters */}
      <section className="py-8 bg-white border-b border-gray-200 sticky top-20 z-40">
        <div className="container-custom">
          <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
            {/* Search Bar */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search destinations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            {/* Filter Toggle */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <Filter className="w-5 h-5" />
                <span>Filters</span>
              </button>

              <button
                onClick={() => setShowMap(!showMap)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
                  showMap ? "bg-teal-600 text-white" : "border border-gray-300 hover:bg-gray-50"
                }`}
              >
                <Map className="w-5 h-5" />
                <span>{showMap ? "Hide Map" : "Show Map"}</span>
              </button>
            </div>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="mt-6 p-6 bg-gray-50 rounded-lg animate-slide-up">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
                  <select
                    value={selectedRegion}
                    onChange={(e) => setSelectedRegion(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {filters.regions.map((region) => (
                      <option key={region} value={region}>
                        {region}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {filters.types.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Best Season</label>
                  <select
                    value={selectedSeason}
                    onChange={(e) => setSelectedSeason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                  >
                    {filters.seasons.map((season) => (
                      <option key={season} value={season}>
                        {season}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Map View */}
      {showMap && (
        <section className="py-8 bg-gray-100">
          <div className="container-custom">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="h-96 bg-gradient-to-br from-teal-100 to-cyan-100 flex items-center justify-center">
                <div className="text-center">
                  <MapPin className="w-16 h-16 text-teal-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Interactive Map</h3>
                  <p className="text-gray-600">Map integration would be implemented here</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Destinations Grid */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-poppins font-bold text-gray-900">
              {filteredDestinations.length} Destinations Found
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredDestinations.map((destination, index) => (
              <Link
                key={destination.id}
                href={`/destinations/${destination.id}`}
                className="group animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover">
                  <div className="relative">
                    <img
                      src={destination.image || "/placeholder.svg"}
                      alt={destination.name}
                      className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-gray-700">
                      {destination.type || destination.category}
                    </div>
                    <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-medium text-gray-700">{destination.rating}</span>
                    </div>
                    <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm">
                      {destination.region}
                    </div>
                  </div>

                  <div className="p-6">
                    <h3 className="text-xl font-poppins font-semibold mb-2 group-hover:text-teal-600 transition-colors duration-200">
                      {destination.name}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-2">{destination.description}</p>

                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <span>★ {destination.rating || 'No rating'}</span>
                      <span>Best: {destination.bestTimeToVisit || 'Year-round'}</span>
                    </div>

                    {destination.activities && destination.activities.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-medium text-gray-900">Highlights:</h4>
                        <div className="flex flex-wrap gap-1">
                          {destination.activities.slice(0, 3).map((activity: string, idx: number) => (
                            <span key={idx} className="px-2 py-1 bg-teal-50 text-teal-700 text-xs rounded-full">
                              {activity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {filteredDestinations.length === 0 && (
            <div className="text-center py-16">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No destinations found</h3>
              <p className="text-gray-600 mb-6">Try adjusting your search criteria or filters</p>
              <button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedRegion("All")
                  setSelectedType("All")
                  setSelectedSeason("All")
                }}
                className="btn-primary"
              >
                Clear All Filters
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
