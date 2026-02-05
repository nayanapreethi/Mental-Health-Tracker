"""MindfulMe - Mental Health Tracker Main Application."""

import streamlit as st
from utils.session_manager import get_current_page, initialize_session
from pages.auth import render as render_auth
from pages.onboarding import render as render_onboarding
from pages.clinical_assessment import render as render_clinical
from pages.dashboard import render as render_dashboard

# Inject custom CSS
with open('static/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configure page
st.set_page_config(
    page_title="MindfulMe - Mental Wellness Tracker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session()

    # Get current page from session
    current_page = get_current_page()

    # Render sidebar navigation if user is logged in
    if st.session_state.get('user_id'):
        render_sidebar()

    # Route to appropriate page
    if current_page == "auth":
        render_auth()
    elif current_page == "onboarding":
        render_onboarding()
    elif current_page == "clinical":
        render_clinical()
    elif current_page == "dashboard":
        render_dashboard()
    else:
        # Default to auth page
        render_auth()

def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("## 🧠 MindfulMe")

        # User info
        username = st.session_state.get('username', 'User')
        st.markdown(f"**Welcome, {username}!**")

        # Navigation menu
        st.markdown("---")

        pages = {
            "Dashboard": "dashboard",
            "Clinical Assessment": "clinical",
            "Settings": "settings"
        }

        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("Logout", key="logout", use_container_width=True):
            from utils.session_manager import logout_user
            logout_user()
            st.rerun()

if __name__ == "__main__":
    main()
