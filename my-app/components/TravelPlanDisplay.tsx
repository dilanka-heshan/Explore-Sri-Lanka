'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { 
  MapPin, 
  Clock, 
  Star, 
  Calendar, 
  Route,
  Camera,
  Utensils,
  Bed,
  Coffee,
  Users,
  DollarSign,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Info,
  Download,
  Share2,
  Heart
} from 'lucide-react';

// Type definitions based on the sample template
interface Attraction {
  id: string;
  name: string;
  category: string;
  description: string;
  region: string;
  latitude: number;
  longitude: number;
  pear_score: number;
  visit_order: number;
}

interface ClusterInfo {
  cluster_id: number;
  region_name: string;
  center_lat: number;
  center_lng: number;
  total_attractions: number;
  total_pear_score: number;
  estimated_time_hours: number;
  travel_time_minutes: number;
  value_per_hour: number;
  is_balanced: boolean;
  optimal_visiting_order: number[];
}

interface PlaceRecommendations {
  day: number;
  cluster_center_lat: number;
  cluster_center_lng: number;
  breakfast_places: any[];
  lunch_places: any[];
  dinner_places: any[];
  accommodation: any[];
  cafes: any[];
}

interface DailyItinerary {
  day: number;
  cluster_info: ClusterInfo;
  attractions: Attraction[];
  total_travel_distance_km: number;
  estimated_total_time_hours: number;
  place_recommendations: PlaceRecommendations;
}

interface PlacesStats {
  success: boolean;
  processing_time_ms: number;
  data_added: number;
  total_places_added: number;
  restaurants: number;
  accommodations: number;
}

interface TravelPlanData {
  query: string;
  total_days: number;
  total_attractions: number;
  daily_itineraries: DailyItinerary[];
  places_stats?: PlacesStats;
  processing_time_ms: number;
  enhancements_applied: string[];
}

interface TravelPlanDisplayProps {
  planData: TravelPlanData;
  onSavePlan?: () => void;
  onDownloadPDF?: () => void;
  onSharePlan?: () => void;
  isLoading?: boolean;
}

const getCategoryIcon = (category: string) => {
  switch (category.toLowerCase()) {
    case 'beach':
      return '🏖️';
    case 'adventure':
      return '🏔️';
    case 'wildlife':
      return '🦁';
    case 'nature':
      return '🌿';
    case 'cultural':
      return '🏛️';
    case 'accommodation':
      return '🏨';
    case 'restaurant':
      return '🍽️';
    default:
      return '📍';
  }
};

