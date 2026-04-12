# Authentication service
from sqlalchemy.orm import Session
from app.models.db import User
from app.core.security import hash_password, verify_password, create_access_token
from app.models.schemas import SignupRequest, LoginRequest, TokenResponse
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Handles user authentication"""

    @staticmethod
    def signup(db: Session, user_data: SignupRequest) -> TokenResponse:
        """Register a new user"""
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User registered: {user_data.email}")

        # Generate token
        access_token = create_access_token(new_user.id, new_user.email)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=new_user.id,
            email=new_user.email
        )

    @staticmethod
    def login(db: Session, credentials: LoginRequest) -> TokenResponse:
        """Authenticate user and return token"""
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        logger.info(f"User logged in: {credentials.email}")

        # Generate token
        access_token = create_access_token(user.id, user.email)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email
        )

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Fetch user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user
