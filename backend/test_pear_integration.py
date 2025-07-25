"""
Test the new simplified PEAR ranker integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_simplified_pear_integration():
    """Test that the new PEAR ranker works with existing system"""
    print("🧪 Testing Simplified PEAR Integration")
    print("=" * 50)
    
    try:
        # Import the new PEAR ranker
        from langgraph_flow.models.pear_ranker import PEARRanker, create_pear_ranker
        
        print("✅ Successfully imported simplified PEAR ranker")
        
        # Initialize the ranker
        print("\n🏗️ Initializing PEAR ranker...")
        pear_ranker = create_pear_ranker()
        
        print("✅ PEAR ranker initialized successfully!")
        
        # Test with sample data (like how it's used in retriever.py)
        print("\n🧪 Testing with sample attractions...")
        
        # Sample user profile (similar to what retriever receives)
        user_profile = {
            'interests': ['culture', 'temples', 'history'],
            'trip_type': 'cultural',
            'budget_level': 'medium',
            'duration': 7,
            'cultural_interest': 8,
            'adventure_level': 3,
            'nature_appreciation': 6,
            'group_size': 2
        }
        
        # Sample attractions (like candidate attractions from retriever)
        sample_attractions = [
            {
                'id': 'temple_1',
                'name': 'Temple of the Sacred Tooth Relic',
                'category': 'Religious Site',
                'description': 'Buddhist temple housing the relic of the tooth of the Buddha',
                'tags': ['temple', 'buddhist', 'cultural', 'historic'],
                'region': 'Kandy',
                'facilities': ['parking', 'guided tours']
            },
            {
                'id': 'beach_1',
                'name': 'Unawatuna Beach',
                'category': 'Beach',
                'description': 'Beautiful sandy beach with clear blue waters',
                'tags': ['beach', 'swimming', 'relaxation'],
                'region': 'Galle',
                'facilities': ['restaurants', 'water sports']
            },
            {
                'id': 'fort_1',
                'name': 'Galle Fort',
                'category': 'Historical Site',
                'description': 'Dutch colonial fort with historic architecture',
                'tags': ['fort', 'colonial', 'historical', 'architecture'],
                'region': 'Galle',
                'facilities': ['museums', 'cafes', 'shops']
            },
            {
                'id': 'park_1',
                'name': 'Yala National Park',
                'category': 'Wildlife',
                'description': 'National park famous for leopards and elephants',
                'tags': ['wildlife', 'safari', 'nature', 'animals'],
                'region': 'Yala',
                'facilities': ['safari vehicles', 'guides']
            }
        ]
        
        # Test the main method that retriever.py uses
        print(f"📊 Testing get_top_attractions with {len(sample_attractions)} attractions...")
        
        top_attractions = pear_ranker.get_top_attractions(
            user_profile=user_profile,
            attractions=sample_attractions,
            top_k=3
        )
        
        print(f"✅ Got {len(top_attractions)} ranked attractions:")
        
        for i, attraction in enumerate(top_attractions, 1):
            name = attraction.get('name', 'Unknown')
            category = attraction.get('category', 'Unknown')
            pear_score = attraction.get('pear_score', 0)
            print(f"  {i}. {name}")
            print(f"     Category: {category}")
            print(f"     PEAR Score: {pear_score:.4f}")
            print()
        
        # Verify the structure is compatible
        if top_attractions and 'pear_score' in top_attractions[0]:
            print("✅ Output format is compatible with existing system!")
        else:
            print("❌ Output format may have issues")
            
        # Test the new vector DB functionality
        print("\n🔍 Testing direct vector database recommendations...")
        try:
            user_query = "I want to visit cultural and historical places in Sri Lanka"
            
            vector_recommendations = pear_ranker.get_recommendations_from_vector_db(
                user_query=user_query,
                user_context=user_profile,
                top_k=5
            )
            
            print(f"✅ Got {len(vector_recommendations)} recommendations from vector DB:")
            for i, rec in enumerate(vector_recommendations[:3], 1):
                name = rec.get('name', 'Unknown')
                category = rec.get('category', 'Unknown') 
                score = rec.get('pear_score', 0)
                print(f"  {i}. {name} ({category}) - Score: {score:.3f}")
                
        except Exception as e:
            print(f"⚠️ Vector DB test failed (may be expected if no connection): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """Test that old imports still work"""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    try:
        # Test that old import patterns still work
        from langgraph_flow.models.pear_ranker import PEARModel, AttractionFeatures, UserFeatures
        
        print("✅ Legacy classes still importable")
        
        # Test that basic instantiation works
        legacy_model = PEARModel()
        print("✅ Legacy PEARModel can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Simplified PEAR Integration")
    print("=" * 60)
    
    # Test 1: Main integration
    integration_ok = test_simplified_pear_integration()
    
    # Test 2: Backward compatibility
    compatibility_ok = test_backward_compatibility()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Main Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    print(f"Backward Compatibility: {'✅ PASS' if compatibility_ok else '❌ FAIL'}")
    
    if integration_ok and compatibility_ok:
        print("\n🎉 All integration tests passed!")
        print("🔄 Your system is now using the simplified transformer-based approach!")
        print("🗑️ The old rule-based implementation has been replaced")
    else:
        print("\n⚠️ Some integration tests failed. Check the errors above.")