const getBudgetColor = (category: string) => {
  switch (category.toLowerCase()) {
    case 'budget':
      return 'bg-green-100 text-green-800';
    case 'mid_range':
      return 'bg-blue-100 text-blue-800';
    case 'luxury':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const AttractionCard: React.FC<{ attraction: Attraction; dayNumber: number }> = ({ attraction, dayNumber }) => {
  return (
    <Card className="mb-4 hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getCategoryIcon(attraction.category)}</span>
            <div>
              <h4 className="font-semibold text-lg">{attraction.name}</h4>
              <Badge variant="outline" className="mt-1">
                {attraction.category}
              </Badge>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              <span>{attraction.pear_score.toFixed(2)}</span>
            </div>
            <Badge variant="secondary" className="mt-1">
              Visit #{attraction.visit_order}
            </Badge>
          </div>
        </div>
        
        {attraction.description && (
          <p className="text-gray-600 text-sm mb-2">{attraction.description}</p>
        )}
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <MapPin className="w-4 h-4" />
            <span>{attraction.region}</span>
          </div>
          <div className="flex items-center space-x-1">
            <span>Lat: {attraction.latitude.toFixed(4)}</span>
            <span>Lng: {attraction.longitude.toFixed(4)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const DayItineraryCard: React.FC<{ itinerary: DailyItinerary }> = ({ itinerary }) => {
  const { day, cluster_info, attractions, total_travel_distance_km, estimated_total_time_hours } = itinerary;
  
  return (
    <Card className="mb-6">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="w-5 h-5" />
            <span>Day {day}</span>
            <Badge variant="outline">{cluster_info.region_name}</Badge>
          </CardTitle>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Route className="w-4 h-4" />
              <span>{total_travel_distance_km.toFixed(1)} km</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4" />
              <span>{estimated_total_time_hours.toFixed(1)} hrs</span>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-6">
        {/* Cluster Information */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h4 className="font-semibold mb-2">Region Overview</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Attractions:</span>
              <div className="font-semibold">{cluster_info.total_attractions}</div>
            </div>
            <div>
              <span className="text-gray-600">Total Score:</span>
              <div className="font-semibold">{cluster_info.total_pear_score.toFixed(2)}</div>
            </div>
            <div>
              <span className="text-gray-600">Travel Time:</span>
              <div className="font-semibold">{Math.round(cluster_info.travel_time_minutes)} min</div>
            </div>
            <div>
              <span className="text-gray-600">Value/Hour:</span>
              <div className="font-semibold">{cluster_info.value_per_hour.toFixed(3)}</div>
            </div>
          </div>
          
          <div className="mt-2 flex items-center space-x-2">
            <Badge variant={cluster_info.is_balanced ? "default" : "secondary"}>
              {cluster_info.is_balanced ? "Balanced Itinerary" : "Concentrated Tour"}
            </Badge>
          </div>
        </div>

        {/* Attractions List */}
        <div>
          <h4 className="font-semibold mb-3 flex items-center space-x-2">
            <MapPin className="w-4 h-4" />
            <span>Attractions to Visit</span>
          </h4>
          <div className="space-y-3">
            {attractions.map((attraction) => (
              <AttractionCard 
                key={attraction.id} 
                attraction={attraction} 
                dayNumber={day}
              />
            ))}
          </div>
        </div>

        {/* Place Recommendations */}
        <div className="mt-6 pt-4 border-t">
          <h4 className="font-semibold mb-3 flex items-center space-x-2">
            <Info className="w-4 h-4" />
            <span>Nearby Services</span>
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <Utensils className="w-4 h-4 text-orange-500" />
              <span>Restaurants: {itinerary.place_recommendations.lunch_places?.length || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Bed className="w-4 h-4 text-blue-500" />
              <span>Hotels: {itinerary.place_recommendations.accommodation?.length || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Coffee className="w-4 h-4 text-brown-500" />
              <span>Cafes: {itinerary.place_recommendations.cafes?.length || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Utensils className="w-4 h-4 text-green-500" />
              <span>Breakfast: {itinerary.place_recommendations.breakfast_places?.length || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Utensils className="w-4 h-4 text-red-500" />
              <span>Dinner: {itinerary.place_recommendations.dinner_places?.length || 0}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const PlanSummaryCard: React.FC<{ planData: TravelPlanData }> = ({ planData }) => {
  return (
    <Card className="mb-6">
      <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50">
        <CardTitle className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5" />
          <span>Trip Overview</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{planData.total_days}</div>
            <div className="text-sm text-gray-600">Days</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{planData.total_attractions}</div>
            <div className="text-sm text-gray-600">Attractions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {planData.daily_itineraries.reduce((sum, day) => sum + day.total_travel_distance_km, 0).toFixed(0)}
            </div>
            <div className="text-sm text-gray-600">Total KM</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {Math.round(planData.processing_time_ms / 1000)}s
            </div>
            <div className="text-sm text-gray-600">Generated In</div>
          </div>
        </div>
        
        <Separator className="my-4" />
        
        <div>
          <h4 className="font-semibold mb-2">Your Query</h4>
          <p className="text-gray-700 italic">"{planData.query}"</p>
        </div>
        
        {planData.enhancements_applied && planData.enhancements_applied.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Enhancements Applied</h4>
            <div className="flex flex-wrap gap-2">
              {planData.enhancements_applied.map((enhancement, index) => (
                <Badge key={index} variant="outline" className="capitalize">
                  {enhancement}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const renderEnhancementStats = (placesStats?: PlacesStats) => {
  // Return null if placesStats is undefined or null
  if (!placesStats) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Info className="w-5 h-5" />
            <span>Enhancement Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 text-gray-600">
            <AlertCircle className="w-4 h-4" />
            <span>No enhancement data available</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Info className="w-5 h-5" />
          <span>Enhancement Status</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-2 mb-4">
          {placesStats.success ? (
            <>
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span className="text-green-700 font-medium">Places enhancement successful</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-700 font-medium">Places enhancement failed</span>
            </>
          )}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Processing Time:</span>
            <div className="font-semibold">{Math.round(placesStats.processing_time_ms)}ms</div>
          </div>
          <div>
            <span className="text-gray-600">Data Added:</span>
            <div className="font-semibold">{placesStats.data_added}</div>
          </div>
          <div>
            <span className="text-gray-600">Restaurants:</span>
            <div className="font-semibold">{placesStats.restaurants}</div>
          </div>
          <div>
            <span className="text-gray-600">Accommodations:</span>
            <div className="font-semibold">{placesStats.accommodations}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const TravelPlanDisplay: React.FC<TravelPlanDisplayProps> = ({ 
  planData, 
  onSavePlan, 
  onDownloadPDF, 
  onSharePlan,
  isLoading = false 
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your travel plan...</p>
        </div>
      </div>
    );
  }

  if (!planData) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600">No plan data available.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Action Buttons */}
      <div className="flex justify-end space-x-4 mb-6">
        {onSavePlan && (
          <Button onClick={onSavePlan} variant="outline" className="flex items-center space-x-2">
            <Heart className="w-4 h-4" />
            <span>Save Plan</span>
          </Button>
        )}
        {onDownloadPDF && (
          <Button onClick={onDownloadPDF} variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </Button>
        )}
        {onSharePlan && (
          <Button onClick={onSharePlan} variant="outline" className="flex items-center space-x-2">
            <Share2 className="w-4 h-4" />
            <span>Share</span>
          </Button>
        )}
      </div>

      {/* Plan Summary */}
      <PlanSummaryCard planData={planData} />
      
      {/* Enhancement Stats */}
      {renderEnhancementStats(planData.places_stats)}
      
      {/* Daily Itineraries */}
      <div>
        <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
          <Calendar className="w-6 h-6" />
          <span>Daily Itinerary</span>
        </h2>
        
        {planData.daily_itineraries.map((itinerary) => (
          <DayItineraryCard key={itinerary.day} itinerary={itinerary} />
        ))}
      </div>
      
      {/* Footer Actions */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <div className="text-center">
          <h3 className="font-semibold mb-2">Ready for your Sri Lankan adventure?</h3>
          <p className="text-gray-600 mb-4">
            Your personalized {planData.total_days}-day itinerary covers {planData.total_attractions} amazing attractions.
          </p>
          <div className="flex justify-center space-x-4">
            {onSavePlan && (
              <Button onClick={onSavePlan} className="flex items-center space-x-2">
                <Heart className="w-4 h-4" />
                <span>Save to My Trips</span>
              </Button>
            )}
            {onDownloadPDF && (
              <Button onClick={onDownloadPDF} variant="outline" className="flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Get PDF Guide</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TravelPlanDisplay;
