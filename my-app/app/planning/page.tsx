"use client"

import { useState } from "react"
import { Users, Heart, Mountain, Camera, Calendar, MapPin, Clock, DollarSign } from "lucide-react"

const tripTypes = [
  {
    id: "solo",
    name: "Solo Adventure",
    icon: Mountain,
    description: "Perfect for independent explorers",
    color: "from-purple-500 to-pink-500",
  },
  {
    id: "couple",
    name: "Romantic Getaway",
    icon: Heart,
    description: "Intimate experiences for couples",
    color: "from-rose-500 to-pink-500",
  },
  {
    id: "family",
    name: "Family Fun",
    icon: Users,
    description: "Activities for all ages",
    color: "from-blue-500 to-cyan-500",
  },
  {
    id: "photography",
    name: "Photography Tour",
    icon: Camera,
    description: "Capture Sri Lanka's beauty",
    color: "from-green-500 to-teal-500",
  },
]

const itineraries = [
  {
    id: 1,
    title: "Classic Sri Lanka",
    duration: "10 Days",
    price: "$1,299",
    image: "/placeholder.svg?height=300&width=400",
    highlights: ["Sigiriya Rock Fortress", "Kandy Temple", "Tea Plantations", "Galle Fort"],
    bestFor: ["First-time visitors", "Cultural enthusiasts"],
  },
  {
    id: 2,
    title: "Beach & Wildlife",
    duration: "8 Days",
    price: "$999",
    image: "/placeholder.svg?height=300&width=400",
    highlights: ["Yala National Park", "Mirissa Beach", "Whale Watching", "Udawalawe Safari"],
    bestFor: ["Nature lovers", "Beach enthusiasts"],
  },
  {
    id: 3,
    title: "Adventure Seeker",
    duration: "12 Days",
    price: "$1,599",
    image: "/placeholder.svg?height=300&width=400",
    highlights: ["Adam's Peak Hike", "White Water Rafting", "Rock Climbing", "Zip Lining"],
    bestFor: ["Adventure enthusiasts", "Active travelers"],
  },
  {
    id: 4,
    title: "Cultural Heritage",
    duration: "7 Days",
    price: "$899",
    image: "/placeholder.svg?height=300&width=400",
    highlights: ["Ancient Cities", "Temple Tours", "Traditional Crafts", "Local Festivals"],
    bestFor: ["History buffs", "Cultural explorers"],
  },
]

const weatherData = [
  { month: "Jan", temp: "27°C", rainfall: "Low", season: "Dry" },
  { month: "Feb", temp: "28°C", rainfall: "Low", season: "Dry" },
  { month: "Mar", temp: "29°C", rainfall: "Medium", season: "Dry" },
  { month: "Apr", temp: "30°C", rainfall: "High", season: "Inter-monsoon" },
  { month: "May", temp: "29°C", rainfall: "High", season: "Southwest Monsoon" },
  { month: "Jun", temp: "28°C", rainfall: "High", season: "Southwest Monsoon" },
  { month: "Jul", temp: "28°C", rainfall: "Medium", season: "Southwest Monsoon" },
  { month: "Aug", temp: "28°C", rainfall: "Medium", season: "Southwest Monsoon" },
  { month: "Sep", temp: "28°C", rainfall: "High", season: "Inter-monsoon" },
  { month: "Oct", temp: "28°C", rainfall: "High", season: "Northeast Monsoon" },
  { month: "Nov", temp: "27°C", rainfall: "High", season: "Northeast Monsoon" },
  { month: "Dec", temp: "27°C", rainfall: "Medium", season: "Northeast Monsoon" },
]

const travelTips = [
  {
    title: "Best Time to Visit",
    content: "December to March for west and south coasts, April to September for east coast.",
    icon: Calendar,
  },
  {
    title: "Getting Around",
    content: "Tuk-tuks for short distances, trains for scenic routes, private drivers for comfort.",
    icon: MapPin,
  },
  {
    title: "Duration",
    content: "Minimum 7 days recommended, 10-14 days ideal for comprehensive exploration.",
    icon: Clock,
  },
  {
    title: "Budget",
    content: "Budget: $30-50/day, Mid-range: $50-100/day, Luxury: $100+/day per person.",
    icon: DollarSign,
  },
]

const visaInfo = [
  {
    country: "Most Countries",
    requirement: "ETA (Electronic Travel Authorization)",
    validity: "30 days",
    cost: "$20",
    processing: "24-72 hours",
  },
  {
    country: "Singapore, Maldives",
    requirement: "Visa on Arrival",
    validity: "30 days",
    cost: "Free",
    processing: "On arrival",
  },
  {
    country: "India, China",
    requirement: "Visa Required",
    validity: "30 days",
    cost: "$25-35",
    processing: "3-5 days",
  },
]

