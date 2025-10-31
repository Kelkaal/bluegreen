#!/usr/bin/env python3
import os
import time
import requests
import sys
from collections import deque

print("WATCHER STARTED - TEST MODE (30s cooldown)")
sys.stdout.flush()

class Watcher:
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        self.error_threshold = float(os.getenv('ERROR_RATE_THRESHOLD', '2.0'))
        self.window_size = int(os.getenv('WINDOW_SIZE', '200'))
        # Reduced cooldown for testing
        self.cooldown_sec = 30  # 30 seconds for testing instead of 300

        self.requests = deque(maxlen=self.window_size)
        self.last_pool = None
        self.last_failover_alert = 0
        self.last_error_alert = 0

        print(f"Config: threshold={self.error_threshold}%, window={self.window_size}, cooldown={self.cooldown_sec}s (TEST MODE)")
        print(f"Slack: {' SET' if self.slack_webhook else ' NOT SET'}")
        sys.stdout.flush()

    def parse_line(self, line):
        try:
            data = {}
            for part in line.split('|'):
                if ':' in part:
                    key, val = part.split(':', 1)
                    data[key] = val
            return data
        except:
            return None

    def calculate_errors(self):
        if len(self.requests) < 10:
            return 0
        errors = sum(1 for r in self.requests if r.get('status', '').startswith('5'))
        return (errors / len(self.requests)) * 100

    def should_alert_failover(self):
        now = time.time()
        if now - self.last_failover_alert < self.cooldown_sec:
            return False
        self.last_failover_alert = now
        return True

    def should_alert_error(self):
        now = time.time()
        if now - self.last_error_alert < self.cooldown_sec:
            return False
        self.last_error_alert = now
        return True

    def send_alert(self, title, message):
        print(f"ALERT: {title}")
        print(f"    {message}")
        sys.stdout.flush()
        
        if not self.slack_webhook:
            print("     Slack not configured - alert logged only")
            sys.stdout.flush()
            return

        payload = {
            "attachments": [{
                "color": "danger",
                "title": title,
                "text": message,
                "ts": time.time()
            }]
        }
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                print("    Alert sent to Slack")
            else:
                print(f"    Slack error: {response.status_code}")
            sys.stdout.flush()
        except Exception as e:
            print(f"    Failed to send to Slack: {e}")
            sys.stdout.flush()

    def watch(self):
        log_file = "/var/log/nginx/access.log"
        print(f" Watching: {log_file}")
        sys.stdout.flush()

        # Wait for file to exist
        while not os.path.exists(log_file):
            print(" Waiting for log file...")
            sys.stdout.flush()
            time.sleep(5)

        print(" Log file found, starting monitor...")
        sys.stdout.flush()

        with open(log_file, 'r') as f:
            while True:
                line = f.readline()
                if line:
                    self.process_line(line.strip())
                else:
                    time.sleep(0.1)

    def process_line(self, line):
        data = self.parse_line(line)
        if not data:
            return

        pool = data.get('pool', 'unknown')
        status = data.get('status', '')

        print(f" {pool} -> {status}")
        sys.stdout.flush()

        # Track request
        self.requests.append(data)

        # Check failover
        if (self.last_pool and pool != self.last_pool and
            pool in ['blue', 'green'] and self.last_pool in ['blue', 'green']):
            print(f" FAILOVER DETECTED: {self.last_pool} -> {pool}")
            sys.stdout.flush()
            if self.should_alert_failover():
                print(f"    SENDING FAILOVER ALERT")
                sys.stdout.flush()
                self.send_alert(
                    " Failover Detected",
                    f"Traffic automatically switched from *{self.last_pool}* to *{pool}* pool.\n\nThis indicates the primary pool may be experiencing issues.\n\n*Timestamp:* {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )
        self.last_pool = pool

        # Check error rate
        if len(self.requests) >= 20 and len(self.requests) % 10 == 0:
            error_rate = self.calculate_errors()
            print(f" Current error rate: {error_rate:.1f}% (threshold: {self.error_threshold}%)")
            sys.stdout.flush()
            if error_rate > self.error_threshold and self.should_alert_error():
                print(f" HIGH ERROR RATE DETECTED: {error_rate:.1f}%")
                sys.stdout.flush()
                self.send_alert(
                    " High Error Rate Alert",
                    f"Error rate has exceeded the threshold!\n\n*Current rate:* {error_rate:.1f}%\n*Threshold:* {self.error_threshold}%\n*Sample size:* {len(self.requests)} requests\n*Timestamp:* {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )

if __name__ == "__main__":
    watcher = Watcher()
    watcher.watch()
