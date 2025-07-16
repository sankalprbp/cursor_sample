# Voice Agent Platform - Authentication System

## Overview

This document provides a comprehensive guide to the authentication system implemented for the Voice Agent Platform. The system includes complete password hashing, token blacklisting with Redis, role-based access control, user registration flow, and password reset functionality.

## Features

### ✅ Complete Password Hashing
- **bcrypt** algorithm for secure password hashing
- Automatic salt generation
- Password verification utilities
- Configurable hashing rounds

### ✅ Token Blacklisting with Redis
- JWT tokens with unique identifiers (JTI)
- Redis-based token blacklisting for logout
- Automatic token expiration cleanup
- Support for blacklisting both access and refresh tokens

### ✅ Role-Based Access Control (RBAC)
- Four user roles: `SUPER_ADMIN`, `TENANT_ADMIN`, `TENANT_USER`, `AGENT`
- Hierarchical permission system
- Decorators for easy role enforcement
- FastAPI dependencies for endpoint protection

### ✅ Complete User Registration Flow
- User registration with email verification
- Automatic email sending for verification
- Secure token generation for verification links
- Welcome emails after successful verification

### ✅ Password Reset Functionality
- Secure password reset with email tokens
- Time-limited reset tokens (1 hour expiry)
- Email notifications for reset requests
- Protection against email enumeration attacks

## Architecture

### Core Components

1. **AuthService** (`app/services/auth.py`)
   - Central authentication logic
   - Password hashing and verification
   - JWT token management
   - User creation and verification

2. **Security Module** (`app/core/security.py`)
   - Role-based access control decorators
   - Permission checking utilities
   - FastAPI dependency factories

3. **Email Service** (`app/services/email.py`)
   - Email template management
   - SMTP integration
   - Verification and reset email sending

4. **Authentication Endpoints** (`app/api/v1/endpoints/auth.py`)
   - REST API endpoints for all auth operations
   - Request/response schemas
   - Error handling

## API Endpoints

### Public Endpoints

#### POST `/api/v1/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "tenant_user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "User registered successfully. Please check your email for verification instructions.",
  "verification_required": true
}
```

#### POST `/api/v1/auth/login`
Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/verify-email`
Verify user email with token from email.

**Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

#### POST `/api/v1/auth/forgot-password`
Initiate password reset process.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### POST `/api/v1/auth/reset-password`
Reset password with token from email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newsecurepassword456"
}
```

### Protected Endpoints

#### GET `/api/v1/auth/me`
Get current user information.

**Headers:** `Authorization: Bearer <access_token>`

#### POST `/api/v1/auth/refresh`
Refresh access token using refresh token.

#### POST `/api/v1/auth/change-password`
Change user password (requires verified email).

#### POST `/api/v1/auth/logout`
Logout and blacklist current token.

#### POST `/api/v1/auth/resend-verification`
Resend email verification token.

### Admin Endpoints

#### GET `/api/v1/auth/admin/users`
List users (admin only).

#### PATCH `/api/v1/auth/admin/users/{user_id}/activate`
Activate/deactivate user (admin only).

## Role-Based Access Control

### User Roles

1. **SUPER_ADMIN**
   - Full platform access
   - Can manage all tenants and users
   - Highest privilege level

2. **TENANT_ADMIN**
   - Manage users within their tenant
   - Access to tenant-specific admin features
   - Cannot access other tenants' data

3. **TENANT_USER**
   - Standard user access
   - Can only access their own data
   - Basic platform features

4. **AGENT**
   - System/API user
   - Limited programmatic access
   - Same privilege level as TENANT_USER

### Using RBAC Decorators

```python
from app.core.security import require_role, require_permission, require_verified_email
from app.models.user import UserRole

# Require specific role
@require_role(UserRole.TENANT_ADMIN)
async def admin_function(user: User):
    pass

# Require specific permission
@require_permission("manage_users", "user")
async def manage_users_function(user: User):
    pass

# Require verified email
@require_verified_email()
async def verified_only_function(user: User):
    pass
```

### Using FastAPI Dependencies

```python
from app.core.security import require_admin, require_super_admin, require_verified_user

@router.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(require_admin)):
    return {"message": "Admin access granted"}

@router.get("/super-admin-only")
async def super_admin_endpoint(current_user: User = Depends(require_super_admin)):
    return {"message": "Super admin access granted"}

@router.get("/verified-users-only")
async def verified_endpoint(current_user: User = Depends(require_verified_user)):
    return {"message": "Verified user access granted"}
