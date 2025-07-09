#!/usr/bin/env python3
"""
Test script to verify service startup
"""

import requests
import time
import sys

def test_health_endpoints():
    """Test health endpoints for all services"""
    
    print("� Testing service health endpoints...")
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False
    
    # Test frontend health
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend health check passed")
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend health check error: {e}")
        return False
    
    # Test nginx proxy
    try:
        response = requests.get("http://localhost/health", timeout=10)
        if response.status_code == 200:
            print("✅ Nginx proxy health check passed")
        else:
            print(f"❌ Nginx proxy health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Nginx proxy health check error: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test basic API endpoints"""
    
    print("\n� Testing API endpoints...")
    
    # Test API root
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("✅ API root endpoint working")
        else:
            print(f"❌ API root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API root endpoint error: {e}")
        return False
    
    # Test API docs
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Voice Agent Platform Startup Test")
    print("=" * 50)
    
    # Wait a bit for services to fully start
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Test health endpoints
    if not test_health_endpoints():
        print("\n❌ Health checks failed!")
        sys.exit(1)
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n❌ API tests failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Services are running correctly.")
    print("\n� Service URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Nginx Proxy: http://localhost")

if __name__ == "__main__":
    main()