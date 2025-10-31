# Blue/Green Deployment with Monitoring

A smart deployment system that automatically manages blue/green deployments, monitors application health, and sends alerts to Slack when something goes wrong.

---

## Quick Start

### 1. Get Ready
```bash
# Copy the configuration template
cp .env.example .env

# Edit the file and add your Slack webhook
nano .env
````


### 2. Start Everything

```bash
# This starts all services
docker-compose up -d --build

# Wait 30 seconds for everything to start
sleep 30
````
### 3. Check It's Working

```bash
# See all running services
docker-compose ps

# Test both color pools
curl -H "X-App-Pool: blue" http://localhost:8080/
curl -H "X-App-Pool: green" http://localhost:8080/
````
### Testing The Alert System

####  Test Failover (Color Switching)

```bash
# This stops the blue pool and watches the system switch to green
python3 test_failover.py
````
#### Test Error Detection

```bash
# This generates traffic to test error monitoring
python3 test_traffic.py
````
### 👀 Watching What's Happening

#### See Live Alerts

```bash
# Watch alerts in real-time
docker-compose logs alert_watcher -f
````
#### 🧾 Check Application Logs

```bash
# See nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log

# See application logs
docker-compose logs app_blue --tail=10
docker-compose logs app_green --tail=10
````
####  Verify Slack Alerts

After running tests, check your Slack channel for:

-  **Failover alerts** – "Traffic switched from blue to green"  
-  **Error rate alerts** – "Error rate: 18.5% (threshold: 2.0%)"
```
#### Proof It Works
```


We've verified the system with these screenshots:

-  **Slack failover alert** showing automatic color switching
<img width="1392" height="298" alt="image" src="https://github.com/user-attachments/assets/548fdd0e-733b-4435-8f4e-a7c4ac70a077" />

 
-  **Slack error rate alert** when too many requests fail
<img width="1386" height="385" alt="image" src="https://github.com/user-attachments/assets/0c0d176b-906b-4510-9e57-ea0a7ef90d48" />

-  **NGINX logs** showing detailed request information
<img width="1902" height="356" alt="Screenshot 2025-10-31 005106" src="https://github.com/user-attachments/assets/8554e19e-0b91-4e10-9679-b004a77a2129" />

### Troubleshooting

#### Alerts not showing in Slack?

Check your `SLACK_WEBHOOK_URL` in `.env` is correct.

Test with:
```bash
python3 test_slack.py
````
####  Services not starting?

Restart everything fresh:

```bash
docker-compose down
docker-compose up -d --build
````
####  Need to change alert settings?

Edit these in your `.env` file:

```bash
ERROR_RATE_THRESHOLD=2.0     # Percentage of errors that trigger alerts  
ALERT_COOLDOWN_SEC=300       # Seconds between repeat alerts
````
## ⚙️ How It Works

- **NGINX** routes traffic between blue/green pools  
- **Python Watcher** reads logs and detects problems  
- **Slack** gets alerts when things need attention  

---

### The system automatically:
- Detects when one pool stops working  
- Switches traffic to the healthy pool  
- Alerts you when error rates get too high  
- Prevents alert spam with cooldown periods  

---

**You get to sleep better at night!**
````
## Tech Stack

- **Docker & Docker Compose** – container orchestration  
- **NGINX** – smart reverse proxy for blue/green routing  
- **Python** – log monitoring and Slack alerting  
- **Slack Webhooks** – real-time deployment notifications
````
## 📁 Project Structure

````
blend/
├── docker-compose.yml
├── nginx.conf
├── watcher.py
├── requirements.txt
├── Dockerfile.watcher
├── .env
├── .env.example
├── runbook.md ← NEW
├── README.md ← NEW
├── test_failover.py
├── test_traffic.py
└── test_slack.py


