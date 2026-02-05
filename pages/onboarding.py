"""User onboarding wizard for collecting profile information."""

import json
import streamlit as st
from database.connection import get_session
from database.models import UserProfile
from utils.session_manager import get_user_id, set_page, get_session_value, set_session_value
from utils.validators import validate_age, validate_sleep_hours
from config.constants import HEALTH_GOALS, PROFESSION_CATEGORIES, SLEEP_QUALITY_SCALE
from components.forms import render_progress_bar


TOTAL_STEPS = 4
STEP_LABELS = ["Basic Info", "Sleep", "Goals", "Review"]


def render():
    """Render the onboarding wizard."""
    user_id = get_user_id()
    if not user_id:
        set_page("auth")
        st.rerun()
        return
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h2 style="color: #263238;">Let's Get to Know You</h2>
            <p style="color: #607D8B;">This helps us personalize your experience</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get current step
    current_step = st.session_state.get("onboarding_step", 1)
    
    # Render progress bar
    render_progress_bar(current_step, TOTAL_STEPS, STEP_LABELS)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render current step
    if current_step == 1:
        _render_step_basic_info()
    elif current_step == 2:
        _render_step_sleep()
    elif current_step == 3:
        _render_step_goals()
    elif current_step == 4:
        _render_step_review()


def _render_step_basic_info():
    """Step 1: Basic information."""
    st.markdown("### Tell us about yourself")
    
    onboarding_data = st.session_state.get("onboarding_data", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input(
            "Age",
            min_value=13,
            max_value=120,
            value=onboarding_data.get("age", 25),
            key="onboarding_age",
            help="You must be at least 13 years old"
        )
    
    with col2:
        profession = st.selectbox(
            "Profession",
            options=PROFESSION_CATEGORIES,
            index=PROFESSION_CATEGORIES.index(onboarding_data.get("profession", "Student")) 
                  if onboarding_data.get("profession") in PROFESSION_CATEGORIES else 0,
            key="onboarding_profession"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col3:
        if st.button("Next →", key="step1_next", use_container_width=True):
            valid, msg = validate_age(age)
            if not valid:
                st.error(msg)
            else:
                onboarding_data["age"] = age
                onboarding_data["profession"] = profession
                st.session_state.onboarding_data = onboarding_data
                st.session_state.onboarding_step = 2
                st.rerun()


def _render_step_sleep():
    """Step 2: Sleep habits."""
    st.markdown("### Your Sleep Habits")
    
    onboarding_data = st.session_state.get("onboarding_data", {})
    
    sleep_hours = st.slider(
        "Average hours of sleep per night",
        min_value=3.0,
        max_value=12.0,
        value=float(onboarding_data.get("sleep_hours", 7.0)),
        step=0.5,
        key="onboarding_sleep_hours"
    )
    
    # Visual indicator for sleep quality
    if sleep_hours < 6:
        st.warning("Getting less than 6 hours may affect your mental health")
    elif sleep_hours > 9:
        st.info("Sleeping more than 9 hours may indicate other health factors")
    else:
        st.success("Great! 7-9 hours is recommended for adults")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    sleep_quality = st.select_slider(
        "How would you rate your sleep quality?",
        options=list(SLEEP_QUALITY_SCALE.keys()),
        format_func=lambda x: SLEEP_QUALITY_SCALE[x],
        value=onboarding_data.get("sleep_quality", 3),
        key="onboarding_sleep_quality"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", key="step2_back", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
    
    with col3:
        if st.button("Next →", key="step2_next", use_container_width=True):
            onboarding_data["sleep_hours"] = sleep_hours
            onboarding_data["sleep_quality"] = sleep_quality
            st.session_state.onboarding_data = onboarding_data
            st.session_state.onboarding_step = 3
            st.rerun()


def _render_step_goals():
    """Step 3: Health goals."""
    st.markdown("### What are your wellness goals?")
    st.markdown("*Select all that apply*")
    
    onboarding_data = st.session_state.get("onboarding_data", {})
    existing_goals = onboarding_data.get("health_goals", [])
    
    selected_goals = st.multiselect(
        "Choose your goals",
        options=HEALTH_GOALS,
        default=existing_goals if existing_goals else None,
        key="onboarding_goals",
        help="You can select multiple goals"
    )
    
    if not selected_goals:
        st.info("Please select at least one goal to continue")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", key="step3_back", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    with col3:
        if st.button("Next →", key="step3_next", use_container_width=True, disabled=len(selected_goals) == 0):
            onboarding_data["health_goals"] = selected_goals
            st.session_state.onboarding_data = onboarding_data
            st.session_state.onboarding_step = 4
            st.rerun()


def _render_step_review():
    """Step 4: Review and submit."""
    st.markdown("### Review Your Profile")
    
    onboarding_data = st.session_state.get("onboarding_data", {})
    
    # Display summary
    st.markdown("""
        <div class="glass-card">
            <div class="glass-card-title">Profile Summary</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Age:** {onboarding_data.get('age', 'Not set')}")
        st.markdown(f"**Profession:** {onboarding_data.get('profession', 'Not set')}")
    
    with col2:
        st.markdown(f"**Sleep Hours:** {onboarding_data.get('sleep_hours', 'Not set')} hours/night")
        quality = onboarding_data.get('sleep_quality', 3)
        st.markdown(f"**Sleep Quality:** {SLEEP_QUALITY_SCALE.get(quality, 'Not set')}")
    
    st.markdown("**Health Goals:**")
    goals = onboarding_data.get('health_goals', [])
    if goals:
        for goal in goals:
            st.markdown(f"- {goal}")
    else:
        st.markdown("*No goals selected*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", key="step4_back", use_container_width=True):
            st.session_state.onboarding_step = 3
            st.rerun()
    
    with col3:
        if st.button("Complete Setup ✓", key="step4_submit", use_container_width=True):
            _save_profile(onboarding_data)


def _save_profile(data: dict):
    """Save the user profile to database."""
    user_id = get_user_id()
    
    try:
        with get_session() as session:
            # Check if profile exists
            profile = session.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if profile:
                # Update existing
                profile.age = data.get("age")
                profile.profession = data.get("profession")
                profile.sleep_hours = data.get("sleep_hours")
                profile.sleep_quality = data.get("sleep_quality")
                profile.health_goals = json.dumps(data.get("health_goals", []))
            else:
                # Create new
                profile = UserProfile(
                    user_id=user_id,
                    age=data.get("age"),
                    profession=data.get("profession"),
                    sleep_hours=data.get("sleep_hours"),
                    sleep_quality=data.get("sleep_quality"),
                    health_goals=json.dumps(data.get("health_goals", []))
                )
                session.add(profile)
        
        st.success("Profile saved successfully!")
        # Clear onboarding data and move to clinical assessment
        st.session_state.onboarding_step = 1
        st.session_state.onboarding_data = {}
        set_page("clinical")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")
