"""Authentication endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, constr

from app.core.logging_config import logger
from app.services.supabase import get_supabase_service
from app.api.v1.dependencies import get_current_user

router = APIRouter()


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(gt=0, description="Token expiration time in seconds")
    refresh_token: Optional[str] = None


class RefreshToken(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., min_length=1, description="Valid refresh token")


class UserCreate(BaseModel):
    """User registration model."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password must be between 8 and 72 characters and contain at least one letter and one number",
        pattern="^[A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*$|^[A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*$",
    )
    password_confirm: str = Field(..., description="Must match password field")
    username: Optional[constr(min_length=3, max_length=50)] = Field(
        None, description="Username between 3 and 50 characters"
    )


class ProfileCreate(BaseModel):
    """Profile creation model."""

    username: constr(min_length=3, max_length=50) = Field(
        ..., description="Username between 3 and 50 characters"
    )


class PasswordReset(BaseModel):
    """Password reset model."""

    token: str = Field(..., min_length=1, description="Valid reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password must be between 8 and 72 characters and contain at least one letter and one number",
        pattern="^[A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*$|^[A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*$",
    )
    new_password_confirm: str = Field(..., description="Must match new_password field")


class EmailRequest(BaseModel):
    """Email request model."""

    email: EmailStr


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    try:
        supabase = get_supabase_service()
        result = await supabase.create_user_with_profile(
            email=user_data.email, password=user_data.password, username=user_data.username
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed"
            )

        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": result["user_id"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token."""
    try:
        supabase = get_supabase_service()
        try:
            result = await supabase.authenticate_user(
                email=form_data.username, password=form_data.password
            )

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return {
                "access_token": result["access_token"],
                "token_type": "bearer",
                "expires_in": 3600,  # 1 hour
                "refresh_token": result["refresh_token"],
            }
        except Exception as auth_error:
            logger.error(f"Login error: {auth_error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.post("/logout")
async def logout(response: Response):
    """Logout current user."""
    try:
        supabase = get_supabase_service()
        await supabase.client.auth.sign_out()
        response.delete_cookie("session")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during logout"
        )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(token_data: RefreshToken):
    """Refresh access token using refresh token."""
    try:
        supabase = get_supabase_service()
        response = await supabase.client.auth.refresh_session(token_data.refresh_token)

        if not response or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour
            "refresh_token": response.session.refresh_token,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/password-reset/request")
async def request_password_reset(email_data: EmailRequest):
    """Request password reset email."""
    try:
        supabase = get_supabase_service()
        await supabase.client.auth.reset_password_email(email_data.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link will be sent"}


@router.post("/password-reset/verify")
async def reset_password(reset_data: PasswordReset):
    """Reset password using reset token."""
    if reset_data.new_password != reset_data.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    try:
        supabase = get_supabase_service()
        # Verify token
        response = await supabase.client.auth.verify_otp(reset_data.token, type_="recovery")

        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
            )

        # Update password
        await supabase.client.auth.update_user({"password": reset_data.new_password})
        return {"message": "Password successfully reset"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password"
        )


@router.get("/verify-email")
async def verify_email(token: str):
    """Verify email address."""
    try:
        supabase = get_supabase_service()
        response = await supabase.client.auth.verify_otp(token, type_="email")
        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token"
            )
        return {"message": "Email successfully verified"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token"
        )


@router.post("/create-profile", status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate, current_user: dict = Depends(get_current_user)
):
    """Create a profile for the authenticated user."""
    try:
        supabase = get_supabase_service()

        # Create profile for the authenticated user
        profile = await supabase.create_profile_for_existing_user(
            user_id=current_user["id"], username=profile_data.username
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create profile"
            )

        return {"message": "Profile created successfully", "profile": profile}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during profile creation",
        )
