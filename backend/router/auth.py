"""
Authentication Router for User Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from models.auth_models import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user"""
    token_data = auth_service.verify_token(credentials.credentials)
    user = await auth_service.get_user_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login(user_credentials: UserLogin):
    """User login"""
    return await auth_service.login(user_credentials)

@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile"""
    profile = await auth_service.get_user_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    return profile

@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update current user profile"""
    updated_user = await auth_service.update_user_profile(current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    return updated_user

@router.put("/me/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update user password"""
    success = await auth_service.update_password(current_user.id, password_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update password"
        )
    return {"message": "Password updated successfully"}

@router.post("/me/saved-destinations/{destination_id}")
async def save_destination(
    destination_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Save a destination to favorites"""
    success = await auth_service.save_destination(current_user.id, destination_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save destination"
        )
    return {"message": "Destination saved successfully"}

@router.delete("/me/saved-destinations/{destination_id}")
async def unsave_destination(
    destination_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Remove a destination from favorites"""
    success = await auth_service.unsave_destination(current_user.id, destination_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to unsave destination"
        )
    return {"message": "Destination removed from favorites"}

@router.get("/me/saved-destinations")
async def get_saved_destinations(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get user's saved destinations"""
    destinations = await auth_service.get_saved_destinations(current_user.id)
    return {"saved_destinations": destinations}

@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """Refresh access token"""
    from datetime import timedelta
    
    access_token = auth_service.create_access_token(
        data={
            "sub": current_user.email,
            "user_id": current_user.id,
            "role": current_user.role.value
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """User logout (client should remove token)"""
    return {"message": "Logged out successfully"}

# Password reset endpoints (implement email service first)
@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset"""
    # Implement password reset email sending
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password with token"""
    # Implement password reset with token verification
    return {"message": "Password reset successfully"}

# Email verification endpoints
@router.post("/verify-email")
async def verify_email(verification: EmailVerification):
    """Verify email with token"""
    # Implement email verification
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(request: EmailVerificationRequest):
    """Resend email verification"""
    # Implement resend verification email
    return {"message": "Verification email sent"}
