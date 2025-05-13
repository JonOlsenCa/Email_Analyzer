#!/usr/bin/env python3
"""
Test script for the Refresh Emails server.

This script tests if the Refresh Emails server is running and can be accessed.
"""

import sys
import requests
import time

def test_server():
    """Test if the Refresh Emails server is running."""
    print("Testing connection to Refresh Emails server...")
    
    try:
        # Try to connect to the server
        response = requests.get("http://localhost:8001/refresh", timeout=5)
        
        # Check if we got a response
        if response.status_code == 200:
            print("SUCCESS: Server is running and responding!")
            return True
        else:
            print(f"ERROR: Server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Is it running?")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Wait a moment to give the server time to start
    time.sleep(2)
    
    # Test the server
    success = test_server()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
