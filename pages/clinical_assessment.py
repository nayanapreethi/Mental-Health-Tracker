"""Clinical assessment page for PHQ-9 and GAD-7 questionnaires."""

import streamlit as st
from datetime import date
from database.connection import get_session
from database.models import HealthBaseline
from utils.session_manager import get_user_id, set_page
from config.constants import (
    PHQ9_QUESTIONS, PHQ9_OPTIONS, PHQ9_SEVERITY,
    GAD7_QUESTIONS, GAD7_OPTIONS, GAD7_SEVERITY,
    COLORS
)
from components.charts import render_donut_chart
from components.cards import render_recommendation_card


def render():
    """Render the clinical assessment page."""
    user_id = get_user_id()
    if not user_id:
        set_page("auth")
        st.rerun()
        return
    
    # Check if showing results
    if st.session_state.get("show_assessment_results", False):
        _render_results()
        return
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h2 style="color: #263238;">Mental Health Assessment</h2>
            <p style="color: #607D8B;">Please answer honestly based on the past 2 weeks</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Assessment tabs
    tab1, tab2 = st.tabs(["Depression Screening (PHQ-9)", "Anxiety Screening (GAD-7)"])
    
    with tab1:
        _render_phq9()
    
    with tab2:
        _render_gad7()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Assessment", key="submit_assessment", use_container_width=True):
            _process_assessment()


