# 🛠️ Utils

**GitHub About:**
Utility functions and helpers for JWT authentication, dependency injection, and security middleware. Provides reusable components for the API.

---

## 📋 Overview

Utility modules provide common functions used across the application: authentication, security, and dependency injection.

---

## 📁 Files

### `auth_dependency.py`

FastAPI dependency for route protection and authentication.

- Extracts JWT token from request headers
- Validates token authenticity
- Returns current user
- Used with `Depends()` in routes

**Usage:**

```python
@router.get("/profile")
async def get_profile(current_user = Depends(get_current_user)):
    return {"username": current_user.username}
```

### `jwt_handler.py`

JWT token creation, validation, and management.

- Encodes user data into JWT tokens
- Decodes and validates tokens
- Handles token expiration
- Secret key management

**Exports:**

- `encode_token(user_id)` - Create JWT
- `decode_token(token)` - Validate & extract user_id
- Token expiry: (configurable, typically 24-48 hours)

---

## 🔐 Security Features

- **JWT Tokens**: Stateless authentication
- **Password Hashing**: bcrypt for password storage
- **CORS**: Cross-origin request handling
- **Environment Secrets**: Secure key management

---

## 📝 Usage Example

### Creating a Protected Route

```python
from fastapi import Depends
from utils.auth_dependency import get_current_user

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Returns authenticated user info"""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email
    }
```

### Token Lifecycle

```python
from utils.jwt_handler import encode_token, decode_token

# Login - Create token
token = encode_token(user_id="user_123")

# Protected route - Validate token
user_id = decode_token(token)  # Returns: "user_123"
```

---

## 🔄 Flow

```
User Login
  ↓
auth_controller verifies credentials
  ↓
jwt_handler.encode_token()
  ↓
Return JWT to client
  ↓
Client includes JWT in Authorization header
  ↓
Request hits protected route
  ↓
auth_dependency.get_current_user()
  ↓
jwt_handler.decode_token()
  ↓
User object passed to route handler
```

---

## 📋 Configuration

### `.env` (create if missing)

```
JWT_SECRET=your_secret_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=48
```

---

## ⚖️ Token Structure

JWT tokens contain (don't decode client-side):

- **Header**: Algorithm, token type
- **Payload**: User ID, issued-at, expiry
- **Signature**: HMAC-SHA256 signature

Example decoded payload:

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "iat": 1704067200,
  "exp": 1704240000
}
```

---

## 🚫 Error Handling

Routes return:

- `401 Unauthorized` - Missing/invalid JWT
- `403 Forbidden` - Token expired
- `400 Bad Request` - Malformed token

---

## 📝 Best Practices

✅ **Do:**

- Store JWT in secure HTTP-only cookies
- Validate token expiry
- Use HTTPS in production
- Refresh tokens periodically

❌ **Don't:**

- Store sensitive data in JWT payload
- Share JWT secrets
- Use weak secret keys
- Send JWT in query params

---

## 🔄 Dependency Injection

Services can inject dependencies:

```python
from fastapi import Depends

@router.get("/repos")
async def get_repos(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    return await db.find_repos(current_user.id)
```

---

## 🛡️ Security Considerations

- JWT secrets stored in environment variables
- Tokens have expiry time
- Each request re-validates token
- Password hashing with salt
- Rate limiting recommended
