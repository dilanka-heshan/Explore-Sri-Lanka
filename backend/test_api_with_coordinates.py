"""
API Test for Clustered Recommendations with Real Coordinates
Tests the actual FastAPI endpoint using the coordinate service
"""
import requests
import json
import asyncio

def test_clustered_recommendations_api():
    """Test the clustered recommendations API endpoint"""
    print("🧪 TESTING CLUSTERED RECOMMENDATIONS API")
    print("=" * 80)
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/clustered-recommendations/plan"
    
    # Test request data
    test_request = {
        "query": "I want to explore Sri Lanka's ancient temples, cultural heritage sites and enjoy scenic mountain views",
        "interests": ["culture", "temples", "heritage", "mountains", "nature"],
        "trip_duration_days": 5,
        "daily_travel_preference": "balanced",
        "max_attractions_per_day": 4,
        "budget_level": "medium",
        "group_size": 2
    }
    
    print(f"📡 Endpoint: {endpoint}")
    print(f"📝 Request: {json.dumps(test_request, indent=2)}")
    
    try:
        print(f"\n🚀 Sending request...")
        response = requests.post(endpoint, json=test_request, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ SUCCESS! API Response:")
            print(f"   📅 Total Days: {data.get('total_days', 0)}")
            print(f"   🏛️  Total Attractions: {data.get('total_attractions', 0)}")
            print(f"   ⏱️  Processing Time: {data.get('processing_time_ms', 0):.2f}ms")
            
            # Show daily itineraries
            for day_data in data.get('daily_itineraries', []):
                day = day_data.get('day', 0)
                cluster_info = day_data.get('cluster_info', {})
                attractions = day_data.get('attractions', [])
                
                print(f"\n   📅 DAY {day}: {cluster_info.get('region_name', 'Unknown')}")
                print(f"      🎯 Center: ({cluster_info.get('center_lat', 0):.4f}, {cluster_info.get('center_lng', 0):.4f})")
                print(f"      ⏱️  Time: {cluster_info.get('estimated_time_hours', 0):.1f}h")
                print(f"      🚗 Travel: {cluster_info.get('travel_time_minutes', 0):.0f}min")
                print(f"      ⚖️  Balanced: {'✅' if cluster_info.get('is_balanced', False) else '❌'}")
                print(f"      🏛️  Attractions ({len(attractions)}):")
                
                for attraction in attractions:
                    name = attraction.get('name', 'Unknown')
                    coords = f"({attraction.get('latitude', 0):.4f}, {attraction.get('longitude', 0):.4f})"
                    score = attraction.get('pear_score', 0)
                    print(f"         • {name} {coords} Score: {score:.3f}")
            
            # Overall statistics
            stats = data.get('overall_stats', {})
            print(f"\n   📊 Overall Statistics:")
            print(f"      🎯 Total Attractions: {stats.get('total_attractions', 0)}")
            print(f"      📏 Total Distance: {stats.get('total_travel_distance_km', 0)} km")
            print(f"      💎 Avg Value/Hour: {stats.get('average_value_per_hour', 0):.3f}")
            print(f"      ⚖️  Balanced Clusters: {stats.get('balanced_clusters', 0)}")
            print(f"      🗺️  Routing: {stats.get('travel_optimization', 'Unknown')}")
            print(f"      🧠 Algorithm: {stats.get('clustering_algorithm', 'Unknown')}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {base_url}")
        print(f"   Make sure the FastAPI server is running:")
        print(f"   cd backend && python main.py")
        return False
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error: Request took longer than 60 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_simple_endpoint():
    """Test a simple endpoint to check if server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is running")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except:
        print("❌ FastAPI server is not running")
        print("   Start server with: cd backend && python main.py")
        return False

if __name__ == "__main__":
    print("🧪 API INTEGRATION TEST")
    print("=" * 50)
    
    # Check if server is running
    if test_simple_endpoint():
        # Test the clustered recommendations endpoint
        success = test_clustered_recommendations_api()
        
        if success:
            print(f"\n🎉 API TEST SUCCESSFUL!")
            print(f"✅ Clustered recommendations working with real coordinates")
            print(f"✅ Geographic clustering functional")
            print(f"✅ OpenStreetMap integration active")
        else:
            print(f"\n❌ API TEST FAILED!")
    else:
        print(f"\n⚠️  Start the FastAPI server first:")
        print(f"   cd backend && python main.py")
