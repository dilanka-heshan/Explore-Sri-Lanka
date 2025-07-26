"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { 
  MapPin, Calendar, Users, Star, Download, Edit, Trash2, 
  Eye, Plus, Filter, Search, Grid, List, Heart, FileText
} from "lucide-react"
import { apiClient } from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"

interface TravelPlan {
  id: string
  title: string
  destination_summary: string
  trip_duration_days: number
  budget_level: string
  trip_type: string
  status: string
  favorite: boolean
  user_rating?: number
  planned_start_date?: string
  created_at: string
  updated_at: string
  times_viewed: number
  pdf_generated: boolean
}

interface TravelPlanStats {
  total_plans: number
  draft_plans: number
  active_plans: number
  completed_plans: number
  favorite_plans: number
  total_destinations: number
  total_trip_days: number
  average_rating?: number
}

export default function MyTripsPage() {
  const router = useRouter()
  const { isAuthenticated, user } = useAuth()
  
  const [plans, setPlans] = useState<TravelPlan[]>([])
  const [stats, setStats] = useState<TravelPlanStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [favoriteOnly, setFavoriteOnly] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [sortBy, setSortBy] = useState("created_at")
  const [sortOrder, setSortOrder] = useState("desc")
  const [pdfGenerating, setPdfGenerating] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
      return
    }
    
    loadPlans()
    loadStats()
  }, [isAuthenticated, searchQuery, statusFilter, favoriteOnly, sortBy, sortOrder])

  const loadPlans = async () => {
    try {
      setLoading(true)
      const result = await apiClient.getMyTravelPlans({
        status_filter: statusFilter || undefined,
        favorite_only: favoriteOnly,
        search: searchQuery || undefined,
        sort_by: sortBy,
        sort_order: sortOrder as 'asc' | 'desc',
        limit: 50
      }) as TravelPlan[]
      
      setPlans(result || [])
    } catch (error) {
      console.error("Error loading travel plans:", error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await apiClient.getTravelPlanStats() as TravelPlanStats
      setStats(statsData)
    } catch (error) {
      console.error("Error loading stats:", error)
    }
  }

  const handleToggleFavorite = async (planId: string) => {
    try {
      await apiClient.toggleTravelPlanFavorite(planId)
      loadPlans() // Reload to update the list
    } catch (error) {
      console.error("Error toggling favorite:", error)
    }
  }

  const handleDeletePlan = async (planId: string, title: string) => {
    if (!confirm(`Are you sure you want to archive "${title}"?`)) return

    try {
      await apiClient.deleteTravelPlan(planId)
      loadPlans() // Reload to update the list
    } catch (error) {
      console.error("Error deleting plan:", error)
      alert("Failed to archive travel plan")
    }
  }

  const handleGeneratePDF = async (planId: string, title: string) => {
    try {
      setPdfGenerating(planId)
      
      // Generate PDF
      const pdfResult = await apiClient.generateTravelPlanPDF(planId, {
        custom_title: title
      }) as any

      if (pdfResult && pdfResult.success) {
        // Download the PDF
        const blob = await apiClient.downloadTravelPlanPDF(planId)
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        loadPlans() // Reload to update PDF status
      }
    } catch (error) {
      console.error("Error generating PDF:", error)
      alert("Failed to generate PDF")
    } finally {
      setPdfGenerating(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
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
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Please Sign In</h1>
          <p className="text-gray-600 mb-8">You need to be signed in to view your travel plans.</p>
          <button
            onClick={() => router.push('/auth/login')}
            className="btn-primary"
          >
            Sign In
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container-custom">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-poppins font-bold text-gray-900">My Travel Plans</h1>
              <p className="text-gray-600 mt-2">Manage your saved travel plans and itineraries</p>
            </div>
            <button
              onClick={() => router.push('/planning')}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Create New Plan</span>
            </button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center">
                  <FileText className="w-8 h-8 text-teal-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Plans</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_plans}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center">
                  <MapPin className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Destinations</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_destinations}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center">
                  <Calendar className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Days</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_trip_days}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center">
                  <Heart className="w-8 h-8 text-red-600" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Favorites</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.favorite_plans}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Filters and Search */}
          <div className="bg-white rounded-lg p-6 shadow-sm mb-8">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 flex-1">
                {/* Search */}
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search plans..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent w-full"
                  />
                </div>

                {/* Status Filter */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>

                {/* Favorites Toggle */}
                <button
                  onClick={() => setFavoriteOnly(!favoriteOnly)}
                  className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                    favoriteOnly 
                      ? 'bg-red-100 text-red-800 border-red-200' 
                      : 'bg-gray-100 text-gray-600 border-gray-200'
                  } border`}
                >
                  <Heart className={`w-4 h-4 ${favoriteOnly ? 'fill-current' : ''}`} />
                  <span>Favorites</span>
                </button>
              </div>

              {/* View Mode and Sort */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-teal-100 text-teal-600' : 'text-gray-400'}`}
                  >
                    <Grid className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded ${viewMode === 'list' ? 'bg-teal-100 text-teal-600' : 'text-gray-400'}`}
                  >
                    <List className="w-4 h-4" />
                  </button>
                </div>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="created_at">Created Date</option>
                  <option value="updated_at">Last Modified</option>
                  <option value="title">Title</option>
                  <option value="trip_duration_days">Duration</option>
                </select>

                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Plans Grid/List */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
          </div>
        ) : plans.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Travel Plans Yet</h3>
            <p className="text-gray-600 mb-6">Start planning your next adventure!</p>
            <button
              onClick={() => router.push('/planning')}
              className="btn-primary"
            >
              Create Your First Plan
            </button>
          </div>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              : "space-y-4"
          }>
            {plans.map((plan) => (
              <div key={plan.id} className={`
                bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow
                ${viewMode === 'list' ? 'p-6' : 'p-6'}
              `}>
                {viewMode === 'grid' ? (
                  // Grid View
                  <>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900 mb-2">{plan.title}</h3>
                        <p className="text-gray-600 text-sm mb-3">{plan.destination_summary}</p>
                      </div>
                      <button
                        onClick={() => handleToggleFavorite(plan.id)}
                        className={`p-2 rounded-full ${
                          plan.favorite ? 'text-red-500' : 'text-gray-400'
                        } hover:bg-gray-100`}
                      >
                        <Heart className={`w-5 h-5 ${plan.favorite ? 'fill-current' : ''}`} />
                      </button>
                    </div>

                    <div className="space-y-3 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span>{plan.trip_duration_days} days</span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(plan.status)}`}>
                          {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-2">
                          <span>{getBudgetIcon(plan.budget_level)}</span>
                          <span className="capitalize">{plan.budget_level.replace('_', ' ')}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span>{getTripTypeIcon(plan.trip_type)}</span>
                          <span className="capitalize">{plan.trip_type}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Eye className="w-4 h-4" />
                          <span>{plan.times_viewed}</span>
                        </div>
                        <span>Created {formatDate(plan.created_at)}</span>
                      </div>

                      {plan.user_rating && (
                        <div className="flex items-center space-x-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < plan.user_rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => router.push(`/my-trips/${plan.id}`)}
                        className="flex-1 px-3 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors"
                      >
                        View Details
                      </button>
                      <button
                        onClick={() => handleGeneratePDF(plan.id, plan.title)}
                        disabled={pdfGenerating === plan.id}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                      >
                        {pdfGenerating === plan.id ? (
                          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <Download className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDeletePlan(plan.id, plan.title)}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </>
                ) : (
                  // List View
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg text-gray-900">{plan.title}</h3>
                          <p className="text-gray-600 text-sm">{plan.destination_summary}</p>
                        </div>
                        <div className="flex items-center space-x-6 text-sm text-gray-500">
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{plan.trip_duration_days} days</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <span>{getBudgetIcon(plan.budget_level)}</span>
                            <span className="capitalize">{plan.budget_level.replace('_', ' ')}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <span>{getTripTypeIcon(plan.trip_type)}</span>
                            <span className="capitalize">{plan.trip_type}</span>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(plan.status)}`}>
                            {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleToggleFavorite(plan.id)}
                        className={`p-2 rounded-full ${
                          plan.favorite ? 'text-red-500' : 'text-gray-400'
                        } hover:bg-gray-100`}
                      >
                        <Heart className={`w-5 h-5 ${plan.favorite ? 'fill-current' : ''}`} />
                      </button>
                      <button
                        onClick={() => router.push(`/my-trips/${plan.id}`)}
                        className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleGeneratePDF(plan.id, plan.title)}
                        disabled={pdfGenerating === plan.id}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50"
                      >
                        {pdfGenerating === plan.id ? (
                          <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <Download className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDeletePlan(plan.id, plan.title)}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
