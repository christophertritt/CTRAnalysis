"""
Authentication module for Bellevue CTR Dashboard
Simple password-based authentication using Streamlit session state
"""

import streamlit as st
import hashlib


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


# Default credentials (change these!)
# Password is hashed for security
DEFAULT_USERS = {
    "admin": hash_password("bellevue2026"),  # Change this password!
    "viewer": hash_password("ctr2026"),       # Change this password!
}


def check_password():
    """
    Returns True if the user has entered a correct password.
    Displays login form if not authenticated.
    """
    
    # Check if already authenticated
    if st.session_state.get("authenticated", False):
        return True
    
    # Show login form
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🚌 Bellevue CTR Dashboard</h1>
            <p style='color: #666; font-size: 1.1rem;'>
                Please log in to access the dashboard
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", key="username")
            password = st.text_input("Password", type="password", key="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Check credentials
                if username in DEFAULT_USERS:
                    if DEFAULT_USERS[username] == hash_password(password):
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username
                        st.success("✓ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("❌ Invalid username or password")
        
        # Show default credentials hint (remove in production!)
        with st.expander("ℹ️ Default Credentials (Development Only)"):
            st.info(
                """
                **Admin Account:**
                - Username: `admin`
                - Password: `bellevue2026`
                
                **Viewer Account:**
                - Username: `viewer`
                - Password: `ctr2026`
                
                ⚠️ **Important:** Change these in `auth.py` before deployment!
                """
            )
    
    return False


def logout():
    """Clear authentication session."""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()


def show_logout_button():
    """Display logout button in sidebar."""
    if st.session_state.get("authenticated", False):
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            f"👤 Logged in as: **{st.session_state.get('username', 'Unknown')}**"
        )
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()


def get_current_user():
    """Get the currently authenticated username."""
    return st.session_state.get("username", None)
