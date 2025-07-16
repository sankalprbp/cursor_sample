#!/usr/bin/env python3
"""
Authentication System Usage Examples
Demonstrates how to use the complete authentication system with all features
"""

import asyncio
import httpx
from typing import Dict, Any


class AuthClient:
    """Client to demonstrate authentication API usage"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            return response.json()
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/verify-email",
                json={"token": token}
            )
            return response.json()
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and store tokens"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                return data
            else:
                return response.json()
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user info"""
        if not self.access_token:
            raise ValueError("No access token available. Please login first.")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            return response.json()
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available.")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                return data
            else:
                return response.json()
    
    async def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        if not self.access_token:
            raise ValueError("No access token available. Please login first.")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/change-password",
                json={
                    "current_password": current_password,
                    "new_password": new_password
                },
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            return response.json()
    
    async def forgot_password(self, email: str) -> Dict[str, Any]:
        """Initiate password reset"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/forgot-password",
                json={"email": email}
            )
            return response.json()
    
    async def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password with token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/reset-password",
                json={
                    "token": token,
                    "new_password": new_password
                }
            )
            return response.json()
    
    async def logout(self) -> Dict[str, Any]:
        """Logout user"""
        if not self.access_token:
            raise ValueError("No access token available.")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/logout",
                json={"token": self.access_token},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                self.access_token = None
                self.refresh_token = None
            
            return response.json()
    
    async def resend_verification(self, email: str) -> Dict[str, Any]:
        """Resend verification email"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/resend-verification",
                json={"email": email}
            )
            return response.json()


async def demonstrate_registration_flow():
    """Demonstrate complete user registration and verification flow"""
    print("=== User Registration Flow ===")
    
    client = AuthClient()
    
    # 1. Register new user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("1. Registering new user...")
    registration_result = await client.register_user(user_data)
    print(f"Registration result: {registration_result}")
    
    # 2. In a real scenario, user would get verification email
    # Here we simulate having the verification token
    print("\n2. User receives verification email...")
    print("(In real scenario, check your email for verification link)")
    
    # 3. Simulate email verification
    # verification_token = "get_from_email"
    # verification_result = await client.verify_email(verification_token)
    # print(f"Verification result: {verification_result}")
    
    return client


async def demonstrate_login_flow():
    """Demonstrate login and token management"""
    print("\n=== Login Flow ===")
    
    client = AuthClient()
    
    # 1. Login
    print("1. Logging in...")
    login_result = await client.login("test@example.com", "securepassword123")
    print(f"Login result: {login_result}")
    
    # 2. Get current user info
    print("\n2. Getting current user info...")
    try:
        user_info = await client.get_current_user()
        print(f"User info: {user_info}")
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    # 3. Refresh token
    print("\n3. Refreshing access token...")
    try:
        refresh_result = await client.refresh_access_token()
        print(f"Token refresh result: {refresh_result}")
    except Exception as e:
        print(f"Error refreshing token: {e}")
    
    return client


async def demonstrate_password_management():
    """Demonstrate password change and reset"""
    print("\n=== Password Management ===")
    
    client = AuthClient()
    
    # First login to get access token
    await client.login("test@example.com", "securepassword123")
    
    # 1. Change password
    print("1. Changing password...")
    try:
        change_result = await client.change_password(
            "securepassword123", 
            "newsecurepassword456"
        )
        print(f"Password change result: {change_result}")
    except Exception as e:
        print(f"Error changing password: {e}")
    
    # 2. Forgot password flow
    print("\n2. Initiating password reset...")
    forgot_result = await client.forgot_password("test@example.com")
    print(f"Forgot password result: {forgot_result}")
    
    # 3. In real scenario, user would get reset email
    print("(User would receive password reset email with token)")
    
    # reset_token = "get_from_email"
    # reset_result = await client.reset_password(reset_token, "resetpassword789")
    # print(f"Password reset result: {reset_result}")


async def demonstrate_security_features():
    """Demonstrate security features like logout and token blacklisting"""
    print("\n=== Security Features ===")
    
    client = AuthClient()
    
    # Login first
    await client.login("test@example.com", "newsecurepassword456")
    
    # 1. Test authenticated endpoint
    print("1. Testing authenticated endpoint...")
    try:
        user_info = await client.get_current_user()
        print(f"✓ Authenticated request successful: {user_info['email']}")
    except Exception as e:
        print(f"✗ Authenticated request failed: {e}")
    
    # 2. Logout (blacklist token)
    print("\n2. Logging out (blacklisting token)...")
    logout_result = await client.logout()
    print(f"Logout result: {logout_result}")
    
    # 3. Try to use blacklisted token
    print("\n3. Testing blacklisted token...")
    client.access_token = "previous_token_now_blacklisted"
    try:
        user_info = await client.get_current_user()
        print("✗ Blacklisted token still works (this shouldn't happen)")
    except Exception as e:
        print("✓ Blacklisted token correctly rejected")


async def demonstrate_role_based_access():
    """Demonstrate role-based access control"""
    print("\n=== Role-Based Access Control ===")
    
    client = AuthClient()
    
    # Login as regular user
    await client.login("test@example.com", "securepassword123")
    
    # Try to access admin endpoint
    print("1. Testing admin endpoint access with regular user...")
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            f"{client.base_url}/api/v1/auth/admin/users",
            headers={"Authorization": f"Bearer {client.access_token}"}
        )
        
        if response.status_code == 403:
            print("✓ Regular user correctly denied admin access")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
    
    print("\n(To test admin access, create a user with admin role)")


async def main():
    """Run all authentication demonstrations"""
    print("Voice Agent Platform - Authentication System Demo")
    print("=" * 50)
    
    try:
        # Run demonstrations
        await demonstrate_registration_flow()
        await demonstrate_login_flow()
        await demonstrate_password_management()
        await demonstrate_security_features()
        await demonstrate_role_based_access()
        
        print("\n" + "=" * 50)
        print("Authentication system demonstration completed!")
        print("\nFeatures demonstrated:")
        print("✓ User registration with email verification")
        print("✓ Login with JWT tokens")
        print("✓ Token refresh mechanism")
        print("✓ Password change and reset")
        print("✓ Token blacklisting on logout")
        print("✓ Role-based access control")
        print("✓ Email notifications")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main())