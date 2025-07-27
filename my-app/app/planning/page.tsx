"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Plus, MapPin, Calendar, Users, DollarSign, Clock, Sparkles, ArrowLeft, Download, Save, FileText } from "lucide-react"
import { apiClient } from "@/lib/api"
import { PlanningRequest, IntegratedPlanningResponse } from "@/lib/types"
import { useAuth } from "@/contexts/AuthContext"
import TravelPlanDisplay from "@/components/TravelPlanDisplay"

const interests = [
  "Culture & Heritage",
  "Nature & Wildlife", 
  "Adventure Sports",
  "Beach & Relaxation",
  "Food & Cuisine",
  "Photography",
  "Temples & Religion",
  "Tea Plantations",
  "Hill Country",
  "Historical Sites",
  "Local Markets",
  "Water Sports"
]

const budgetLevels = [
  { value: "budget", label: "Budget", description: "₹2,000-5,000/day", icon: "💰" },
  { value: "mid_range", label: "Mid-Range", description: "₹5,000-12,000/day", icon: "💎" },
  { value: "luxury", label: "Luxury", description: "₹12,000+/day", icon: "✨" }
]

const tripTypes = [
  { value: "solo", label: "Solo Travel", icon: "🎒" },
  { value: "couple", label: "Couple", icon: "💑" },
  { value: "family", label: "Family", icon: "👨‍👩‍👧‍👦" },
  { value: "group", label: "Group", icon: "👥" }
]

const activityLevels = [
  { value: 1, label: "Very Low", description: "Mostly relaxing" },
  { value: 2, label: "Low", description: "Light activities" },
  { value: 3, label: "Moderate", description: "Balanced pace" },
  { value: 4, label: "High", description: "Active exploration" },
  { value: 5, label: "Very High", description: "Non-stop adventure" }
]

const travelPreferences = [
  { value: "minimal", label: "Minimal", description: "Stay in one area" },
  { value: "moderate", label: "Moderate", description: "Some travel between areas" },
  { value: "extensive", label: "Extensive", description: "Cover maximum ground" }
]

