"""
Travel Plan Management Service
Handles storage, retrieval, and management of user travel plans
"""
import json
import os
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import text, desc, asc, and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

from models.database import get_db, supabase
from models.travel_plan_models import (
    UserTravelPlan,
    TravelPlanCreate,
    TravelPlanUpdate,
    TravelPlanQuery,
    TravelPlanSummary,
    TravelPlanStats,
    PDFGenerationRequest,
    PDFGenerationResponse,
    TravelPlanShare,
    SharedTravelPlan,
    TripStatus,
    TripPrivacy
)

logger = logging.getLogger(__name__)


class TravelPlanService:
    """Service for managing user travel plans"""
    
    def __init__(self):
        pass
    
    def get_session(self) -> Session:
        """Get database session"""
        return next(get_db())
    
    def _convert_datetime_strings(self, plan_dict: dict) -> dict:
        """Convert datetime strings from database back to datetime objects"""
        datetime_fields = ['created_at', 'updated_at', 'planned_start_date', 
                          'actual_start_date', 'actual_end_date', 'last_accessed']
        
        for field in datetime_fields:
            if plan_dict.get(field) and isinstance(plan_dict[field], str):
                try:
                    # Handle both ISO format and Supabase format
                    plan_dict[field] = datetime.fromisoformat(plan_dict[field].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    # If conversion fails, set to None
                    plan_dict[field] = None
                    
        return plan_dict
    
    async def create_travel_plan(
        self, 
        user_id: str, 
        plan_data: TravelPlanCreate
    ) -> UserTravelPlan:
        """Create a new travel plan for a user"""
        try:
            # Generate unique ID
            plan_id = str(uuid4())
            
            # Extract destination summary from travel plan data
            destination_summary = self._extract_destination_summary(plan_data.travel_plan_data)
            
            # Prepare data for database
            travel_plan = {
                'id': plan_id,
                'user_id': user_id,
                'title': plan_data.title,
                'description': plan_data.description,
                'destination_summary': destination_summary,
                'trip_duration_days': plan_data.trip_duration_days,
                'budget_level': plan_data.budget_level,
                'trip_type': plan_data.trip_type,
                'original_query': plan_data.original_query,
                'interests': plan_data.interests,
                'travel_plan_data': json.dumps(plan_data.travel_plan_data, cls=DateTimeEncoder),
                'planned_start_date': plan_data.planned_start_date.isoformat() if plan_data.planned_start_date else None,
                'privacy': plan_data.privacy.value,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert into database using Supabase
            if supabase:
                result = supabase.table('user_travel_plans').insert(travel_plan).execute()
                if result.data:
                    # Log creation
                    await self._log_modification(
                        plan_id, user_id, 'created', 
                        description=f"Travel plan '{plan_data.title}' created"
                    )
                    
                    # Convert back to UserTravelPlan model
                    plan_dict = result.data[0]
                    plan_dict['travel_plan_data'] = json.loads(plan_dict['travel_plan_data'])
                    plan_dict = self._convert_datetime_strings(plan_dict)
                    
                    return UserTravelPlan(**plan_dict)
            
            raise Exception("Failed to create travel plan")
            
        except Exception as e:
            logger.error(f"Error creating travel plan: {str(e)}")
            raise e
    
    async def get_travel_plan(
        self, 
        plan_id: str, 
        user_id: str
    ) -> Optional[UserTravelPlan]:
        """Get a specific travel plan by ID"""
        try:
            if supabase:
                # Check if user has access to this plan
                result = supabase.table('user_travel_plans').select('*').or_(
                    f'user_id.eq.{user_id},'
                    f'shared_with.cs.{{{user_id}}},'
                    f'privacy.eq.public'
                ).eq('id', plan_id).execute()
                
                if result.data:
                    plan_dict = result.data[0]
                    plan_dict['travel_plan_data'] = json.loads(plan_dict['travel_plan_data'])
                    plan_dict = self._convert_datetime_strings(plan_dict)
                    
                    # Update last accessed
                    await self._update_last_accessed(plan_id, user_id)
                    
                    return UserTravelPlan(**plan_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting travel plan {plan_id}: {str(e)}")
            return None
    
    async def get_user_travel_plans(
        self, 
        user_id: str, 
        query: TravelPlanQuery
    ) -> Tuple[List[TravelPlanSummary], int]:
        """Get user's travel plans with filtering and pagination"""
        try:
            if not supabase:
                return [], 0
            
            # Build query conditions
            conditions = [f'user_id.eq.{user_id}']
            
            if query.status:
                conditions.append(f'status.eq.{query.status.value}')
            
            if query.privacy:
                conditions.append(f'privacy.eq.{query.privacy.value}')
            
            if query.favorite_only:
                conditions.append('favorite.eq.true')
            
            if query.budget_level:
                conditions.append(f'budget_level.eq.{query.budget_level}')
            
            if query.trip_type:
                conditions.append(f'trip_type.eq.{query.trip_type}')
            
            if query.date_from:
                conditions.append(f'created_at.gte.{query.date_from.isoformat()}')
            
            if query.date_to:
                conditions.append(f'created_at.lte.{query.date_to.isoformat()}')
            
            # Combine conditions
            filter_query = ','.join(conditions) if len(conditions) > 1 else conditions[0] if conditions else ''
            
            # Execute query with pagination
            query_builder = supabase.table('user_travel_plan_summary').select(
                'id, title, destination_summary, trip_duration_days, budget_level, '
                'trip_type, status, favorite, user_rating, planned_start_date, '
                'created_at, updated_at, times_viewed, pdf_generated'
            )
            
            if filter_query:
                query_builder = query_builder.filter(filter_query)
            
            # Add search functionality
            if query.search_query:
                search_term = query.search_query.lower()
                query_builder = query_builder.or_(
                    f'title.ilike.%{search_term}%,'
                    f'destination_summary.ilike.%{search_term}%'
                )
            
            # Add sorting
            if query.sort_order == 'desc':
                query_builder = query_builder.order(query.sort_by, desc=True)
            else:
                query_builder = query_builder.order(query.sort_by)
            
            # Execute with pagination
            result = query_builder.range(query.offset, query.offset + query.limit - 1).execute()
            
            # Get total count
            count_result = supabase.table('user_travel_plans').select('id', count='exact').eq('user_id', user_id).execute()
            total_count = count_result.count or 0
            
            # Convert to TravelPlanSummary objects
            summaries = []
            if result.data:
                for plan in result.data:
                    plan = self._convert_datetime_strings(plan)
                    summaries.append(TravelPlanSummary(**plan))
            
            return summaries, total_count
            
        except Exception as e:
            logger.error(f"Error getting user travel plans: {str(e)}")
            return [], 0
    
    async def update_travel_plan(
        self, 
        plan_id: str, 
        user_id: str, 
        updates: TravelPlanUpdate
    ) -> Optional[UserTravelPlan]:
        """Update a travel plan"""
        try:
            if not supabase:
                return None
            
            # Check if user has edit access
            access_check = await self._check_edit_access(plan_id, user_id)
            if not access_check:
                raise Exception("User does not have edit access to this travel plan")
            
            # Prepare update data
            update_data = {}
            modifications = []
            
            # Get current plan for comparison
            current_plan = await self.get_travel_plan(plan_id, user_id)
            if not current_plan:
                return None
            
            # Check for changes and build update data
            if updates.title is not None and updates.title != current_plan.title:
                update_data['title'] = updates.title
                modifications.append(f"Title changed from '{current_plan.title}' to '{updates.title}'")
            
            if updates.description is not None and updates.description != current_plan.description:
                update_data['description'] = updates.description
                modifications.append("Description updated")
            
            if updates.status is not None and updates.status != current_plan.status:
                update_data['status'] = updates.status.value
                modifications.append(f"Status changed from '{current_plan.status}' to '{updates.status.value}'")
            
            if updates.privacy is not None and updates.privacy != current_plan.privacy:
                update_data['privacy'] = updates.privacy.value
                modifications.append(f"Privacy changed from '{current_plan.privacy}' to '{updates.privacy.value}'")
            
            if updates.user_rating is not None and updates.user_rating != current_plan.user_rating:
                update_data['user_rating'] = updates.user_rating
                modifications.append(f"Rating set to {updates.user_rating} stars")
            
            if updates.user_notes is not None and updates.user_notes != current_plan.user_notes:
                update_data['user_notes'] = updates.user_notes
                modifications.append("User notes updated")
            
            if updates.favorite is not None and updates.favorite != current_plan.favorite:
                update_data['favorite'] = updates.favorite
                action = "added to" if updates.favorite else "removed from"
                modifications.append(f"Plan {action} favorites")
            
            if updates.planned_start_date is not None and updates.planned_start_date != current_plan.planned_start_date:
                update_data['planned_start_date'] = updates.planned_start_date.isoformat() if updates.planned_start_date else None
                modifications.append("Planned start date updated")
            
            if updates.actual_start_date is not None and updates.actual_start_date != current_plan.actual_start_date:
                update_data['actual_start_date'] = updates.actual_start_date.isoformat() if updates.actual_start_date else None
                modifications.append("Actual start date set")
            
            if updates.actual_end_date is not None and updates.actual_end_date != current_plan.actual_end_date:
                update_data['actual_end_date'] = updates.actual_end_date.isoformat() if updates.actual_end_date else None
                modifications.append("Actual end date set")
            
            if not update_data:
                # No changes to make
                return current_plan
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Execute update
            result = supabase.table('user_travel_plans').update(update_data).eq('id', plan_id).execute()
            
            if result.data:
                # Log modifications
                for mod in modifications:
                    await self._log_modification(plan_id, user_id, 'updated', description=mod)
                
                # Return updated plan
                return await self.get_travel_plan(plan_id, user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating travel plan {plan_id}: {str(e)}")
            raise e
    
    async def delete_travel_plan(self, plan_id: str, user_id: str) -> bool:
        """Delete a travel plan (soft delete by changing status)"""
        try:
            if not supabase:
                return False
            
            # Check if user owns the plan
            plan = await self.get_travel_plan(plan_id, user_id)
            if not plan or plan.user_id != user_id:
                return False
            
            # Soft delete by updating status
            result = supabase.table('user_travel_plans').update({
                'status': 'archived',
                'updated_at': datetime.now()
            }).eq('id', plan_id).execute()
            
            if result.data:
                await self._log_modification(
                    plan_id, user_id, 'deleted', 
                    description="Travel plan archived"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting travel plan {plan_id}: {str(e)}")
            return False
    
    async def get_travel_plan_stats(self, user_id: str) -> TravelPlanStats:
        """Get statistics about user's travel plans"""
        try:
            if not supabase:
                return TravelPlanStats(
                    total_plans=0, draft_plans=0, active_plans=0, completed_plans=0,
                    favorite_plans=0, total_destinations=0, total_trip_days=0,
                    average_rating=None, most_visited_destinations=[],
                    budget_distribution={}, trip_type_distribution={}
                )
            
            # Get stats from the view
            result = supabase.table('user_travel_stats').select('*').eq('user_id', user_id).execute()
            
            if result.data:
                stats_data = result.data[0]
                
                # Get additional data for comprehensive stats
                plans_result = supabase.table('user_travel_plans').select(
                    'destination_summary, budget_level, trip_type'
                ).eq('user_id', user_id).execute()
                
                # Process destination data
                destinations = {}
                budget_dist = {}
                trip_type_dist = {}
                
                if plans_result.data:
                    for plan in plans_result.data:
                        # Count destinations (simplified - could be enhanced with proper parsing)
                        dest = plan.get('destination_summary', '')
                        destinations[dest] = destinations.get(dest, 0) + 1
                        
                        # Budget distribution
                        budget = plan.get('budget_level', '')
                        budget_dist[budget] = budget_dist.get(budget, 0) + 1
                        
                        # Trip type distribution
                        trip_type = plan.get('trip_type', '')
                        trip_type_dist[trip_type] = trip_type_dist.get(trip_type, 0) + 1
                
                # Most visited destinations
                most_visited = [
                    {'destination': dest, 'count': count}
                    for dest, count in sorted(destinations.items(), key=lambda x: x[1], reverse=True)[:5]
                ]
                
                return TravelPlanStats(
                    total_plans=stats_data.get('total_plans', 0),
                    draft_plans=stats_data.get('draft_plans', 0),
                    active_plans=stats_data.get('active_plans', 0),
                    completed_plans=stats_data.get('completed_plans', 0),
                    favorite_plans=stats_data.get('favorite_plans', 0),
                    total_destinations=len(destinations),
                    total_trip_days=stats_data.get('total_trip_days', 0),
                    average_rating=stats_data.get('average_rating'),
                    most_visited_destinations=most_visited,
                    budget_distribution=budget_dist,
                    trip_type_distribution=trip_type_dist
                )
            
            # Return empty stats if no data
            return TravelPlanStats(
                total_plans=0, draft_plans=0, active_plans=0, completed_plans=0,
                favorite_plans=0, total_destinations=0, total_trip_days=0,
                average_rating=None, most_visited_destinations=[],
                budget_distribution={}, trip_type_distribution={}
            )
            
        except Exception as e:
            logger.error(f"Error getting travel plan stats: {str(e)}")
            return TravelPlanStats(
                total_plans=0, draft_plans=0, active_plans=0, completed_plans=0,
                favorite_plans=0, total_destinations=0, total_trip_days=0,
                average_rating=None, most_visited_destinations=[],
                budget_distribution={}, trip_type_distribution={}
            )
    
    # Helper methods
    def _extract_destination_summary(self, travel_plan_data: Dict[str, Any]) -> str:
        """Extract a summary of destinations from travel plan data"""
        try:
            if 'daily_itineraries' in travel_plan_data:
                destinations = set()
                for day in travel_plan_data['daily_itineraries']:
                    if 'cluster_name' in day:
                        destinations.add(day['cluster_name'])
                    if 'attractions' in day:
                        for attraction in day['attractions']:
                            if 'location' in attraction:
                                destinations.add(attraction['location'])
                return ', '.join(list(destinations)[:5])  # Limit to first 5 destinations
            
            if 'summary' in travel_plan_data:
                return travel_plan_data['summary'][:200]  # Limit length
            
            return "Sri Lanka Adventure"  # Default fallback
            
        except Exception:
            return "Sri Lanka Adventure"  # Fallback
    
    async def _check_edit_access(self, plan_id: str, user_id: str) -> bool:
        """Check if user has edit access to a travel plan"""
        try:
            if not supabase:
                return False
            
            # Check if user owns the plan
            owner_result = supabase.table('user_travel_plans').select('id').eq('id', plan_id).eq('user_id', user_id).execute()
            if owner_result.data:
                return True
            
            # Check if user has shared edit access
            share_result = supabase.table('travel_plan_shares').select('id').eq('travel_plan_id', plan_id).eq('shared_with_user_id', user_id).eq('can_edit', True).execute()
            if share_result.data:
                return True
            
            return False
            
        except Exception:
            return False
    
    async def _update_last_accessed(self, plan_id: str, user_id: str):
        """Update last accessed timestamp and increment view count"""
        try:
            if supabase:
                # Increment view count and update last accessed
                result = supabase.rpc('increment_plan_views', {
                    'plan_id': plan_id
                }).execute()
                
                # If RPC doesn't exist, fall back to direct update
                if not result.data:
                    supabase.table('user_travel_plans').update({
                        'last_accessed': datetime.now().isoformat(),
                        'times_viewed': 'times_viewed + 1'
                    }).eq('id', plan_id).execute()
                    
        except Exception as e:
            logger.error(f"Error updating last accessed for plan {plan_id}: {str(e)}")
    
    async def _log_modification(
        self, 
        plan_id: str, 
        user_id: str, 
        modification_type: str, 
        field_changed: str = None,
        old_value: str = None,
        new_value: str = None,
        description: str = None
    ):
        """Log a modification to the travel plan"""
        try:
            if supabase:
                modification_data = {
                    'travel_plan_id': plan_id,
                    'modified_by_user_id': user_id,
                    'modification_type': modification_type,
                    'field_changed': field_changed,
                    'old_value': old_value,
                    'new_value': new_value,
                    'description': description,
                    'created_at': datetime.now().isoformat()
                }
                
                supabase.table('travel_plan_modifications').insert(modification_data).execute()
                
        except Exception as e:
            logger.error(f"Error logging modification: {str(e)}")


# Singleton instance
_travel_plan_service = None

def get_travel_plan_service() -> TravelPlanService:
    """Get the travel plan service instance"""
    global _travel_plan_service
    if _travel_plan_service is None:
        _travel_plan_service = TravelPlanService()
    return _travel_plan_service
