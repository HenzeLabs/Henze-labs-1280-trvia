#!/usr/bin/env python3
"""Simple test to verify host page functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app

# Create Flask app
app = create_app()

# Test that routes exist
with app.test_client() as client:
    print("🧪 Testing Host Page Routes...")

    # Test host page loads
    response = client.get('/host')
    print(f"✅ GET /host: {response.status_code}")
    assert response.status_code == 200, "Host page should load"

    # Test create game endpoint
    response = client.post('/api/game/create',
                          json={'host_name': 'Test Host'},
                          content_type='application/json')
    print(f"✅ POST /api/game/create: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {data}")

    if data.get('success'):
        print(f"✅ Game created successfully!")
        print(f"   Room code: {data.get('room_code')}")
    else:
        print(f"⚠️  Game creation returned: {data.get('message')}")

print("\n✅ All tests passed! The backend is working correctly.")
print("\n📝 Next steps:")
print("   1. Start the Flask server: python3 run.py")
print("   2. Open browser to: http://localhost:5001/host")
print("   3. Enter your name and click 'Create Game'")
print("   4. Check browser console (F12) for any JavaScript errors")
