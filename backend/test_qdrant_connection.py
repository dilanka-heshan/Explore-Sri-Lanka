"""
Simple test to check Qdrant connection
"""
import os
from dotenv import load_dotenv

def test_qdrant_connection():
    """Test basic Qdrant connection"""
    print("🔍 Testing Qdrant Connection")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    try:
        from qdrant_client import QdrantClient
        
        # Get configuration from environment
        qdrant_url = os.getenv("QDRANT_HOST", "https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "exploresl")
        
        print(f"🔗 Connecting to: {qdrant_url}")
        print(f"📚 Collection: {collection_name}")
        print(f"🔑 API Key: {'✅ Found' if qdrant_api_key else '❌ Missing'}")
        
        if not qdrant_api_key:
            print("❌ No API key found in environment variables!")
            return False
        
        # Create client
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        
        # Test connection by getting collection info
        print("\n📊 Testing connection...")
        collection_info = client.get_collection(collection_name)
        
        print(f"✅ Connection successful!")
        print(f"📈 Collection has {collection_info.points_count} points")
        print(f"🔢 Vector size: {collection_info.config.params.vectors.size}")
        
        # Test search functionality
        print("\n🔍 Testing search...")
        results = client.scroll(
            collection_name=collection_name,
            limit=3,
            with_payload=True
        )
        
        print(f"✅ Retrieved {len(results[0])} sample records:")
        for i, point in enumerate(results[0], 1):
            name = point.payload.get('name', 'Unknown') if point.payload else 'No payload'
            print(f"  {i}. {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_simplified_ranker():
    """Test the simplified ranker initialization"""
    print("\n🧠 Testing Simplified PEAR Ranker")
    print("=" * 40)
    
    try:
        from langgraph_flow.models.simplified_pear_ranker import create_travel_ranker
        
        # Load environment variables
        load_dotenv()
        
        qdrant_url = os.getenv("QDRANT_HOST", "https://50ab27b1-fac6-42dc-88af-ef70408179e6.us-east-1-0.aws.cloud.qdrant.io")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "exploresl")
        
        print(f"🏗️ Initializing ranker...")
        ranker = create_travel_ranker(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name=collection_name
        )
        
        print("✅ Simplified PEAR Ranker initialized successfully!")
        
        # Test with a simple query
        print("\n🧪 Testing with sample query...")
        test_query = "I want hike some places and as well as explore cultural heritages"
        test_context = {
            "interests": ["culture", "mountains"],
            "budget": "medium",
            "duration": 5
        }
        
        recommendations = ranker.get_recommendations(
            user_query=test_query,
            user_context=test_context,
            top_k=5
        )
        
        print(f"✅ Got {len(recommendations)} recommendations!")
        for i, rec in enumerate(recommendations[:3], 1):
            name = rec.get('payload', {}).get('name', 'Unknown')
            score = rec.get('combined_score', 0)
            print(f"  {i}. {name} (Score: {score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ranker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Qdrant Connection Test")
    print("=" * 50)
    
    # Test 1: Basic connection
    connection_ok = test_qdrant_connection()
    
    # Test 2: Simplified ranker (only if connection works)
    if connection_ok:
        ranker_ok = test_simplified_ranker()
    else:
        ranker_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"Qdrant Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Simplified Ranker: {'✅ PASS' if ranker_ok else '❌ FAIL'}")
    
    if connection_ok and ranker_ok:
        print("\n🎉 All tests passed! Your system is ready!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
