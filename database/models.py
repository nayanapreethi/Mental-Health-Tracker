"""SQLAlchemy ORM models for MindfulMe."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime, 
    ForeignKey, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    health_baseline: Mapped[Optional["HealthBaseline"]] = relationship(
        "HealthBaseline", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    daily_logs: Mapped[List["DailyLog"]] = relationship(
        "DailyLog", back_populates="user", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserProfile(Base):
    """User profile with onboarding data."""
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 scale
    health_goals: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string list
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, profession='{self.profession}')>"


class HealthBaseline(Base):
    """Clinical assessment baseline scores."""
    __tablename__ = "health_baseline"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phq9_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phq9_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gad7_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gad7_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_test_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="health_baseline")
    
    def __repr__(self):
        return f"<HealthBaseline(user_id={self.user_id}, phq9={self.phq9_score}, gad7={self.gad7_score})>"


class DailyLog(Base):
    """Daily mood and health log entries."""
    __tablename__ = "daily_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "log_date", name="unique_user_date"),
        Index("idx_user_date", "user_id", "log_date"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mood_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10 scale
    journal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ai_sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_emotion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cognitive_distortions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string list
    vocal_tension: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100 scale
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="daily_logs")
    
    def __repr__(self):
        return f"<DailyLog(user_id={self.user_id}, date={self.log_date}, mood={self.mood_score})>"
