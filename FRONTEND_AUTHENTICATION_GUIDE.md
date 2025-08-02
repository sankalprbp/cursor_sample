# Frontend Authentication Guide

This guide explains the frontend authentication system implementation for the AI Voice Agent Platform.

## Overview

The frontend authentication system is fully connected to the backend authentication endpoints and provides a complete user authentication experience with:

- ✅ User registration and login
- ✅ Email verification
- ✅ Password reset functionality
- ✅ Token-based authentication with automatic refresh
- ✅ Secure token storage
- ✅ Comprehensive error handling
- ✅ User feedback and notifications

## Architecture

### Core Components

1. **AuthProvider** (`/src/hooks/useAuth.tsx`)
   - Manages authentication state
   - Provides authentication methods
   - Handles token storage and refresh

2. **API Service** (`/src/services/api.ts`)
   - Handles HTTP requests to backend
   - Automatic token refresh on 401 errors
   - Secure token storage
   - Comprehensive error handling

3. **Authentication Pages**
   - Login (`/src/app/login/page.tsx`)
   - Register (`/src/app/register/page.tsx`)
   - Forgot Password (`/src/app/forgot-password/page.tsx`)
   - Reset Password (`/src/app/reset-password/page.tsx`)
   - Email Verification (`/src/app/verify-email/page.tsx`)
   - Resend Verification (`/src/app/resend-verification/page.tsx`)

4. **AuthGuard** (`/src/components/AuthGuard.tsx`)
   - Protects routes requiring authentication
   - Redirects unauthenticated users to login

## Authentication Flow

### 1. User Registration

```typescript
// User fills registration form
const { register } = useAuth();
const success = await register(email, username, password);

if (success) {
  // User is logged in automatically
  // Email verification is sent
  router.push('/dashboard');
}
```

**Backend Endpoint:** `POST /api/v1/auth/register`

### 2. User Login

```typescript
// User fills login form
const { login } = useAuth();
const success = await login(email, password);

if (success) {
  // Tokens are stored securely
  // User is redirected to dashboard
  router.push('/dashboard');
}
```

**Backend Endpoint:** `POST /api/v1/auth/login`

### 3. Email Verification

```typescript
// User clicks verification link in email
const { verifyEmail } = useAuth();
const success = await verifyEmail(token);

if (success) {
  // User email is verified
  // User can access full features
}
```

**Backend Endpoint:** `POST /api/v1/auth/verify-email`

### 4. Password Reset

```typescript
// User requests password reset
const { requestPasswordReset } = useAuth();
await requestPasswordReset(email);

// User receives email with reset link
// User clicks link and sets new password
const { resetPassword } = useAuth();
await resetPassword(token, newPassword);
```

**Backend Endpoints:**
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

## Token Management

### Secure Storage

Tokens are stored using a secure storage wrapper that provides:

- Error handling for storage failures
- Cross-browser compatibility
- Safe access in SSR environments

```typescript
// Secure storage methods
secureStorage.setItem('accessToken', token);
secureStorage.getItem('accessToken');
secureStorage.removeItem('accessToken');
```

### Automatic Token Refresh

The API service automatically handles token refresh:

1. **Request Interceptor**: Adds access token to all requests
2. **Response Interceptor**: Handles 401 errors by:
   - Attempting to refresh the token
   - Retrying the original request
   - Redirecting to login if refresh fails

```typescript
// Automatic refresh flow
if (error.response?.status === 401) {
  const refreshToken = secureStorage.getItem('refreshToken');
  if (refreshToken) {
    // Attempt refresh
    const newTokens = await refreshTokens(refreshToken);
    // Retry original request
    return api(originalRequest);
  }
}
```

## Error Handling

### Comprehensive Error Messages

The system provides specific error messages for different scenarios:

```typescript
const getErrorMessage = (error: AxiosError): string => {
  switch (error.response?.status) {
    case 400: return 'Invalid request. Please check your input.';
    case 401: return 'Invalid credentials. Please check your email and password.';
    case 403: return 'Access denied. Your account may be disabled.';
    case 409: return 'Email already registered. Please use a different email.';
    case 422: return 'Validation error. Please check your input.';
    case 429: return 'Too many requests. Please try again later.';
    case 500: return 'Server error. Please try again later.';
    default: return 'An unexpected error occurred. Please try again.';
  }
};
```

### User Feedback

