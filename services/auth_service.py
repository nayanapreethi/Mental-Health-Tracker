"""Authentication service for user management."""

import bcrypt
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from database.models import User, UserProfile, HealthBaseline
from database.connection import get_session


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def create_user(username: str, email: str, password: str) -> Tuple[bool, str, Optional[int]]:
    """
    Create a new user account.
    
    Returns:
        Tuple of (success: bool, message: str, user_id: Optional[int])
    """
    with get_session() as session:
        # Check if username already exists
        existing_user = session.query(User).filter(
            User.username == username
        ).first()
        if existing_user:
            return False, "Username already exists", None
        
        # Check if email already exists
        existing_email = session.query(User).filter(
            User.email == email
        ).first()
        if existing_email:
            return False, "Email already registered", None
        
        # Create new user
        hashed_pw = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_pw
        )
        session.add(new_user)
        session.flush()  # Get the ID before commit
        
        user_id = new_user.id
        return True, "Account created successfully", user_id


def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[int]]:
    """
    Authenticate a user by username and password.
    
    Returns:
        Tuple of (success: bool, message: str, user_id: Optional[int])
    """
    with get_session() as session:
        user = session.query(User).filter(
            User.username == username
        ).first()
        
        if not user:
            return False, "Invalid username or password", None
        
        if not verify_password(password, user.hashed_password):
            return False, "Invalid username or password", None
        
        return True, "Login successful", user.id


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user information by ID."""
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
        }


def has_completed_onboarding(user_id: int) -> bool:
    """Check if user has completed the onboarding profile."""
    with get_session() as session:
        profile = session.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        return profile is not None and profile.age is not None


def has_completed_assessment(user_id: int) -> bool:
    """Check if user has completed the clinical assessment."""
    with get_session() as session:
        baseline = session.query(HealthBaseline).filter(
            HealthBaseline.user_id == user_id
        ).first()
        return baseline is not None and baseline.phq9_score is not None


def delete_user_account(user_id: int) -> bool:
    """Delete a user account and all associated data."""
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            return True
        return False
