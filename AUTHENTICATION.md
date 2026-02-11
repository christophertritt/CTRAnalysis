# Authentication Setup Guide

## Overview

The Bellevue CTR Dashboard includes a simple password-based authentication system built with native Streamlit features and Python's hashlib library. No additional dependencies required.

## How It Works

### Architecture
- **auth.py** - Authentication module with login logic
- **Session State** - Stores authentication status across page reruns
- **Password Hashing** - SHA-256 hashing for secure password storage
- **Login Form** - Centered, user-friendly login interface

### Security Features
- ✅ Passwords stored as SHA-256 hashes (not plaintext)
- ✅ Session-based authentication
- ✅ Logout functionality
- ✅ No external dependencies
- ✅ Simple to configure

## Quick Configuration

### 1. Change Default Passwords (Required!)

**Edit auth.py:**

```python
DEFAULT_USERS = {
    "admin": hash_password("your_secure_password_here"),
    "viewer": hash_password("another_secure_password"),
}
```

### 2. Add More Users

```python
DEFAULT_USERS = {
    "admin": hash_password("admin_password"),
    "john_doe": hash_password("johns_password"),
    "jane_smith": hash_password("janes_password"),
    "analyst1": hash_password("analyst_password"),
}
```

### 3. Remove Development Hints

In **auth.py**, delete or comment out the expander showing default credentials:

```python
# with st.expander("ℹ️ Default Credentials (Development Only)"):
#     st.info(...)
```

## Password Management

### Generating Password Hashes

To generate a hash for a new password:

```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Example:
print(hash_password("my_new_password"))
# Output: a5f8c3b2... (64-character hash)
```

Or use Python directly in your terminal:

```bash
python3 -c "import hashlib; print(hashlib.sha256('my_new_password'.encode()).hexdigest())"
```

### Password Best Practices

✅ **DO:**
- Use strong passwords (12+ characters, mix of letters/numbers/symbols)
- Change default passwords immediately
- Use different passwords for different users
- Store production passwords securely (use secrets management)

❌ **DON'T:**
- Use common passwords (password123, admin, etc.)
- Share passwords across multiple users
- Commit production passwords to git
- Leave default credentials in production

## Using Streamlit Secrets (Recommended for Production)

### Step 1: Create `.streamlit/secrets.toml`

```toml
[passwords]
admin = "your_hashed_password_here"
analyst = "another_hashed_password_here"
viewer = "viewer_hashed_password_here"
```

### Step 2: Update auth.py

```python
import streamlit as st

# Load from secrets instead of hardcoding
DEFAULT_USERS = st.secrets.get("passwords", {
    "admin": hash_password("fallback_password")
})
```

### Step 3: Add to .gitignore

Ensure `.streamlit/secrets.toml` is in your `.gitignore` (already configured).

## Deployment Considerations

### Streamlit Community Cloud

1. Push your code to GitHub (without production credentials)
2. In Streamlit Cloud dashboard, go to app settings
3. Add secrets in the "Secrets" section:
   ```toml
   [passwords]
   admin = "production_hash_here"
   viewer = "production_hash_here"
   ```

### Self-Hosted / Enterprise

For production deployments with many users:

#### Option 1: Environment Variables
```python
import os

DEFAULT_USERS = {
    "admin": os.getenv("ADMIN_PASSWORD_HASH"),
    "viewer": os.getenv("VIEWER_PASSWORD_HASH"),
}
```

#### Option 2: External User Database
```python
import sqlite3

def check_user(username, password):
    # Query database for user
    # Verify password hash
    pass
```

#### Option 3: OAuth Integration
Consider using:
- **streamlit-authenticator** library
- **Authlib** for OAuth/OIDC
- **LDAP** integration for Active Directory

## Advanced Authentication

### Installing streamlit-authenticator

For a more robust solution:

```bash
pip install streamlit-authenticator
```

**Example config:**

```python
import streamlit_authenticator as stauth

names = ['John Doe', 'Jane Smith']
usernames = ['jdoe', 'jsmith']
passwords = ['password1', 'password2']

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    'ctr_dashboard',
    'auth_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')
```

### Role-Based Access Control (RBAC)

Extend **auth.py** to support roles:

```python
USER_ROLES = {
    "admin": {"role": "admin", "hash": hash_password("admin_pass")},
    "analyst": {"role": "analyst", "hash": hash_password("analyst_pass")},
    "viewer": {"role": "viewer", "hash": hash_password("viewer_pass")},
}

def get_user_role(username):
    return USER_ROLES.get(username, {}).get("role", "viewer")

# In your dashboard:
user_role = get_user_role(auth.get_current_user())

if user_role == "admin":
    # Show admin-only features
    pass
elif user_role == "analyst":
    # Show analyst features
    pass
```

## Troubleshooting

### Issue: "Invalid username or password" with correct credentials

**Solution:** Ensure password hash is generated correctly
```python
# In auth.py, add temporary debug:
st.write(f"Stored hash: {DEFAULT_USERS.get(username)}")
st.write(f"Entered hash: {hash_password(password)}")
# These should match
```

### Issue: Logged out on every page refresh

**Solution:** Check session state configuration
```python
# Ensure session state persists
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
```

### Issue: Can't logout

**Solution:** Clear browser cache or use:
```python
# Force logout
st.session_state.clear()
st.rerun()
```

## Testing Authentication

### Manual Testing Checklist

- [ ] Login with valid credentials works
- [ ] Login with invalid credentials shows error
- [ ] Authenticated user can access dashboard
- [ ] Logout button appears for authenticated users
- [ ] Logout clears session and redirects to login
- [ ] Session persists across page interactions
- [ ] Multiple users can login with different credentials

### Automated Testing (Optional)

```python
# test_auth.py
from auth import hash_password, DEFAULT_USERS

def test_password_hashing():
    password = "test123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 == hash2  # Same password = same hash
    assert len(hash1) == 64  # SHA-256 produces 64-char hex

def test_user_exists():
    assert "admin" in DEFAULT_USERS
    assert len(DEFAULT_USERS) > 0
```

## Security Notes

⚠️ **Current Implementation Limitations:**

1. **Basic Security:** SHA-256 hashing without salt (sufficient for low-risk internal dashboards)
2. **No Rate Limiting:** Susceptible to brute force attacks
3. **No Password Reset:** Users must contact admin to change passwords
4. **Session-based:** Authentication clears when browser session ends

🔒 **For High-Security Applications:**

- Use **bcrypt** or **argon2** for password hashing
- Implement rate limiting (e.g., max 5 login attempts)
- Add password reset flow with email verification
- Use HTTPS in production
- Implement session timeouts
- Add audit logging for login attempts
- Consider multi-factor authentication (MFA)

## Support

For authentication issues or questions:
- Check [README.md](README.md) for basic setup
- Review this guide for advanced configuration
- Contact: City of Bellevue Transportation Department - CTR Program

---

**Last Updated:** February 2026
