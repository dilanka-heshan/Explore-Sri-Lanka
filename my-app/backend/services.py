from typing import List, Optional, Dict, Any
from database import DatabaseManager
from models import *
import uuid
from datetime import datetime

class BaseService:
    def __init__(self, db_client):
        self.db = db_client
        self.db_manager = DatabaseManager()

class DestinationService(BaseService):
    async def get_destinations(
        self,
        region: Optional[str] = None,
        destination_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[DestinationResponse]:
        """Get destinations with optional filtering"""
        query = self.db.table('destinations').select('*')
        
        if region and region != 'All':
            query = query.eq('region', region)
        
        if destination_type and destination_type != 'All':
            query = query.eq('destination_type', destination_type)
        
        if search:
            query = query.or_(f'name.ilike.%{search}%,description.ilike.%{search}%')
        
        query = query.order('name').range(offset, offset + limit - 1)
        
        response = query.execute()
        return [DestinationResponse(**item) for item in response.data]
    
    async def get_destination_by_slug(self, slug: str) -> Optional[DestinationDetailResponse]:
        """Get destination details by slug"""
        response = self.db.table('destinations').select('*').eq('slug', slug).execute()
        
        if not response.data:
            return None
        
        destination_data = response.data[0]
        
        # Get related experiences
        experiences_response = self.db.table('experiences').select('*').eq('destination_id', destination_data['id']).execute()
        experiences = [ExperienceResponse(**exp) for exp in experiences_response.data]
        
        # Get recent reviews
        reviews_response = self.db.table('reviews').select('*').eq('destination_id', destination_data['id']).order('created_at', desc=True).limit(5).execute()
        reviews = [ReviewResponse(**review) for review in reviews_response.data]
        
        destination = DestinationDetailResponse(
            **destination_data,
            experiences=experiences,
            recent_reviews=reviews
        )
        
        return destination

class ExperienceService(BaseService):
    async def get_experiences(
        self,
        category: Optional[str] = None,
        destination_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ExperienceResponse]:
        """Get experiences with optional filtering"""
        query = self.db.table('experiences').select('*, destinations(*)')
        
        if category:
            query = query.eq('category', category)
        
        if destination_id:
            query = query.eq('destination_id', destination_id)
        
        query = query.order('title').range(offset, offset + limit - 1)
        
        response = query.execute()
        experiences = []
        
        for item in response.data:
            destination_data = item.pop('destinations', None)
            experience = ExperienceResponse(**item)
            if destination_data:
                experience.destination = DestinationResponse(**destination_data)
            experiences.append(experience)
        
        return experiences
    
    async def get_experience_by_slug(self, slug: str) -> Optional[ExperienceDetailResponse]:
        """Get experience details by slug"""
        response = self.db.table('experiences').select('*, destinations(*)').eq('slug', slug).execute()
        
        if not response.data:
            return None
        
        item = response.data[0]
        destination_data = item.pop('destinations', None)
        
        experience = ExperienceDetailResponse(**item)
        if destination_data:
            experience.destination = DestinationResponse(**destination_data)
        
        return experience

class ItineraryService(BaseService):
    async def get_itineraries(
        self,
        trip_type: Optional[str] = None,
        duration_min: Optional[int] = None,
        duration_max: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ItineraryResponse]:
        """Get itineraries with optional filtering"""
        query = self.db.table('itineraries').select('*')
        
        if trip_type:
            query = query.eq('trip_type', trip_type)
        
        if duration_min:
            query = query.gte('duration_days', duration_min)
        
        if duration_max:
            query = query.lte('duration_days', duration_max)
        
        if price_min:
            query = query.gte('price', price_min)
        
        if price_max:
            query = query.lte('price', price_max)
        
        query = query.order('title').range(offset, offset + limit - 1)
        
        response = query.execute()
        return [ItineraryResponse(**item) for item in response.data]
    
    async def get_itinerary_by_slug(self, slug: str) -> Optional[ItineraryDetailResponse]:
        """Get itinerary details by slug"""
        response = self.db.table('itineraries').select('*').eq('slug', slug).execute()
        
        if not response.data:
            return None
        
        return ItineraryDetailResponse(**response.data[0])

class BlogService(BaseService):
    async def get_blog_posts(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        published_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> List[BlogPostResponse]:
        """Get blog posts with optional filtering"""
        query = self.db.table('blog_posts').select('*')
        
        if published_only:
            query = query.eq('published', True)
        
        if category:
            query = query.eq('category', category)
        
        if tag:
            query = query.contains('tags', [tag])
        
        if search:
            query = query.or_(f'title.ilike.%{search}%,excerpt.ilike.%{search}%,content.ilike.%{search}%')
        
        query = query.order('published_at', desc=True).range(offset, offset + limit - 1)
        
        response = query.execute()
        return [BlogPostResponse(**item) for item in response.data]
    
    async def get_blog_post_by_slug(self, slug: str) -> Optional[BlogPostDetailResponse]:
        """Get blog post details by slug"""
        response = self.db.table('blog_posts').select('*').eq('slug', slug).execute()
        
        if not response.data:
            return None
        
        return BlogPostDetailResponse(**response.data[0])

class ReviewService(BaseService):
    async def get_destination_reviews(
        self,
        destination_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[ReviewResponse]:
        """Get reviews for a destination"""
        response = self.db.table('reviews').select('*').eq('destination_id', destination_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return [ReviewResponse(**item) for item in response.data]
    
    async def create_review(self, destination_id: str, review: ReviewCreate) -> ReviewResponse:
        """Create a new review"""
        review_data = review.dict()
        review_data['destination_id'] = destination_id
        review_data['id'] = str(uuid.uuid4())
        review_data['created_at'] = datetime.now()
        
        response = self.db.table('reviews').insert(review_data).execute()
        
        # Update destination rating
        await self._update_destination_rating(destination_id)
        
        return ReviewResponse(**response.data[0])
    
    async def _update_destination_rating(self, destination_id: str):
        """Update destination average rating and review count"""
        # Get all reviews for this destination
        reviews_response = self.db.table('reviews').select('rating').eq('destination_id', destination_id).execute()
        
        if reviews_response.data:
            ratings = [review['rating'] for review in reviews_response.data]
            avg_rating = sum(ratings) / len(ratings)
            review_count = len(ratings)
            
            # Update destination
            self.db.table('destinations').update({
                'rating': round(avg_rating, 1),
                'review_count': review_count
            }).eq('id', destination_id).execute()

class BookingService(BaseService):
    async def create_booking(self, booking: BookingCreate) -> BookingResponse:
        """Create a new booking"""
        booking_data = booking.dict()
        booking_data['id'] = str(uuid.uuid4())
        booking_data['status'] = BookingStatus.PENDING
        booking_data['created_at'] = datetime.now()
        
        response = self.db.table('bookings').insert(booking_data).execute()
        
        # Get itinerary details
        itinerary_response = self.db.table('itineraries').select('*').eq('id', booking.itinerary_id).execute()
        itinerary = ItineraryResponse(**itinerary_response.data[0]) if itinerary_response.data else None
        
        booking_result = BookingResponse(**response.data[0])
        booking_result.itinerary = itinerary
        
        return booking_result
    
    async def get_booking(self, booking_id: str) -> Optional[BookingResponse]:
        """Get booking by ID"""
        response = self.db.table('bookings').select('*, itineraries(*)').eq('id', booking_id).execute()
        
        if not response.data:
            return None
        
        item = response.data[0]
        itinerary_data = item.pop('itineraries', None)
        
        booking = BookingResponse(**item)
        if itinerary_data:
            booking.itinerary = ItineraryResponse(**itinerary_data)
        
        return booking

class NewsletterService(BaseService):
    async def subscribe(self, email: str) -> bool:
        """Subscribe email to newsletter"""
        try:
            data = {
                'id': str(uuid.uuid4()),
                'email': email,
                'subscribed_at': datetime.now(),
                'active': True
            }
            
            self.db.table('newsletter_subscriptions').insert(data).execute()
            return True
        except Exception as e:
            # Handle duplicate email case
            if 'duplicate key' in str(e).lower():
                return True  # Already subscribed
            raise e

class ContactService(BaseService):
    async def create_message(self, message: ContactMessage) -> bool:
        """Create a contact message"""
        message_data = message.dict()
        message_data['id'] = str(uuid.uuid4())
        message_data['created_at'] = datetime.now()
        message_data['replied'] = False
        
        self.db.table('contact_messages').insert(message_data).execute()
        return True

class MediaService(BaseService):
    async def get_media_items(
        self,
        category: Optional[str] = None,
        destination_id: Optional[str] = None,
        featured_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[MediaResponse]:
        """Get media gallery items"""
        query = self.db.table('media_gallery').select('*, destinations(*)')
        
        if category:
            query = query.eq('category', category)
        
        if destination_id:
            query = query.eq('destination_id', destination_id)
        
        if featured_only:
            query = query.eq('featured', True)
        
        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)
        
        response = query.execute()
        media_items = []
        
        for item in response.data:
            destination_data = item.pop('destinations', None)
            media = MediaResponse(**item)
            if destination_data:
                media.destination = DestinationResponse(**destination_data)
            media_items.append(media)
        
        return media_items

class SearchService(BaseService):
    async def search_content(
        self,
        query: str,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> SearchResponse:
        """Search across destinations, experiences, and blog posts"""
        results = []
        
        # Search destinations
        if not content_type or content_type == 'destinations':
            dest_response = self.db.table('destinations').select('id, name, description, image_url, slug').or_(f'name.ilike.%{query}%,description.ilike.%{query}%').limit(limit).execute()
            
            for item in dest_response.data:
                results.append(SearchResult(
                    type='destination',
                    id=item['id'],
                    title=item['name'],
                    description=item['description'],
                    image_url=item['image_url'],
                    slug=item['slug']
                ))
        
        # Search experiences
        if not content_type or content_type == 'experiences':
            exp_response = self.db.table('experiences').select('id, title, description, image_url, slug').or_(f'title.ilike.%{query}%,description.ilike.%{query}%').limit(limit).execute()
            
            for item in exp_response.data:
                results.append(SearchResult(
                    type='experience',
                    id=item['id'],
                    title=item['title'],
                    description=item['description'],
                    image_url=item['image_url'],
                    slug=item['slug']
                ))
        
        # Search blog posts
        if not content_type or content_type == 'blog':
            blog_response = self.db.table('blog_posts').select('id, title, excerpt, image_url, slug').eq('published', True).or_(f'title.ilike.%{query}%,excerpt.ilike.%{query}%,content.ilike.%{query}%').limit(limit).execute()
            
            for item in blog_response.data:
                results.append(SearchResult(
                    type='blog',
                    id=item['id'],
                    title=item['title'],
                    description=item['excerpt'],
                    image_url=item['image_url'],
                    slug=item['slug']
                ))
        
        return SearchResponse(
            query=query,
            total_results=len(results),
            results=results[:limit]
        )
