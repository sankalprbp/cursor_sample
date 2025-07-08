#!/usr/bin/env python3
"""
Simple startup test script to validate configuration and imports
without starting the full application.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔧 Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app.core.database import Base, engine
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from app.models.user import User
        print("✅ User model imported successfully")
    except Exception as e:
        print(f"❌ User model import failed: {e}")
        return False
    
    try:
        from app.models.tenant import Tenant
        print("✅ Tenant model imported successfully")
    except Exception as e:
        print(f"❌ Tenant model import failed: {e}")
        return False
    
    try:
        from app.api.v1.router import api_router
        print("✅ API router imported successfully")
    except Exception as e:
        print(f"❌ API router import failed: {e}")
        return False
    
    try:
        from app.websocket.connection_manager import ConnectionManager
        print("✅ WebSocket manager imported successfully")
    except Exception as e:
        print(f"❌ WebSocket manager import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration settings"""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Debug: {settings.DEBUG}")
        print(f"Database URL: {settings.DATABASE_URL}")
        print(f"Redis URL: {settings.REDIS_URL}")
        print(f"Sentry DSN configured: {'Yes' if settings.SENTRY_DSN else 'No'}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_sentry_config():
    """Test Sentry configuration specifically"""
    print("\n🔧 Testing Sentry configuration...")
    
    try:
        from app.core.config import settings
        
        if settings.SENTRY_DSN and settings.SENTRY_DSN.strip():
            print(f"✅ Sentry DSN is configured: {settings.SENTRY_DSN[:20]}...")
            
            # Test Sentry initialization
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
            )
            print("✅ Sentry initialized successfully")
        else:
            print("ℹ️  Sentry DSN not configured (this is fine for development)")
        
        return True
    except Exception as e:
        print(f"❌ Sentry configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Voice Agent Platform - Startup Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test configuration
    if not test_configuration():
        all_passed = False
    
    # Test Sentry configuration
    if not test_sentry_config():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application should start successfully.")
        print("\n📝 Next steps:")
        print("1. Ensure PostgreSQL is running (docker-compose up postgres)")
        print("2. Ensure Redis is running (docker-compose up redis)")
        print("3. Start the backend: cd backend && uvicorn main:app --reload")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()