#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all validation tests in sequence
"""

import subprocess
import sys
import time
import requests

def check_server_running():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_test(test_name, test_script):
    """Run a test script and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_script], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: {test_name}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {test_name} took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {test_name} - {str(e)}")
        return False

def main():
    print("🎯 1280 Trivia - Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  cd /Users/laurenadmin/1280_Trivia")
        print("  source .venv/bin/activate")
        print("  python3 run_server.py")
        return False
    
    print("✅ Server is running at http://localhost:5001")
    
    # Define tests to run
    tests = [
        ("State Management Validation", "validate_state.py"),
        ("Game Flow Testing", "test_game_flow.py"),
        ("WebSocket Communication", "test_websockets.py")
    ]
    
    results = []
    
    for test_name, test_script in tests:
        success = run_test(test_name, test_script)
        results.append((test_name, success))
        
        # Small delay between tests
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Game logic is solid.")
        return True
    else:
        print(f"\n🚨 {total - passed} test suite(s) failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)