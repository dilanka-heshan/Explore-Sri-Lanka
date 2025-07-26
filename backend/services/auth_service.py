"""
Authentication Service for User Management
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging

from models.auth_models import *
from models.database import get_supabase_client

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class AuthService:
    def __init__(self):
        self.db = get_supabase_client()
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token_data = TokenData(
                email=email, 
                user_id=user_id, 
                role=UserRole(role) if role else UserRole.USER
            )
            return token_data
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db.table("user_profiles").select("*").eq("email", user_data.email).execute()
            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user record with only essential fields for now
            user_record = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "password_hash": hashed_password,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add optional fields only if they have values
            if user_data.avatar_url:
                user_record["avatar_url"] = user_data.avatar_url
            if user_data.phone:
                user_record["phone"] = user_data.phone
            if user_data.date_of_birth:
                user_record["date_of_birth"] = user_data.date_of_birth.isoformat()
            if user_data.nationality:
                user_record["nationality"] = user_data.nationality
            if user_data.location:
                user_record["location"] = user_data.location
            if user_data.bio:
                user_record["bio"] = user_data.bio
            
            # Try to add role-related fields, but handle gracefully if columns don't exist
            try:
                user_record.update({
                    "role": UserRole.USER.value,
                    "email_verified": False,
                    "is_active": True
                })
            except:
                # If these columns don't exist yet, continue without them
                pass
            
            result = self.db.table("user_profiles").insert(user_record).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            user = result.data[0]
            
            # Create response with safe defaults for missing fields
            user_response_data = {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "avatar_url": user.get("avatar_url"),
                "phone": user.get("phone"),
                "date_of_birth": user.get("date_of_birth"),
                "nationality": user.get("nationality"),
                "location": user.get("location"),
                "bio": user.get("bio"),
                "role": user.get("role", "user"),
                "email_verified": user.get("email_verified", False),
                "is_active": user.get("is_active", True),
                "created_at": user["created_at"],
                "updated_at": user.get("updated_at"),
                "last_login": user.get("last_login")
            }
            
            # Send verification email (implement this separately)
            try:
                await self.send_verification_email(user["email"], user["id"])
            except:
                # Continue if email sending fails
                pass
            
            return UserResponse(**user_response_data)
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Authenticate user login"""
        try:
            # Get user by email
            result = self.db.table("user_profiles").select("*").eq("email", email).execute()
            
            if not result.data:
                return None
            
            user = result.data[0]
            
            # Verify password
            if not self.verify_password(password, user.get("password_hash", "")):
                return None
            
            # Update last login
            self.db.table("user_profiles").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user["id"]).execute()
            
            return UserResponse(**user)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def login(self, user_credentials: UserLogin) -> AuthResponse:
        """User login"""
        user = await self.authenticate_user(user_credentials.email, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "role": user.role.value
            },
            expires_delta=access_token_expires
        )
        
        token = Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(user=user, token=token)
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            result = self.db.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if not result.data:
                return None
            
            return UserResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfileResponse]:
        """Get detailed user profile"""
        try:
            # Get user data
            user_result = self.db.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                return None
            
            user = user_result.data[0]
            
            # Get additional stats
            reviews_count = self.db.table("reviews").select("id", count="exact").eq("user_id", user_id).execute()
            bookings_count = self.db.table("bookings").select("id", count="exact").eq("user_id", user_id).execute()
            
            # Get favorite destinations (saved destinations)
            favorites = self.db.table("user_saved_destinations").select("destination_id").eq("user_id", user_id).execute()
            favorite_destinations = [fav["destination_id"] for fav in (favorites.data or [])]
            
            profile_data = {
                **user,
                "total_reviews": reviews_count.count or 0,
                "total_bookings": bookings_count.count or 0,
                "favorite_destinations": favorite_destinations
            }
            
            return UserProfileResponse(**profile_data)
            
        except Exception as e:
            logger.error(f"Get user profile failed: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> Optional[UserResponse]:
        """Update user profile"""
        try:
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow().isoformat()
            
            if update_data.date_of_birth:
                update_dict["date_of_birth"] = update_data.date_of_birth.isoformat()
            
            result = self.db.table("user_profiles").update(update_dict).eq("id", user_id).execute()
            
            if not result.data:
                return None
            
            return UserResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Update user profile failed: {e}")
            return None
    
    async def update_password(self, user_id: str, password_data: PasswordUpdate) -> bool:
        """Update user password"""
        try:
            # Get current user
            user_result = self.db.table("user_profiles").select("password_hash").eq("id", user_id).execute()
            
            if not user_result.data:
                return False
            
            user = user_result.data[0]
            
            # Verify current password
            if not self.verify_password(password_data.current_password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_password_hash = self.get_password_hash(password_data.new_password)
            
            # Update password
            result = self.db.table("user_profiles").update({
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(result.data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update password failed: {e}")
            return False
    
    async def send_verification_email(self, email: str, user_id: str):
        """Send email verification"""
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Store token in database (you'll need to create a verification_tokens table)
        # For now, we'll just log it
        logger.info(f"Verification token for {email}: {verification_token}")
        
        # In production, implement actual email sending
        pass
    
    async def save_destination(self, user_id: str, destination_id: str) -> bool:
        """Save destination to user favorites"""
        try:
            # Check if already saved
            existing = self.db.table("user_saved_destinations").select("*").eq("user_id", user_id).eq("destination_id", destination_id).execute()
            
            if existing.data:
                return True  # Already saved
            
            # Save destination
            result = self.db.table("user_saved_destinations").insert({
                "user_id": user_id,
                "destination_id": destination_id,
                "saved_at": datetime.utcnow().isoformat()
            }).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Save destination failed: {e}")
            return False
    
    async def unsave_destination(self, user_id: str, destination_id: str) -> bool:
        """Remove destination from user favorites"""
        try:
            result = self.db.table("user_saved_destinations").delete().eq("user_id", user_id).eq("destination_id", destination_id).execute()
            return True
        except Exception as e:
            logger.error(f"Unsave destination failed: {e}")
            return False
    
    async def get_saved_destinations(self, user_id: str) -> List[str]:
        """Get user's saved destinations"""
        try:
            result = self.db.table("user_saved_destinations").select("destination_id").eq("user_id", user_id).execute()
            return [item["destination_id"] for item in (result.data or [])]
        except Exception as e:
            logger.error(f"Get saved destinations failed: {e}")
            return []