```

## Token Management

### JWT Token Structure

Access tokens contain:
- `sub`: User ID
- `username`: Username
- `exp`: Expiration timestamp
- `jti`: Unique token identifier (for blacklisting)
- `type`: "access"

Refresh tokens contain:
- `sub`: User ID
- `username`: Username
- `exp`: Expiration timestamp
- `jti`: Unique token identifier
- `type`: "refresh"

### Token Blacklisting

When a user logs out, their token's JTI is added to Redis with an expiration matching the token's expiration. This prevents the token from being used even if it hasn't expired yet.

**Redis Keys:**
- `blacklist:token:{jti}`: Stores blacklisted token IDs

### Token Expiration

- **Access tokens**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh tokens**: 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- **Email verification tokens**: 24 hours
- **Password reset tokens**: 1 hour

## Email Integration

### Email Templates

The system includes professionally styled HTML email templates for:

1. **Welcome/Verification Email**
   - Sent after user registration
   - Contains verification link
   - 24-hour expiration notice

2. **Password Reset Email**
   - Sent when user requests password reset
   - Contains secure reset link
   - 1-hour expiration notice
   - Security warnings

3. **Welcome Email**
   - Sent after successful email verification
   - Platform feature overview
   - Call-to-action to dashboard

4. **Security Alert Email**
   - Sent for security-related events
   - IP address logging
   - Action recommendations

### SMTP Configuration

Configure email settings in your environment:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com
FRONTEND_URL=https://yourapp.com
```

## Security Best Practices

### Password Security
- Minimum 8 characters required
- bcrypt hashing with automatic salting
- No password storage in plain text
- Password history prevention (can be implemented)

### Token Security
- Short-lived access tokens (30 minutes)
- Secure token blacklisting on logout
- Unique token identifiers (JTI)
- HTTPS-only in production

### Rate Limiting
Consider implementing rate limiting for:
- Login attempts
- Password reset requests
- Email verification requests

### Security Headers
Ensure your FastAPI app includes security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@voiceagent.com
FRONTEND_URL=http://localhost:3000
```

### Database Setup

Ensure your database includes the user model with all required fields:

```sql
-- Users table with authentication fields
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'tenant_user',
    tenant_id UUID,
    last_login TIMESTAMP WITH TIME ZONE,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Usage Examples

### Python Client Example

```python
import httpx
import asyncio

async def example_usage():
    # Register user
    async with httpx.AsyncClient() as client:
        # Register
        response = await client.post(
            "http://localhost:8000/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": "testuser",
                "password": "securepass123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        print("Registration:", response.json())
        
        # Login
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "securepass123"
            }
        )
        tokens = response.json()
        
        # Use access token
        response = await client.get(
            "http://localhost:8000/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print("User info:", response.json())

asyncio.run(example_usage())
```

### JavaScript/Frontend Example

```javascript
// Register user
const registerResponse = await fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'testuser',
    password: 'securepass123',
    first_name: 'Test',
    last_name: 'User'
  })
});

// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepass123'
  })
});

const tokens = await loginResponse.json();
localStorage.setItem('access_token', tokens.access_token);
localStorage.setItem('refresh_token', tokens.refresh_token);

// Use access token
const userResponse = await fetch('/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check SMTP configuration
   - Verify email credentials
   - Check firewall/network settings

2. **Tokens not working**
   - Verify SECRET_KEY is set
   - Check token expiration
   - Ensure token is not blacklisted

3. **Permission denied errors**
   - Verify user role/permissions
   - Check email verification status
   - Ensure user is active

4. **Redis connection issues**
   - Verify Redis server is running
   - Check REDIS_URL configuration
   - Test Redis connectivity

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check Redis contents:
```bash
redis-cli
> KEYS blacklist:*
> KEYS verification:*
> KEYS reset:*
```

## Testing

Run the example demonstration:

```bash
cd backend
python example_auth_usage.py
```

This will test all authentication features and provide feedback on what's working correctly.

## Production Considerations

### Security
- Use HTTPS in production
- Set strong SECRET_KEY
- Configure rate limiting
- Enable security headers
- Monitor for suspicious activity

### Performance
- Configure Redis connection pooling
- Use database connection pooling
- Implement token cleanup jobs
- Monitor email delivery

### Monitoring
- Log authentication events
- Monitor failed login attempts
- Track email delivery rates
- Set up alerts for security events

---

This authentication system provides enterprise-grade security with all the essential features needed for a modern web application. The modular design makes it easy to extend and customize for specific requirements.