export default function PlanningPage() {
  const [selectedTripType, setSelectedTripType] = useState<string | null>(null)

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="relative py-24 bg-gradient-to-r from-teal-600 to-cyan-600 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20" />
        <div className="container-custom relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-poppins font-bold mb-6 animate-fade-in">Plan Your Perfect Trip</h1>
            <p className="text-xl md:text-2xl text-teal-100 animate-slide-up animation-delay-200">
              Let us help you create unforgettable memories in Sri Lanka
            </p>
          </div>
        </div>
      </section>

      {/* Trip Type Selector */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">What Type of Trip Are You Planning?</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose your travel style and we'll customize recommendations just for you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {tripTypes.map((type, index) => {
              const Icon = type.icon
              return (
                <button
                  key={type.id}
                  onClick={() => setSelectedTripType(type.id)}
                  className={`p-8 rounded-2xl text-center transition-all duration-300 transform hover:scale-105 animate-slide-up ${
                    selectedTripType === type.id
                      ? "bg-gradient-to-r " + type.color + " text-white shadow-2xl"
                      : "bg-white hover:shadow-xl border border-gray-200"
                  }`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div
                    className={`w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${
                      selectedTripType === type.id ? "bg-white/20" : "bg-gradient-to-r " + type.color
                    }`}
                  >
                    <Icon className={`w-8 h-8 ${selectedTripType === type.id ? "text-white" : "text-white"}`} />
                  </div>
                  <h3
                    className={`text-xl font-poppins font-semibold mb-2 ${
                      selectedTripType === type.id ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {type.name}
                  </h3>
                  <p className={`text-sm ${selectedTripType === type.id ? "text-white/80" : "text-gray-600"}`}>
                    {type.description}
                  </p>
                </button>
              )
            })}
          </div>
        </div>
      </section>

      {/* Suggested Itineraries */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Suggested Itineraries</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Carefully crafted journeys to help you experience the best of Sri Lanka
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {itineraries.map((itinerary, index) => (
              <div
                key={itinerary.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden card-hover animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <img
                  src={itinerary.image || "/placeholder.svg"}
                  alt={itinerary.title}
                  className="w-full h-48 object-cover"
                />
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-poppins font-semibold">{itinerary.title}</h3>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-teal-600">{itinerary.price}</div>
                      <div className="text-sm text-gray-500">{itinerary.duration}</div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Highlights:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {itinerary.highlights.map((highlight, idx) => (
                        <li key={idx} className="flex items-center">
                          <div className="w-1.5 h-1.5 bg-teal-500 rounded-full mr-2" />
                          {highlight}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-900 mb-2">Best For:</h4>
                    <div className="flex flex-wrap gap-2">
                      {itinerary.bestFor.map((tag, idx) => (
                        <span key={idx} className="px-3 py-1 bg-teal-50 text-teal-700 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button className="w-full btn-primary">Customize This Trip</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Weather Guide */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Weather Guide</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Plan your visit based on Sri Lanka's tropical climate patterns
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold">Month</th>
                    <th className="px-6 py-4 text-left font-semibold">Temperature</th>
                    <th className="px-6 py-4 text-left font-semibold">Rainfall</th>
                    <th className="px-6 py-4 text-left font-semibold">Season</th>
                  </tr>
                </thead>
                <tbody>
                  {weatherData.map((month, index) => (
                    <tr
                      key={month.month}
                      className={`border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200 ${
                        index % 2 === 0 ? "bg-gray-50/50" : "bg-white"
                      }`}
                    >
                      <td className="px-6 py-4 font-semibold text-gray-900">{month.month}</td>
                      <td className="px-6 py-4 text-gray-700">{month.temp}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            month.rainfall === "Low"
                              ? "bg-green-100 text-green-800"
                              : month.rainfall === "Medium"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-red-100 text-red-800"
                          }`}
                        >
                          {month.rainfall}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-700">{month.season}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Travel Tips */}
      <section className="section-padding bg-gray-50">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Essential Travel Tips</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to know for a smooth Sri Lankan adventure
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {travelTips.map((tip, index) => {
              const Icon = tip.icon
              return (
                <div
                  key={tip.title}
                  className="bg-white p-6 rounded-2xl shadow-lg card-hover animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-poppins font-semibold mb-2">{tip.title}</h3>
                      <p className="text-gray-600 leading-relaxed">{tip.content}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Visa Information */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-poppins font-bold mb-6 gradient-text">Visa Information</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">Visa requirements based on your nationality</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {visaInfo.map((visa, index) => (
              <div
                key={visa.country}
                className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <h3 className="text-lg font-poppins font-semibold mb-4 text-center">{visa.country}</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Requirement:</span>
                    <span className="font-medium">{visa.requirement}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Validity:</span>
                    <span className="font-medium">{visa.validity}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cost:</span>
                    <span className="font-medium text-teal-600">{visa.cost}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Processing:</span>
                    <span className="font-medium">{visa.processing}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-6">Need help with your visa application?</p>
            <button className="btn-primary">Get Visa Assistance</button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-gradient-to-r from-teal-600 to-cyan-600 text-white">
        <div className="container-custom">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-poppins font-bold mb-6 animate-fade-in">Ready to Start Planning?</h2>
            <p className="text-xl mb-8 text-teal-100 animate-slide-up animation-delay-200">
              Let our local experts create a personalized itinerary just for you
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up animation-delay-400">
              <button className="bg-white text-teal-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors duration-200">
                Get Custom Itinerary
              </button>
              <button className="border-2 border-white text-white px-8 py-3 rounded-full font-semibold hover:bg-white hover:text-teal-600 transition-colors duration-200">
                Speak to an Expert
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
