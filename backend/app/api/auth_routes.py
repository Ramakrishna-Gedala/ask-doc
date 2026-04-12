# Authentication routes
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.core.security import verify_token, TokenData
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(authorization: Optional[str] = Header(None)) -> TokenData:
    """Dependency to get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")
    user_data = verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user_data


@router.post("/signup", response_model=TokenResponse)
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **email**: User email (must be unique)
    - **full_name**: User's full name
    - **password**: User password (will be hashed)

    Returns: JWT access token
    """
    try:
        token_response = AuthService.signup(db, user_data)
        return token_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user and get JWT token.

    - **email**: User email
    - **password**: User password

    Returns: JWT access token
    """
    try:
        token_response = AuthService.login(db, credentials)
        return token_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user = AuthService.get_user(db, current_user.user_id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
