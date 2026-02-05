"""Session state management utilities for Streamlit."""

import streamlit as st
from typing import Any, Optional


def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "user_id": None,
        "username": None,
        "page": "auth",
        "onboarding_step": 1,
        "onboarding_data": {},
        "assessment_data": {},
        "show_assessment_results": False,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.get("user_id") is not None


def get_user_id() -> Optional[int]:
    """Get the current user's ID."""
    return st.session_state.get("user_id")


def get_username() -> Optional[str]:
    """Get the current user's username."""
    return st.session_state.get("username")


def set_user(user_id: int, username: str):
    """Set the authenticated user."""
    st.session_state.user_id = user_id
    st.session_state.username = username


def logout():
    """Clear user session and redirect to auth."""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.page = "auth"
    st.session_state.onboarding_step = 1
    st.session_state.onboarding_data = {}
    st.session_state.assessment_data = {}
    st.session_state.show_assessment_results = False


def set_page(page_name: str):
    """Navigate to a different page."""
    st.session_state.page = page_name


def get_current_page() -> str:
    """Get the current page name."""
    return st.session_state.get("page", "auth")


def set_session_value(key: str, value: Any):
    """Set a custom session state value."""
    st.session_state[key] = value


def get_session_value(key: str, default: Any = None) -> Any:
    """Get a session state value with optional default."""
    return st.session_state.get(key, default)


def clear_onboarding_data():
    """Clear onboarding form data."""
    st.session_state.onboarding_step = 1
    st.session_state.onboarding_data = {}


def clear_assessment_data():
    """Clear assessment form data."""
    st.session_state.assessment_data = {}
    st.session_state.show_assessment_results = False
