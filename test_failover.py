#!/usr/bin/env python3
import requests
import time
import subprocess

print("🔀 TESTING FAILOVER...")

# Generate some initial traffic
print("1. Initial traffic to blue...")
for i in range(10):
    try:
        r = requests.get('http://localhost:8080', headers={'X-App-Pool': 'blue'}, timeout=5)
        print(f"   Blue: {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    time.sleep(0.1)

print("2. Stopping blue container...")
subprocess.run(["docker-compose", "stop", "app_blue"])

print("3. Traffic should failover to green...")
for i in range(15):
    try:
        r = requests.get('http://localhost:8080', headers={'X-App-Pool': 'blue'}, timeout=5)
        print(f"   Request {i+1}: {r.status_code}")
    except Exception as e:
        print(f"   Request {i+1}: {e}")
    time.sleep(0.1)

print("4. Restarting blue...")
subprocess.run(["docker-compose", "start", "app_blue"])

print("✅ Failover test complete - check watcher logs for alerts!")
