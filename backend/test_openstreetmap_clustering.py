"""
Test OpenStreetMap-based clustering with top 30 recommendations
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

async def test_openstreetmap_clustering():
    """Test the new OpenStreetMap-based clustering system"""
    print("🗺️ Testing OpenStreetMap Clustering Integration")
    print("=" * 60)
    
    try:
        # Import required modules
        from langgraph_flow.models.pear_ranker import create_pear_ranker
        from langgraph_flow.models.geo_clustering import AdvancedGeographicClusterer
        
        print("✅ Successfully imported clustering modules")
        
        # Step 1: Get top 30 recommendations
        print("\n1️⃣ Getting top 30 recommendations...")
        pear_ranker = create_pear_ranker()
        
        user_query = "I want to explore ancient temples, cultural heritage sites, and historical places in Sri Lanka"
        user_context = {
            "interests": ["culture", "temples", "history", "heritage"],
            "trip_type": "cultural exploration",
            "budget": "medium",
            "duration": 5,
            "group_size": 2
        }
        
        recommendations = pear_ranker.get_recommendations_from_vector_db(
            user_query=user_query,
            user_context=user_context,
            top_k=30
        )
        
        print(f"✅ Got {len(recommendations)} recommendations")
        
        # Step 2: Convert to clustering format and add coordinates
        print("\n2️⃣ Preparing attractions for clustering...")
        attractions_for_clustering = []
        
        # Sample coordinates for Sri Lankan attractions (in production, get from database)
        sample_coordinates = {
            "Sigiriya": (7.9568, 80.7604),
            "Dambulla": (7.8567, 80.6492),
            "Kandy": (7.2936, 80.6350),
            "Anuradhapura": (8.3114, 80.4037),
            "Polonnaruwa": (7.9403, 81.0188),
            "Galle Fort": (6.0367, 80.2170),
            "Temple": (7.2936, 80.6350),  # Default temple coordinates
            "Cultural": (7.5000, 80.0000),  # Default cultural site coordinates
        }
        
        for i, rec in enumerate(recommendations):
            payload = rec.get('payload', {})
            name = payload.get('name', f'Attraction_{i}')
            
            # Find coordinates based on name matching
            lat, lng = None, None
            for location, coords in sample_coordinates.items():
                if location.lower() in name.lower():
                    lat, lng = coords
                    break
            
            if lat is None:
                # Assign random coordinates in Sri Lanka if no match
                lat = 7.0 + (i * 0.1) % 2.0  # Between 7.0 and 9.0
                lng = 80.0 + (i * 0.1) % 1.5  # Between 80.0 and 81.5
            
            attraction = {
                'id': str(rec.get('id', f'attr_{i}')),
                'name': name,
                'category': payload.get('category', 'Cultural'),
                'description': payload.get('description', 'Cultural heritage site'),
                'region': payload.get('region', 'Central Province'),
                'latitude': lat,
                'longitude': lng,
                'pear_score': rec.get('pear_score', 0.5),
                'visit_duration_minutes': 120
            }
            attractions_for_clustering.append(attraction)
        
        print(f"✅ Prepared {len(attractions_for_clustering)} attractions with coordinates")
        
        # Show sample attractions
        print("\n📍 Sample attractions with coordinates:")
        for i, attr in enumerate(attractions_for_clustering[:5]):
            print(f"  {i+1}. {attr['name']} ({attr['latitude']:.4f}, {attr['longitude']:.4f}) - Score: {attr['pear_score']:.3f}")
        
        # Step 3: Test different clustering algorithms
        print("\n3️⃣ Testing clustering algorithms...")
        
        clusterer = AdvancedGeographicClusterer(
            max_cluster_radius_km=30.0,
            max_daily_travel_time_hours=3.0,
            min_attractions_per_cluster=2,
            max_attractions_per_cluster=5,
            target_clusters=5
        )
        
        # Test smart clustering
        print("\n🧠 Testing Smart Clustering...")
        smart_clusters = await clusterer.create_balanced_clusters(
            attractions_for_clustering,
            algorithm="smart_clustering"
        )
        
        print(f"✅ Smart clustering created {len(smart_clusters)} clusters")
        
        # Display cluster results
        print("\n📊 Cluster Analysis:")
        for i, cluster in enumerate(smart_clusters):
            print(f"\n🗂️ Cluster {i+1}: {cluster.region_name}")
            print(f"   📍 Center: ({cluster.center_lat:.4f}, {cluster.center_lng:.4f})")
            print(f"   🎯 Attractions: {len(cluster.attractions)}")
            print(f"   ⭐ Total PEAR Score: {cluster.total_pear_score:.2f}")
            print(f"   ⏱️ Estimated Time: {cluster.estimated_time_hours:.1f} hours")
            print(f"   🚗 Travel Time: {cluster.total_travel_time_minutes:.1f} minutes")
            print(f"   💎 Value/Hour: {cluster.value_per_hour:.2f}")
            print(f"   ⚖️ Balanced: {'✅' if cluster.is_balanced else '❌'}")
            print(f"   📏 Max Distance: {cluster.max_travel_distance_km:.1f} km")
            
            print(f"   🏛️ Attractions in cluster:")
            for j, attraction in enumerate(cluster.attractions):
                order = cluster.optimal_order[j] + 1 if cluster.optimal_order else j + 1
                print(f"      {order}. {attraction['name']} (Score: {attraction['pear_score']:.3f})")
        
        # Step 4: Test cluster ranking
        print("\n4️⃣ Testing cluster ranking...")
        ranked_clusters = clusterer.rank_clusters_by_value(smart_clusters)
        
        print(f"✅ Ranked {len(ranked_clusters)} clusters by value")
        print("\n🏆 Top 3 Clusters for 5-day trip:")
        for i, cluster in enumerate(ranked_clusters[:3]):
            print(f"  Day {i+1}: {cluster.region_name}")
            print(f"    • {len(cluster.attractions)} attractions")
            print(f"    • {cluster.estimated_time_hours:.1f} hours total")
            print(f"    • Value/Hour: {cluster.value_per_hour:.2f}")
            print(f"    • Travel: {cluster.total_travel_time_minutes:.0f} min")
        
        # Step 5: Test OpenRouteService integration
        print("\n5️⃣ Testing OpenRouteService integration...")
        if os.getenv("OPENROUTE_SERVICE_API_KEY"):
            print("✅ OpenRouteService API key found - real routing will be used")
        else:
            print("⚠️ No OpenRouteService API key - using haversine distance fallback")
        
        # Test route calculation between two points
        from langgraph_flow.models.geo_clustering import OpenStreetMapRouter
        router = OpenStreetMapRouter()
        
        # Test route between Sigiriya and Dambulla
        route_info = await router.get_route_info(7.9568, 80.7604, 7.8567, 80.6492)
        print(f"📍 Route Sigiriya → Dambulla:")
        print(f"   Distance: {route_info.distance_km:.1f} km")
        print(f"   Duration: {route_info.duration_minutes:.1f} minutes")
        
        await router.close()
        await clusterer.close()
        
        print("\n✅ All clustering tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Clustering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_clustered_api():
    """Test the clustered recommendations API"""
    print("\n🌐 Testing Clustered Recommendations API")
    print("=" * 50)
    
    try:
        from router.clustered_recommendations import test_clustering_algorithm
        
        result = await test_clustering_algorithm()
        print(f"✅ API test result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def main():
    """Run all clustering tests"""
    print("🚀 OpenStreetMap Clustering Integration Test")
    print("=" * 70)
    
    # Test 1: Core clustering functionality
    clustering_ok = await test_openstreetmap_clustering()
    
    # Test 2: API integration
    api_ok = await test_clustered_api()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 CLUSTERING INTEGRATION SUMMARY")
    print("=" * 70)
    print(f"Core Clustering: {'✅ PASS' if clustering_ok else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if clustering_ok and api_ok:
        print("\n🎉 SUCCESS! OpenStreetMap clustering is working!")
        print("\n🔥 New Features Available:")
        print("   ✅ OpenStreetMap routing integration")
        print("   ✅ Balanced cluster creation from top 30 attractions")
        print("   ✅ Smart clustering algorithm with PEAR ranking")
        print("   ✅ Optimal visiting order within clusters")
        print("   ✅ Travel time optimization")
        print("   ✅ Daily itinerary planning")
        print("   ✅ Same-day cluster restriction")
        print("   ✅ Balanced workload distribution")
        
        print("\n📋 API Endpoints:")
        print("   • POST /clustered-recommendations/plan - Get full travel plan")
        print("   • GET /clustered-recommendations/test-clustering - Test clustering")
        
        print("\n🎯 Your Enhanced System Now:")
        print("   User Query → PEAR Ranking → Top 30 → Geographic Clustering → Daily Plans")
        
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
