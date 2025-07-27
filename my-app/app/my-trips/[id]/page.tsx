"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { 
  ArrowLeft, MapPin, Calendar, Users, Star, Download, Edit, 
  Heart, Clock, DollarSign, Sparkles, Navigation
} from "lucide-react"
import { apiClient } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

interface TravelPlan {
  id: string
  title: string
  description?: string
  destination_summary: string
  trip_duration_days: number
  budget_level: string
  trip_type: string
  status: string
  favorite: boolean
  user_rating?: number
  user_notes?: string
  planned_start_date?: string
  actual_start_date?: string
  actual_end_date?: string
  created_at: string
  updated_at: string
  times_viewed: number
  pdf_generated: boolean
  travel_plan_data: any
  original_query: string
  interests: string[]
}

export default function TripDetailsPage() {
  const router = useRouter()
  const params = useParams()
  const { isAuthenticated } = useAuth()
  const planId = params.id as string
  
  const [plan, setPlan] = useState<TravelPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [pdfGenerating, setPdfGenerating] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    user_rating: 0,
    user_notes: "",
    status: "draft"
  })

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
      return
    }
    
    if (planId) {
      loadPlan()
    }
  }, [isAuthenticated, planId])

  const loadPlan = async () => {
    try {
      setLoading(true)
      const result = await apiClient.getTravelPlan(planId) as any
      
      if (result && result.plan) {
        setPlan(result.plan)
        setEditForm({
          title: result.plan.title,
          description: result.plan.description || "",
          user_rating: result.plan.user_rating || 0,
          user_notes: result.plan.user_notes || "",
          status: result.plan.status
        })
      }
    } catch (error) {
      console.error("Error loading travel plan:", error)
      router.push('/my-trips')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleFavorite = async () => {
    if (!plan) return

    try {
      await apiClient.toggleTravelPlanFavorite(plan.id)
      setPlan({ ...plan, favorite: !plan.favorite })
    } catch (error) {
      console.error("Error toggling favorite:", error)
    }
  }

  const handleSaveChanges = async () => {
    if (!plan) return

    try {
      const updates = {
        title: editForm.title,
        description: editForm.description,
        user_rating: editForm.user_rating || undefined,
        user_notes: editForm.user_notes,
        status: editForm.status as any
      }

      const result = await apiClient.updateTravelPlan(plan.id, updates) as any
      
      if (result && result.plan) {
        setPlan(result.plan)
        setEditing(false)
      }
    } catch (error) {
      console.error("Error updating plan:", error)
      alert("Failed to update travel plan")
    }
  }

  const handleGeneratePDF = async () => {
    if (!plan) return

    try {
      setPdfGenerating(true)
      
      const pdfResult = await apiClient.generateTravelPlanPDF(plan.id, {
        custom_title: plan.title,
        include_maps: true,
        include_photos: true,
        include_weather: true
      }) as any

      if (pdfResult && pdfResult.success) {
        const blob = await apiClient.downloadTravelPlanPDF(plan.id)
        
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${plan.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        // Reload plan to update PDF status
        loadPlan()
      }
    } catch (error) {
      console.error("Error generating PDF:", error)
      alert("Failed to generate PDF")
    } finally {
      setPdfGenerating(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getBudgetIcon = (budget: string) => {
    switch (budget) {
      case 'budget': return '💰'
      case 'mid_range': return '💎'
      case 'luxury': return '✨'
      default: return '💰'
    }
  }

  const getTripTypeIcon = (type: string) => {
    switch (type) {
      case 'solo': return '🎒'
      case 'couple': return '💑'
      case 'family': return '👨‍👩‍👧‍👦'
      case 'group': return '👥'
      default: return '🎒'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800'
      case 'active': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!isAuthenticated) {
    return null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Travel Plan Not Found</h1>
          <button
            onClick={() => router.push('/my-trips')}
            className="btn-primary"
          >
            Back to My Trips
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container-custom">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => router.push('/my-trips')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to My Trips</span>
          </button>

          <div className="flex items-center space-x-4">
            <button
              onClick={handleToggleFavorite}
              className={`p-2 rounded-full ${
                plan.favorite ? 'text-red-500 bg-red-50' : 'text-gray-400 bg-gray-100'
              } hover:bg-red-100`}
            >
              <Heart className={`w-6 h-6 ${plan.favorite ? 'fill-current' : ''}`} />
            </button>
            
            <button
              onClick={() => setEditing(!editing)}
              className="btn-secondary flex items-center space-x-2"
            >
              <Edit className="w-4 h-4" />
              <span>{editing ? 'Cancel' : 'Edit'}</span>
            </button>

            <button
              onClick={handleGeneratePDF}
              disabled={pdfGenerating}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              {pdfGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download PDF</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Plan Header */}
            <div className="bg-white rounded-lg shadow-sm p-8">
              {editing ? (
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Title
                    </label>
                    <input
                      type="text"
                      value={editForm.title}
                      onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={editForm.description}
                      onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                      rows={3}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status
                      </label>
                      <select
                        value={editForm.status}
                        onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      >
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rating (1-5)
                      </label>
                      <select
                        value={editForm.user_rating}
                        onChange={(e) => setEditForm({ ...editForm, user_rating: parseInt(e.target.value) })}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      >
                        <option value={0}>No rating</option>
                        <option value={1}>1 Star</option>
                        <option value={2}>2 Stars</option>
                        <option value={3}>3 Stars</option>
                        <option value={4}>4 Stars</option>
                        <option value={5}>5 Stars</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Personal Notes
                    </label>
                    <textarea
                      value={editForm.user_notes}
                      onChange={(e) => setEditForm({ ...editForm, user_notes: e.target.value })}
                      rows={4}
                      placeholder="Add your personal notes about this trip..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex space-x-4">
                    <button
                      onClick={handleSaveChanges}
                      className="btn-primary"
                    >
                      Save Changes
                    </button>
                    <button
                      onClick={() => setEditing(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h1 className="text-3xl font-poppins font-bold text-gray-900 mb-2">
                        {plan.title}
                      </h1>
                      {plan.description && (
                        <p className="text-gray-600 text-lg">{plan.description}</p>
                      )}
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(plan.status)}`}>
                      {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <Calendar className="w-6 h-6 mx-auto mb-2 text-teal-600" />
                      <div className="font-medium">{plan.trip_duration_days} Days</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <span className="text-2xl mb-2 block">{getBudgetIcon(plan.budget_level)}</span>
                      <div className="font-medium capitalize">{plan.budget_level.replace('_', ' ')}</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <span className="text-2xl mb-2 block">{getTripTypeIcon(plan.trip_type)}</span>
                      <div className="font-medium capitalize">{plan.trip_type}</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <Users className="w-6 h-6 mx-auto mb-2 text-teal-600" />
                      <div className="font-medium">{plan.times_viewed} Views</div>
                    </div>
                  </div>

                  {plan.user_rating && (
                    <div className="flex items-center space-x-2 mb-4">
                      <span className="text-sm font-medium text-gray-700">Your Rating:</span>
                      <div className="flex items-center space-x-1">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-5 h-5 ${
                              i < plan.user_rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {plan.user_notes && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-medium text-blue-900 mb-2">Your Notes</h4>
                      <p className="text-blue-800">{plan.user_notes}</p>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Daily Itinerary */}
            <div className="bg-white rounded-lg shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Daily Itinerary</h2>
              
              {plan.travel_plan_data && plan.travel_plan_data.daily_itineraries ? (
                <div className="space-y-8">
                  {plan.travel_plan_data.daily_itineraries.map((day: any, index: number) => (
                    <div key={index} className="border-l-4 border-teal-500 pl-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-semibold text-gray-900">
                          Day {day.day || index + 1}: {day.cluster_name || day.name || 'Exploration'}
                        </h3>
                        {day.estimated_time_hours && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Clock className="w-4 h-4 mr-1" />
                            {day.estimated_time_hours}h estimated
                          </div>
                        )}
                      </div>

                      {day.summary && (
                        <p className="text-gray-600 mb-4">{day.summary}</p>
                      )}

                      <div className="space-y-4">
                        {(day.attractions || []).map((attraction: any, idx: number) => (
                          <div key={idx} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                            <div className="w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                              {idx + 1}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">{attraction.name}</h4>
                              <p className="text-sm text-gray-600 mt-1">{attraction.description}</p>
                              <div className="flex items-center mt-2 text-xs text-gray-500">
                                <MapPin className="w-3 h-3 mr-1" />
                                {attraction.location?.city || attraction.location?.region || attraction.city || 'Sri Lanka'}
                                {attraction.duration_hours && (
                                  <>
                                    <Clock className="w-3 h-3 ml-3 mr-1" />
                                    {attraction.duration_hours}h
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Enhanced Places */}
                      {day.places && Object.keys(day.places).length > 0 && (
                        <div className="mt-6 pt-6 border-t">
                          <h4 className="font-medium text-gray-900 mb-4">Recommended Places</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {day.places.restaurants?.slice(0, 2).map((restaurant: any, idx: number) => (
                              <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                                <div className="font-medium text-sm">{restaurant.name}</div>
                                <div className="text-xs text-gray-600">Restaurant • {restaurant.rating}/5</div>
                              </div>
                            ))}
                            {day.places.accommodation?.slice(0, 1).map((hotel: any, idx: number) => (
                              <div key={idx} className="p-3 bg-green-50 rounded-lg">
                                <div className="font-medium text-sm">{hotel.name}</div>
                                <div className="text-xs text-gray-600">Hotel • {hotel.rating}/5</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Sparkles className="w-12 h-12 mx-auto mb-4" />
                  <p>Detailed itinerary information is not available for this plan.</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Trip Info */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Trip Information</h3>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm font-medium text-gray-700">Destinations</div>
                  <div className="text-gray-900">{plan.destination_summary}</div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-700">Interests</div>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {plan.interests.map((interest, idx) => (
                      <span key={idx} className="px-2 py-1 bg-teal-100 text-teal-800 text-xs rounded-full">
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-700">Original Query</div>
                  <div className="text-gray-600 text-sm italic">{plan.original_query}</div>
                </div>

                {plan.planned_start_date && (
                  <div>
                    <div className="text-sm font-medium text-gray-700">Planned Start Date</div>
                    <div className="text-gray-900">{formatDate(plan.planned_start_date)}</div>
                  </div>
                )}

                {plan.actual_start_date && (
                  <div>
                    <div className="text-sm font-medium text-gray-700">Actual Start Date</div>
                    <div className="text-gray-900">{formatDate(plan.actual_start_date)}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Plan Metadata */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Plan Details</h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="text-gray-900">{formatDate(plan.created_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Last Updated:</span>
                  <span className="text-gray-900">{formatDate(plan.updated_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Times Viewed:</span>
                  <span className="text-gray-900">{plan.times_viewed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">PDF Generated:</span>
                  <span className={plan.pdf_generated ? 'text-green-600' : 'text-gray-900'}>
                    {plan.pdf_generated ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/planning')}
                  className="w-full btn-secondary text-left"
                >
                  Create Similar Plan
                </button>
                <button
                  onClick={() => navigator.share?.({
                    title: plan.title,
                    text: plan.description || plan.destination_summary,
                    url: window.location.href
                  }) || navigator.clipboard.writeText(window.location.href)}
                  className="w-full btn-secondary text-left"
                >
                  Share Plan
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
