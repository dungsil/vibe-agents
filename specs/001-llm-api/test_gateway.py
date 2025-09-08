#!/usr/bin/env python3
"""
Simple test script for the LLM API Gateway.
"""

import requests
import json
import sys
import time

GATEWAY_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{GATEWAY_URL}/health")
    if response.status_code == 200:
        print("✓ Health check passed")
        return True
    else:
        print("✗ Health check failed")
        return False

def test_admin_endpoints():
    """Test admin endpoints."""
    print("\nTesting admin endpoints...")
    
    # Create a virtual key
    print("Creating virtual key...")
    response = requests.post(
        f"{GATEWAY_URL}/admin/virtual-keys",
        json={"project_name": "Test Project"}
    )
    
    if response.status_code == 200:
        key_data = response.json()
        virtual_key = key_data["id"]
        print(f"✓ Virtual key created: {virtual_key}")
        
        # List virtual keys
        response = requests.get(f"{GATEWAY_URL}/admin/virtual-keys")
        if response.status_code == 200:
            keys = response.json()
            print(f"✓ Listed {len(keys)} virtual keys")
        else:
            print("✗ Failed to list virtual keys")
            return False, None
        
        # Get usage stats
        response = requests.get(f"{GATEWAY_URL}/admin/usage-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Retrieved usage stats for {len(stats)} keys")
        else:
            print("✗ Failed to get usage stats")
            return False, None
        
        return True, virtual_key
    else:
        print("✗ Failed to create virtual key")
        return False, None

def test_proxy_endpoint(virtual_key):
    """Test proxy endpoint (will fail without real API key)."""
    print(f"\nTesting proxy endpoint with virtual key...")
    
    response = requests.post(
        f"{GATEWAY_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {virtual_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 10
        }
    )
    
    if response.status_code == 502:
        print("✓ Proxy endpoint working (no real API key configured)")
        return True
    elif response.status_code == 401:
        print("✗ Virtual key authentication failed")
        return False
    elif response.status_code == 200:
        print("✓ Proxy request successful!")
        return True
    else:
        print(f"✗ Unexpected response: {response.status_code}")
        return False

def test_invalid_key():
    """Test with invalid virtual key."""
    print("\nTesting invalid virtual key...")
    
    response = requests.post(
        f"{GATEWAY_URL}/v1/chat/completions",
        headers={
            "Authorization": "Bearer invalid-key",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello!"}]
        }
    )
    
    if response.status_code == 401:
        print("✓ Invalid key properly rejected")
        return True
    else:
        print(f"✗ Expected 401, got {response.status_code}")
        return False

def main():
    print("LLM API Gateway Test Suite")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("\n✗ Gateway is not running or unhealthy")
        print("Start the gateway with: python cli.py serve")
        sys.exit(1)
    
    # Test admin endpoints
    success, virtual_key = test_admin_endpoints()
    if not success:
        print("\n✗ Admin endpoints failed")
        sys.exit(1)
    
    # Test proxy with valid key
    if not test_proxy_endpoint(virtual_key):
        print("\n✗ Proxy endpoint failed")
        sys.exit(1)
    
    # Test invalid key
    if not test_invalid_key():
        print("\n✗ Invalid key test failed")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✓ All tests passed!")
    print("\nTo configure real API keys:")
    print("  python cli.py config set-key openai 'your-openai-key'")
    print("  python cli.py config set-key anthropic 'your-anthropic-key'")

if __name__ == "__main__":
    main()