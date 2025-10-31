#!/usr/bin/env python3
import requests
import time
import subprocess

print("🎯 FRESH TEST FOR ALERTS")

print("1. Waiting 35 seconds for cooldown to reset...")
time.sleep(35)

print("2. Generating normal traffic...")
for i in range(20):
    pool = "blue" if i % 2 == 0 else "green"
    try:
        r = requests.get('http://localhost:8080', headers={'X-App-Pool': pool}, timeout=5)
        print(f"   {pool}: {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    time.sleep(0.1)

print("3. Triggering failover...")
print("   Stopping blue container...")
subprocess.run(["docker-compose", "stop", "app_blue"])

print("4. Generating errors to trigger error rate alert...")
for i in range(25):
    try:
        r = requests.get('http://localhost:8080', headers={'X-App-Pool': 'blue'}, timeout=2)
        print(f"   Error request {i+1}: {r.status_code}")
    except Exception as e:
        print(f"   Error request {i+1}: {e}")
    time.sleep(0.1)

print("5. Restarting blue...")
subprocess.run(["docker-compose", "start", "app_blue"])

print("✅ Test complete - check watcher logs and Slack for alerts!")