def _render_phq9():
    """Render PHQ-9 questionnaire."""
    st.markdown("### Over the last 2 weeks, how often have you been bothered by:")
    
    assessment_data = st.session_state.get("assessment_data", {})
    phq9_responses = assessment_data.get("phq9", {})
    
    for i, question in enumerate(PHQ9_QUESTIONS, 1):
        st.markdown(f"**{i}. {question}**")
        
        key = f"phq9_q{i}"
        options = list(PHQ9_OPTIONS.values())
        
        # Get previous selection
        prev_value = phq9_responses.get(key)
        default_index = 0
        if prev_value is not None:
            default_index = list(PHQ9_OPTIONS.keys()).index(prev_value)
        
        selected = st.radio(
            f"Question {i}",
            options=options,
            index=default_index,
            key=key,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Store the value
        selected_value = list(PHQ9_OPTIONS.keys())[options.index(selected)]
        phq9_responses[key] = selected_value
        
        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    # Update session state
    assessment_data["phq9"] = phq9_responses
    st.session_state.assessment_data = assessment_data


def _render_gad7():
    """Render GAD-7 questionnaire."""
    st.markdown("### Over the last 2 weeks, how often have you been bothered by:")
    
    assessment_data = st.session_state.get("assessment_data", {})
    gad7_responses = assessment_data.get("gad7", {})
    
    for i, question in enumerate(GAD7_QUESTIONS, 1):
        st.markdown(f"**{i}. {question}**")
        
        key = f"gad7_q{i}"
        options = list(GAD7_OPTIONS.values())
        
        # Get previous selection
        prev_value = gad7_responses.get(key)
        default_index = 0
        if prev_value is not None:
            default_index = list(GAD7_OPTIONS.keys()).index(prev_value)
        
        selected = st.radio(
            f"Question {i}",
            options=options,
            index=default_index,
            key=key,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Store the value
        selected_value = list(GAD7_OPTIONS.keys())[options.index(selected)]
        gad7_responses[key] = selected_value
        
        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    # Update session state
    assessment_data["gad7"] = gad7_responses
    st.session_state.assessment_data = assessment_data


def _process_assessment():
    """Process and save the assessment results."""
    user_id = get_user_id()
    assessment_data = st.session_state.get("assessment_data", {})
    
    # Calculate PHQ-9 score
    phq9_responses = assessment_data.get("phq9", {})
    phq9_score = sum(phq9_responses.values()) if phq9_responses else 0
    phq9_severity = _get_severity_level(phq9_score, PHQ9_SEVERITY)
    
    # Calculate GAD-7 score
    gad7_responses = assessment_data.get("gad7", {})
    gad7_score = sum(gad7_responses.values()) if gad7_responses else 0
    gad7_severity = _get_severity_level(gad7_score, GAD7_SEVERITY)
    
    # Store results in session for display
    st.session_state.assessment_results = {
        "phq9_score": phq9_score,
        "phq9_severity": phq9_severity,
        "gad7_score": gad7_score,
        "gad7_severity": gad7_severity,
    }
    
    # Save to database
    try:
        with get_session() as session:
            baseline = session.query(HealthBaseline).filter(
                HealthBaseline.user_id == user_id
            ).first()
            
            if baseline:
                baseline.phq9_score = phq9_score
                baseline.phq9_severity = phq9_severity["level"]
                baseline.gad7_score = gad7_score
                baseline.gad7_severity = gad7_severity["level"]
                baseline.last_test_date = date.today()
            else:
                baseline = HealthBaseline(
                    user_id=user_id,
                    phq9_score=phq9_score,
                    phq9_severity=phq9_severity["level"],
                    gad7_score=gad7_score,
                    gad7_severity=gad7_severity["level"],
                    last_test_date=date.today()
                )
                session.add(baseline)
        
        st.session_state.show_assessment_results = True
        st.rerun()
        
    except Exception as e:
        st.error(f"Error saving assessment: {str(e)}")


def _get_severity_level(score: int, severity_dict: dict) -> dict:
    """Get severity level info based on score."""
    for (min_score, max_score), info in severity_dict.items():
        if min_score <= score <= max_score:
            return info
    return list(severity_dict.values())[-1]  # Return highest severity if not found


def _render_results():
    """Render assessment results page."""
    results = st.session_state.get("assessment_results", {})
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #263238;">Your Assessment Results</h2>
            <p style="color: #607D8B;">Based on your responses from the past 2 weeks</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display scores in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Depression (PHQ-9)")
        phq9_score = results.get("phq9_score", 0)
        phq9_severity = results.get("phq9_severity", {})
        
        render_donut_chart(
            score=phq9_score,
            max_score=27,
            title="PHQ-9 Score",
            color=phq9_severity.get("color", COLORS["dark_teal"]),
            show_percentage=False
        )
        
        st.markdown(f"""
            <div style="text-align: center;">
                <span class="severity-badge" style="background: {phq9_severity.get('color', COLORS['dark_teal'])}20; 
                       color: {phq9_severity.get('color', COLORS['dark_teal'])};">
                    {phq9_severity.get('level', 'Unknown')}
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Anxiety (GAD-7)")
        gad7_score = results.get("gad7_score", 0)
        gad7_severity = results.get("gad7_severity", {})
        
        render_donut_chart(
            score=gad7_score,
            max_score=21,
            title="GAD-7 Score",
            color=gad7_severity.get("color", COLORS["dark_teal"]),
            show_percentage=False
        )
        
        st.markdown(f"""
            <div style="text-align: center;">
                <span class="severity-badge" style="background: {gad7_severity.get('color', COLORS['dark_teal'])}20; 
                       color: {gad7_severity.get('color', COLORS['dark_teal'])};">
                    {gad7_severity.get('level', 'Unknown')}
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_recommendation_card(
            "For Depression",
            phq9_severity.get("recommendation", "Continue monitoring your mood.")
        )
    
    with col2:
        render_recommendation_card(
            "For Anxiety",
            gad7_severity.get("recommendation", "Practice relaxation techniques.")
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Disclaimer
    st.info("""
        **Important:** This assessment is a screening tool, not a diagnosis. 
        If you're experiencing distress, please consult a mental health professional.
        If you're having thoughts of self-harm, please contact emergency services or a crisis helpline.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Continue button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Continue to Dashboard →", key="continue_dashboard", use_container_width=True):
            st.session_state.show_assessment_results = False
            st.session_state.assessment_data = {}
            set_page("dashboard")
            st.rerun()