- **Toast Notifications**: Success and error messages
- **Form Validation**: Real-time validation feedback
- **Loading States**: Visual feedback during operations
- **Error Clearing**: Errors clear when user starts typing

## Security Features

### 1. Token Security

- Tokens stored securely with error handling
- Automatic token refresh to prevent expiration
- Secure logout with server-side token blacklisting

### 2. Input Validation

- Client-side validation using Zod schemas
- Server-side validation feedback
- XSS protection through proper input sanitization

### 3. Route Protection

```typescript
// Protect routes with AuthGuard
<AuthGuard>
  <ProtectedComponent />
</AuthGuard>
```

### 4. CSRF Protection

- Tokens included in Authorization header
- Secure cookie handling
- Same-origin policy enforcement

## Usage Examples

### Using the Auth Hook

```typescript
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const { user, login, logout, loading, error } = useAuth();
  
  const handleLogin = async () => {
    const success = await login(email, password);
    if (success) {
      // Handle successful login
    }
  };
  
  return (
    <div>
      {user ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  );
}
```

### Protected Routes

```typescript
// In your page component
import AuthGuard from '@/components/AuthGuard';

export default function DashboardPage() {
  return (
    <AuthGuard>
      <div>Protected content here</div>
    </AuthGuard>
  );
}
```

### Custom API Calls

```typescript
import api from '@/services/api';

// API calls automatically include authentication
const fetchUserData = async () => {
  try {
    const response = await api.get('/api/v1/users/me');
    return response.data;
  } catch (error) {
    // Error handling is automatic
    console.error('Failed to fetch user data:', error);
  }
};
```

## Environment Configuration

### Required Environment Variables

```bash
# Frontend environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development Setup

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Testing Authentication

### Manual Testing

1. **Registration Flow**
   - Navigate to `/register`
   - Fill in email, username, and password
   - Submit and verify email verification is sent

2. **Login Flow**
   - Navigate to `/login`
   - Enter credentials
   - Verify successful login and redirect

3. **Password Reset Flow**
   - Navigate to `/forgot-password`
   - Enter email address
   - Check email for reset link
   - Test password reset

4. **Email Verification Flow**
   - Register new account
   - Check email for verification link
   - Click link to verify email

### Automated Testing

```typescript
// Example test for login functionality
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '@/hooks/useAuth';
import LoginPage from '@/app/login/page';

test('login form submits correctly', async () => {
  render(
    <AuthProvider>
      <LoginPage />
    </AuthProvider>
  );
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' },
  });
  
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
  
  await waitFor(() => {
    expect(screen.getByText(/signing in/i)).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Common Issues

1. **Token Refresh Fails**
   - Check if refresh token is valid
   - Verify backend refresh endpoint is working
   - Check network connectivity

2. **Login Not Working**
   - Verify backend is running
   - Check API URL configuration
   - Verify user credentials are correct

3. **Email Verification Issues**
   - Check email service configuration
   - Verify email templates are set up
   - Check spam folder for verification emails

4. **CORS Issues**
   - Verify CORS configuration in backend
   - Check allowed origins in settings
   - Ensure frontend URL is in allowed origins

### Debug Mode

Enable debug logging by setting:

```typescript
// In development
console.log('Auth state:', { user, loading, error });
```

## Best Practices

1. **Always use the AuthProvider**
   - Wrap your app with AuthProvider
   - Use useAuth hook for authentication state

2. **Handle loading states**
   - Show loading indicators during authentication
   - Disable forms during submission

3. **Provide user feedback**
   - Use toast notifications for success/error
   - Show specific error messages
   - Clear errors when user starts typing

4. **Secure token handling**
   - Use secure storage methods
   - Clear tokens on logout
   - Handle storage errors gracefully

5. **Validate inputs**
   - Use Zod schemas for validation
   - Provide helpful error messages
   - Sanitize user inputs

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/verify-email` | POST | Email verification |
| `/api/v1/auth/resend-verification` | POST | Resend verification email |
| `/api/v1/auth/forgot-password` | POST | Request password reset |
| `/api/v1/auth/reset-password` | POST | Reset password |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/logout` | POST | Logout user |
| `/api/v1/auth/me` | GET | Get current user |

## Conclusion

The frontend authentication system provides a complete, secure, and user-friendly authentication experience. It handles all common authentication scenarios and provides robust error handling and user feedback.

For additional support or questions, refer to the backend authentication documentation or contact the development team.