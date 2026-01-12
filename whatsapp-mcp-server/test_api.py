#!/usr/bin/env python3
"""
Quick test script for WhatsApp MCP FastAPI
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n📋 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n📋 Testing / endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint works")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_contacts():
    """Test contacts endpoint"""
    print("\n📋 Testing /contacts endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/contacts", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contacts endpoint works")
            print(f"   Returned {len(data)} contacts")
            if data:
                print(f"   First contact: {data[0]}")
            return True
        else:
            print(f"❌ Contacts failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Contacts error: {e}")
        return False

def test_chats():
    """Test chats endpoint"""
    print("\n📋 Testing /chats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/chats", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chats endpoint works")
            print(f"   Returned {len(data)} chats")
            if data:
                print(f"   First chat: {data[0]}")
            return True
        else:
            print(f"❌ Chats failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Chats error: {e}")
        return False

def test_docs():
    """Test documentation endpoint"""
    print("\n📋 Testing /docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        if response.status_code == 200:
            print(f"✅ Documentation available at {BASE_URL}/docs")
            return True
        else:
            print(f"❌ Docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Docs error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  WhatsApp MCP FastAPI - Quick Test Suite")
    print("=" * 70)
    
    # Check if server is running
    print("\n🔍 Checking if server is running...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=1)
        print("✅ Server is running")
    except:
        print(f"❌ Server not responding at {BASE_URL}")
        print("\nStart the server with:")
        print("  cd whatsapp-mcp-server")
        print("  python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Run tests
    results = []
    results.append(("Health", test_health()))
    results.append(("Root", test_root()))
    results.append(("Docs", test_docs()))
    results.append(("Contacts", test_contacts()))
    results.append(("Chats", test_chats()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    # Next steps
    print("\n" + "=" * 70)
    print("  Next Steps")
    print("=" * 70)
    print(f"\n1. View interactive API docs: {BASE_URL}/docs")
    print(f"2. View ReDoc: {BASE_URL}/redoc")
    print(f"3. Read: whatsapp-mcp-server/README_API.md")
    print(f"4. Read: ../QUICK_START.md for code examples")
    print("\n⚠️  Note: Make sure Go bridge is running on port 8080:")
    print("   cd whatsapp-bridge && go run main.go")
    print()