export default function PlanningPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [planResult, setPlanResult] = useState<IntegratedPlanningResponse | null>(null)
  const [savedPlanId, setSavedPlanId] = useState<string | null>(null)
  const [pdfGenerating, setPdfGenerating] = useState(false)
  const [formData, setFormData] = useState<PlanningRequest & { enablePlaces: boolean, enableAI: boolean }>({
    query: "",
    interests: [],
    trip_duration_days: 3,
    budget_level: "mid_range",
    trip_type: "couple",
    activity_level: 3,
    max_attractions_per_day: 4,
    daily_travel_preference: "moderate",
    group_size: 2,
    enablePlaces: true,
    enableAI: true
  })

  const updateFormData = (updates: Partial<typeof formData>) => {
    setFormData(prev => ({ ...prev, ...updates }))
  }

  const handleInterestToggle = (interest: string) => {
    const newInterests = formData.interests.includes(interest)
      ? formData.interests.filter(i => i !== interest)
      : [...formData.interests, interest]
    updateFormData({ interests: newInterests })
  }

  const generatePlan = async () => {
    if (!formData.query.trim() || formData.interests.length === 0) {
      alert("Please fill in all required fields")
      return
    }

    setLoading(true)
    try {
      const planningData = {
        query: formData.query,
        interests: formData.interests,
        trip_duration_days: formData.trip_duration_days,
        budget_level: formData.budget_level,
        trip_type: formData.trip_type,
        activity_level: formData.activity_level,
        max_attractions_per_day: formData.max_attractions_per_day,
        daily_travel_preference: formData.daily_travel_preference,
        group_size: formData.group_size,
        enhancements: {
          places: {
            enabled: formData.enablePlaces,
            priority: 1,
            config: {
              search_radius_km: 5,
              include_breakfast: true,
              include_lunch: true,
              include_dinner: true,
              include_accommodation: true,
              include_cafes: true
            }
          }
        },
        async_processing: false
      }

      const result = await apiClient.planTripIntegratedFull(planningData) as any
      console.log("Planning result:", result) // Debug log
      console.log("Result type:", typeof result)
      console.log("Is array:", Array.isArray(result))
      
      // Be very flexible with response structure - just check if we got something back
      if (result && (typeof result === 'object')) {
        setPlanResult(result as IntegratedPlanningResponse)
        
        // Auto-save the plan if user is authenticated
        if (isAuthenticated) {
          try {
            const autoSaveData = {
              travel_plan: result,
              original_request: planningData
            }
            const saveResult = await apiClient.autoSaveFromPlanning(autoSaveData) as any
            if (saveResult && saveResult.plan_id) {
              setSavedPlanId(saveResult.plan_id)
              console.log(`Plan auto-saved with ID: ${saveResult.plan_id}`)
            }
          } catch (saveError) {
            console.warn("Auto-save failed:", saveError)
            // Don't show error to user - auto-save is optional
          }
        }
        
        setStep(4)
      } else {
        console.error("Invalid response structure:", result)
        console.log("Available keys:", result ? Object.keys(result) : 'No result')
        alert("Received invalid response from planning service. Please try again.")
      }
    } catch (error) {
      console.error("Planning failed:", error)
      alert(`Failed to generate travel plan: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const savePlanManually = async () => {
    if (!planResult || !isAuthenticated) return

    try {
      // Extract destination summary from plan
      const planData = planResult as any
      const clusteredPlan = planData.clustered_plan || planData.plan || planData.days || []
      const destinations = clusteredPlan.map((cluster: any) => 
        cluster.cluster_name || cluster.name || `Day ${cluster.day || 1}`
      ).join(', ')

      const title = `Sri Lanka Trip - ${formData.trip_duration_days} Days`
      const description = `Exploring ${destinations}`

      const planCreateData = {
        title,
        description,
        travel_plan_data: planResult,
        original_query: formData.query,
        interests: formData.interests,
        trip_duration_days: formData.trip_duration_days,
        budget_level: formData.budget_level,
        trip_type: formData.trip_type || 'couple',
        privacy: 'private' as const
      }

      const result = await apiClient.saveTravelPlan(planCreateData) as any
      if (result && result.plan && result.plan.id) {
        setSavedPlanId(result.plan.id)
        alert("Travel plan saved successfully!")
      }
    } catch (error) {
      console.error("Error saving plan:", error)
      alert("Failed to save travel plan. Please try again.")
    }
  }

  const generateAndDownloadPDF = async () => {
    if (!savedPlanId) {
      alert("Please save the plan first to generate a PDF")
      return
    }

    setPdfGenerating(true)
    try {
      // Generate PDF
      const pdfResult = await apiClient.generateTravelPlanPDF(savedPlanId, {
        include_maps: true,
        include_photos: true,
        include_weather: true,
        custom_title: `Sri Lanka Travel Plan - ${formData.trip_duration_days} Days`
      }) as any

      if (pdfResult && pdfResult.success) {
        // Download the PDF
        const blob = await apiClient.downloadTravelPlanPDF(savedPlanId)
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `Sri_Lanka_Travel_Plan_${formData.trip_duration_days}_Days.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        alert("PDF downloaded successfully!")
      } else {
        alert("Failed to generate PDF. Please try again.")
      }
    } catch (error) {
      console.error("Error generating PDF:", error)
      alert("Failed to generate PDF. Please try again.")
    } finally {
      setPdfGenerating(false)
    }
  }

  const renderStep1 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-poppins font-bold mb-4">Tell us about your dream trip</h2>
        <p className="text-gray-600 text-lg">Describe what you'd like to experience in Sri Lanka</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What would you like to explore? *
          </label>
          <textarea
            value={formData.query}
            onChange={(e) => updateFormData({ query: e.target.value })}
            placeholder="e.g., Ancient temples and cultural sites in the cultural triangle, beautiful beaches in the south, wildlife safaris..."
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            rows={4}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Select your interests *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {interests.map((interest) => (
              <button
                key={interest}
                onClick={() => handleInterestToggle(interest)}
                className={`p-3 rounded-lg border text-sm font-medium transition-all duration-200 ${
                  formData.interests.includes(interest)
                    ? "bg-teal-500 text-white border-teal-500"
                    : "bg-white text-gray-700 border-gray-300 hover:border-teal-300"
                }`}
              >
                {interest}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">Select at least one interest</p>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => setStep(2)}
          disabled={!formData.query.trim() || formData.interests.length === 0}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next: Trip Details
        </button>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-poppins font-bold mb-4">Trip Details</h2>
        <p className="text-gray-600 text-lg">Let us know your travel preferences</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">Duration</label>
          <div className="flex items-center space-x-4">
            <Calendar className="w-5 h-5 text-gray-400" />
            <input
              type="number"
              min="1"
              max="30"
              value={formData.trip_duration_days}
              onChange={(e) => updateFormData({ trip_duration_days: parseInt(e.target.value) })}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            />
            <span className="text-gray-600">days</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">Group Size</label>
          <div className="flex items-center space-x-4">
            <Users className="w-5 h-5 text-gray-400" />
            <input
              type="number"
              min="1"
              max="20"
              value={formData.group_size}
              onChange={(e) => updateFormData({ group_size: parseInt(e.target.value) })}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            />
            <span className="text-gray-600">people</span>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">Budget Level</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {budgetLevels.map((budget) => (
            <button
              key={budget.value}
              onClick={() => updateFormData({ budget_level: budget.value as any })}
              className={`p-4 rounded-lg border text-left transition-all duration-200 ${
                formData.budget_level === budget.value
                  ? "bg-teal-50 border-teal-500 ring-2 ring-teal-500"
                  : "bg-white border-gray-300 hover:border-teal-300"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{budget.label}</span>
                <span className="text-2xl">{budget.icon}</span>
              </div>
              <p className="text-sm text-gray-600">{budget.description}</p>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">Trip Type</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {tripTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => updateFormData({ trip_type: type.value as any })}
              className={`p-4 rounded-lg border text-center transition-all duration-200 ${
                formData.trip_type === type.value
                  ? "bg-teal-50 border-teal-500 ring-2 ring-teal-500"
                  : "bg-white border-gray-300 hover:border-teal-300"
              }`}
            >
              <div className="text-2xl mb-2">{type.icon}</div>
              <span className="font-medium">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => setStep(1)}
          className="btn-secondary"
        >
          Back
        </button>
        <button
          onClick={() => setStep(3)}
          className="btn-primary"
        >
          Next: Preferences
        </button>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-poppins font-bold mb-4">Travel Preferences</h2>
        <p className="text-gray-600 text-lg">Fine-tune your travel experience</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">Activity Level</label>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {activityLevels.map((level) => (
            <button
              key={level.value}
              onClick={() => updateFormData({ activity_level: level.value })}
              className={`p-4 rounded-lg border text-center transition-all duration-200 ${
                formData.activity_level === level.value
                  ? "bg-teal-50 border-teal-500 ring-2 ring-teal-500"
                  : "bg-white border-gray-300 hover:border-teal-300"
              }`}
            >
              <div className="font-medium text-sm mb-1">{level.label}</div>
              <div className="text-xs text-gray-600">{level.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-4">Daily Travel Preference</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {travelPreferences.map((pref) => (
            <button
              key={pref.value}
              onClick={() => updateFormData({ daily_travel_preference: pref.value as any })}
              className={`p-4 rounded-lg border text-left transition-all duration-200 ${
                formData.daily_travel_preference === pref.value
                  ? "bg-teal-50 border-teal-500 ring-2 ring-teal-500"
                  : "bg-white border-gray-300 hover:border-teal-300"
              }`}
            >
              <div className="font-medium mb-1">{pref.label}</div>
              <div className="text-sm text-gray-600">{pref.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Max Attractions per Day
          </label>
          <div className="flex items-center space-x-4">
            <MapPin className="w-5 h-5 text-gray-400" />
            <input
              type="number"
              min="1"
              max="8"
              value={formData.max_attractions_per_day}
              onChange={(e) => updateFormData({ max_attractions_per_day: parseInt(e.target.value) })}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
            />
            <span className="text-gray-600">attractions</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-4">Enhanced Features</h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.enablePlaces}
              onChange={(e) => updateFormData({ enablePlaces: e.target.checked })}
              className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
            />
            <div className="ml-3">
              <div className="font-medium">Google Places Integration</div>
              <div className="text-sm text-gray-600">Include restaurant, hotel, and cafe recommendations</div>
            </div>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.enableAI}
              onChange={(e) => updateFormData({ enableAI: e.target.checked })}
              className="rounded border-gray-300 text-teal-600 focus:ring-teal-500"
            />
            <div className="ml-3">
              <div className="font-medium">AI Enhancement</div>
              <div className="text-sm text-gray-600">Get AI-powered insights and recommendations</div>
            </div>
          </label>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => setStep(2)}
          className="btn-secondary"
        >
          Back
        </button>
        <button
          onClick={generatePlan}
          disabled={loading}
          className="btn-primary flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating Plan...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Generate My Trip</span>
            </>
          )}
        </button>
      </div>
    </div>
  )

  const renderPlanResult = () => {
    if (!planResult) return null

    // Handle different response structures - check for the backend template format
    const planData = planResult as any
    console.log("Full plan data:", planData) // Debug log
    console.log("Available keys:", Object.keys(planData))
    
    // Check if this matches the backend template format
    if (planData.daily_itineraries && Array.isArray(planData.daily_itineraries)) {
      // Use the new TravelPlanDisplay component for the backend template format
      return (
        <TravelPlanDisplay
          planData={planData}
          onSavePlan={savedPlanId ? undefined : savePlanManually}
          onDownloadPDF={savedPlanId ? generateAndDownloadPDF : undefined}
          onSharePlan={() => {
            // TODO: Implement sharing functionality
            console.log("Share plan")
          }}
          isLoading={false}
        />
      )
    }

    // Fallback for other response formats (keep existing logic)
    const clusteredPlan = planData.clustered_plan || planData.plan || planData.days || []
    const placesRecommendations = planData.places_recommendations || planData.enhanced_places || {}
    
    console.log("Extracted clustered plan:", clusteredPlan)
    console.log("Extracted places recommendations:", placesRecommendations)

    return (
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-poppins font-bold mb-4">Your Personalized Travel Plan</h2>
          <p className="text-gray-600 text-lg">
            Generated in {planData.processing_time_seconds || planData.processing_time || 'N/A'}s
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Plan Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Calendar className="w-6 h-6 mx-auto mb-2 text-teal-600" />
              <div className="font-medium">{formData.trip_duration_days} Days</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <MapPin className="w-6 h-6 mx-auto mb-2 text-teal-600" />
              <div className="font-medium">{clusteredPlan.length || 0} Areas</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <DollarSign className="w-6 h-6 mx-auto mb-2 text-teal-600" />
              <div className="font-medium">{formData.budget_level}</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <Users className="w-6 h-6 mx-auto mb-2 text-teal-600" />
              <div className="font-medium">{formData.group_size} People</div>
            </div>
          </div>

          <div className="space-y-6">
            {clusteredPlan && clusteredPlan.length > 0 ? (
              clusteredPlan.map((cluster: any, index: number) => (
                <div key={cluster.cluster_id || cluster.id || index} className="border rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold">Day {cluster.day || index + 1}</h4>
                    <span className="text-sm text-gray-600">
                      {cluster.estimated_time_hours || cluster.duration || 'N/A'}h estimated time
                    </span>
                  </div>

                  <div className="space-y-4">
                    {(cluster.attractions || cluster.places || []).map((attraction: any, idx: number) => (
                    <div key={attraction.id || idx} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium">{attraction.name}</h5>
                        <p className="text-sm text-gray-600 mt-1">{attraction.description}</p>
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <MapPin className="w-3 h-3 mr-1" />
                          {attraction.location?.city || attraction.location?.region || attraction.city || 'Unknown location'}
                          {(attraction.duration_hours || attraction.duration) && (
                            <>
                              <Clock className="w-3 h-3 ml-3 mr-1" />
                              {attraction.duration_hours || attraction.duration}h
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {placesRecommendations[cluster.cluster_id || cluster.id] && (
                  <div className="mt-6 pt-6 border-t">
                    <h5 className="font-medium mb-4">Recommended Places</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(placesRecommendations[cluster.cluster_id || cluster.id].restaurants || []).slice(0, 2).map((restaurant: any) => (
                        <div key={restaurant.place_id || restaurant.id} className="p-3 bg-blue-50 rounded-lg">
                          <div className="font-medium text-sm">{restaurant.name}</div>
                          <div className="text-xs text-gray-600">Restaurant • {restaurant.rating}/5</div>
                        </div>
                      ))}
                      {(placesRecommendations[cluster.cluster_id || cluster.id].accommodation || []).slice(0, 1).map((hotel: any) => (
                        <div key={hotel.place_id || hotel.id} className="p-3 bg-green-50 rounded-lg">
                          <div className="font-medium text-sm">{hotel.name}</div>
                          <div className="text-xs text-gray-600">Hotel • {hotel.rating}/5</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600">No plan data available. The planning service may have returned an unexpected format.</p>
                <button 
                  onClick={() => setStep(1)} 
                  className="mt-4 btn-primary"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>

          {planData.ai_insights && (
            <div className="mt-8 p-6 bg-teal-50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center">
                <Sparkles className="w-5 h-5 mr-2 text-teal-600" />
                AI Insights
              </h4>
              <p className="text-gray-700">{planData.ai_insights}</p>
            </div>
          )}
        </div>

        <div className="flex justify-center space-x-4 flex-wrap gap-4">
          <button
            onClick={() => {
              setStep(1)
              setPlanResult(null)
              setSavedPlanId(null)
              setFormData({
                query: "",
                interests: [],
                trip_duration_days: 3,
                budget_level: "mid_range",
                trip_type: "couple",
                activity_level: 3,
                max_attractions_per_day: 4,
                daily_travel_preference: "moderate",
                group_size: 2,
                enablePlaces: true,
                enableAI: true
              })
            }}
            className="btn-secondary flex items-center space-x-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Plan Another Trip</span>
          </button>
          
          {isAuthenticated && (
            <>
              {savedPlanId ? (
                <div className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                  <Save className="w-4 h-4" />
                  <span className="text-sm">Plan Saved!</span>
                </div>
              ) : (
                <button
                  onClick={savePlanManually}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>Save This Plan</span>
                </button>
              )}
              
              {savedPlanId && (
                <button
                  onClick={generateAndDownloadPDF}
                  disabled={pdfGenerating}
                  className="btn-primary flex items-center space-x-2 disabled:opacity-50"
                >
                  {pdfGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
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
              
              {savedPlanId && (
                <button
                  onClick={() => router.push('/my-trips')}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>View My Trips</span>
                </button>
              )}
            </>
          )}
          
          {!isAuthenticated && (
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-blue-800 text-sm mb-2">
                <strong>Sign in to save your plans and generate PDFs!</strong>
              </p>
              <button
                onClick={() => router.push('/auth/login')}
                className="btn-primary"
              >
                Sign In
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container-custom">
        <div className="max-w-4xl mx-auto">
          {/* Progress indicator */}
          <div className="mb-12">
            <div className="flex items-center justify-center space-x-4">
              {[1, 2, 3, 4].map((stepNum) => (
                <div key={stepNum} className="flex items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                      step >= stepNum
                        ? "bg-teal-500 text-white"
                        : "bg-gray-200 text-gray-600"
                    }`}
                  >
                    {stepNum}
                  </div>
                  {stepNum < 4 && (
                    <div
                      className={`w-16 h-1 mx-2 ${
                        step > stepNum ? "bg-teal-500" : "bg-gray-200"
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-center mt-4">
              <div className="text-sm text-gray-600">
                {step === 1 && "Trip Details"}
                {step === 2 && "Basic Info"}
                {step === 3 && "Preferences"}
                {step === 4 && "Your Plan"}
              </div>
            </div>
          </div>

          {/* Step content */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderPlanResult()}
          </div>
        </div>
      </div>
    </div>
  )
}
