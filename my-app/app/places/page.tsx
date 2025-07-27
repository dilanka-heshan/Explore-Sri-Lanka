"use client"

import { useState } from "react"
import { MapPin, Search, Filter } from "lucide-react"
import PlacesSearch from "@/components/places/places-search"
import { PlaceRecommendation } from "@/lib/types"

export default function PlacesPage() {
  const [selectedPlace, setSelectedPlace] = useState<PlaceRecommendation | null>(null)

  const handlePlaceSelect = (place: PlaceRecommendation) => {
    setSelectedPlace(place)
  }

  return (
    <div className="min-h-screen pt-20 bg-gray-50">
      {/* Hero Section */}
      <section className="relative py-16 bg-gradient-to-r from-teal-600 to-cyan-600 text-white">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-poppins font-bold mb-6">
              Discover Amazing Places
            </h1>
            <p className="text-xl text-teal-100 mb-8">
              Find the best restaurants, hotels, and attractions powered by Google Places
            </p>
            <div className="flex items-center justify-center space-x-6 text-teal-100">
              <div className="flex items-center">
                <Search className="w-5 h-5 mr-2" />
                <span>Smart Search</span>
              </div>
              <div className="flex items-center">
                <MapPin className="w-5 h-5 mr-2" />
                <span>Real-time Data</span>
              </div>
              <div className="flex items-center">
                <Filter className="w-5 h-5 mr-2" />
                <span>Advanced Filters</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Places Search */}
            <div className="lg:col-span-2">
              <PlacesSearch 
                onPlaceSelect={handlePlaceSelect}
                placeTypes={["restaurant", "lodging", "tourist_attraction", "cafe"]}
              />
            </div>

            {/* Selected Place Details */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden sticky top-24">
                {selectedPlace ? (
                  <div className="p-6">
                    <h3 className="text-xl font-poppins font-bold mb-4">Place Details</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-semibold text-lg">{selectedPlace.name}</h4>
                        <p className="text-gray-600">{selectedPlace.address}</p>
                      </div>

                      {selectedPlace.rating && (
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">Rating:</span>
                          <div className="flex items-center">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <svg
                                key={star}
                                className={`w-4 h-4 ${
                                  star <= Math.floor(selectedPlace.rating!)
                                    ? "text-yellow-400 fill-current"
                                    : "text-gray-300"
                                }`}
                                viewBox="0 0 20 20"
                              >
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                            ))}
                            <span className="ml-1 text-sm text-gray-600">
                              ({selectedPlace.rating.toFixed(1)})
                            </span>
                          </div>
                        </div>
                      )}

                      {selectedPlace.price_level && (
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">Price Level:</span>
                          <div className="flex">
                            {[1, 2, 3, 4].map((level) => (
                              <span
                                key={level}
                                className={`text-lg ${
                                  level <= selectedPlace.price_level!
                                    ? "text-green-500"
                                    : "text-gray-300"
                                }`}
                              >
                                $
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {selectedPlace.phone_number && (
                        <div>
                          <span className="font-medium">Phone: </span>
                          <a 
                            href={`tel:${selectedPlace.phone_number}`}
                            className="text-teal-600 hover:underline"
                          >
                            {selectedPlace.phone_number}
                          </a>
                        </div>
                      )}

                      {selectedPlace.website && (
                        <div>
                          <span className="font-medium">Website: </span>
                          <a 
                            href={selectedPlace.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-teal-600 hover:underline"
                          >
                            Visit Website
                          </a>
                        </div>
                      )}

                      {selectedPlace.opening_hours && selectedPlace.opening_hours.length > 0 && (
                        <div>
                          <span className="font-medium block mb-2">Opening Hours:</span>
                          <div className="space-y-1 text-sm text-gray-600">
                            {selectedPlace.opening_hours.map((hours, index) => (
                              <div key={index}>{hours}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="pt-4 border-t border-gray-200">
                        <button
                          onClick={() => {
                            const url = `https://www.google.com/maps/search/?api=1&query=${selectedPlace.location.lat},${selectedPlace.location.lng}`
                            window.open(url, '_blank')
                          }}
                          className="w-full btn-primary"
                        >
                          View on Google Maps
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 text-center">
                    <MapPin className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Select a Place
                    </h3>
                    <p className="text-gray-600">
                      Click on any place from the search results to view details
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section-padding bg-white">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-poppins font-bold mb-6">Powered by Google Places</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Access real-time information about millions of places worldwide
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <Search className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Smart Search</h3>
              <p className="text-gray-600">
                Find exactly what you're looking for with intelligent search filters and location-based results.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <MapPin className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Real-time Data</h3>
              <p className="text-gray-600">
                Get up-to-date information including ratings, reviews, opening hours, and contact details.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <Filter className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Advanced Filters</h3>
              <p className="text-gray-600">
                Filter by budget, distance, meal type, and more to find places that match your preferences.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
