"""Authentication page with login and signup functionality."""

import streamlit as st
from services.auth_service import create_user, authenticate_user
from utils.session_manager import set_user, set_page
from utils.validators import validate_email, validate_password_strength, validate_username


def render():
    """Render the authentication page."""
    
    # Center the content
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # App branding
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div class="brand-logo">MindfulMe</div>
            <p style="color: #00897B; font-size: 1.1rem;">Your Mental Wellness Companion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create centered columns for the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tabs for Login and Signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            _render_login_form()
        
        with tab2:
            _render_signup_form()


def _render_login_form():
    """Render the login form."""
    st.markdown("### Welcome Back")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                success, message, user_id = authenticate_user(username, password)
                
                if success:
                    set_user(user_id, username)
                    st.success(message)
                    # Check if user needs to complete onboarding
                    from services.auth_service import has_completed_onboarding, has_completed_assessment
                    
                    if not has_completed_onboarding(user_id):
                        set_page("onboarding")
                    elif not has_completed_assessment(user_id):
                        set_page("clinical")
                    else:
                        set_page("dashboard")
                    st.rerun()
                else:
                    st.error(message)


def _render_signup_form():
    """Render the signup form."""
    st.markdown("### Create Account")
    
    with st.form("signup_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username",
            help="3-30 characters, letters, numbers, and underscores"
        )
        
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            key="signup_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="signup_password",
            help="At least 8 characters with uppercase, lowercase, and number"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm your password",
            key="signup_confirm_password"
        )
        
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            key="agree_terms"
        )
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            
            if not username or not email or not password or not confirm_password:
                errors.append("Please fill in all fields")
            else:
                # Validate username
                username_valid, username_msg = validate_username(username)
                if not username_valid:
                    errors.append(username_msg)
                
                # Validate email
                if not validate_email(email):
                    errors.append("Please enter a valid email address")
                
                # Validate password
                password_valid, password_msg = validate_password_strength(password)
                if not password_valid:
                    errors.append(password_msg)
                
                # Check password match
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                # Check terms agreement
                if not agree_terms:
                    errors.append("Please agree to the Terms of Service")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create the user
                success, message, user_id = create_user(username, email, password)
                
                if success:
                    st.success("Account created successfully! Redirecting...")
                    set_user(user_id, username)
                    set_page("onboarding")
                    st.rerun()
                else:
                    st.error(message)
    
    # Additional info
    st.markdown("""
        <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #607D8B;">
            Your data is encrypted and stored securely.<br>
            We never share your personal information.
        </div>
    """, unsafe_allow_html=True)
