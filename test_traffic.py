#!/usr/bin/env python3
import requests
import time

def test_traffic():
    print("Testing traffic...")
    
    # Test both pools
    for pool in ['blue', 'green']:
        try:
            r = requests.get(
                'http://localhost:8080',
                headers={'X-App-Pool': pool},
                timeout=5
            )
            print(f"{pool}: {r.status_code}")
            print(f"   Headers - Pool: {r.headers.get('X-App-Pool')}")
            print(f"   Headers - Release: {r.headers.get('X-Release-Id')}")
        except Exception as e:
            print(f"{pool}: {e}")

def generate_traffic():
    print("Generating traffic for alerts...")
    for i in range(30):
        pool = 'blue' if i % 2 == 0 else 'green'
        try:
            r = requests.get(
                f'http://localhost:8080',
                headers={'X-App-Pool': pool},
                timeout=5
            )
            print(f"Request {i+1} to {pool}: {r.status_code}")
        except Exception as e:
            print(f"Request {i+1}: {e}")
        time.sleep(0.1)

if __name__ == "__main__":
    test_traffic()
    print()
    generate_traffic()
