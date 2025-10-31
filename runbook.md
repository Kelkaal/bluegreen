 Blue/Green Deployment Alert Runbook
=====================================

##  What These Alerts Mean & What To Do

### "Failover Detected" Alert
**What Happened:**
The system automatically switched traffic from one color to another (like from Blue to Green).

**Why This Happens:**
- One of your application pools stopped working
- The load balancer detected issues and switched to the backup pool
- This is the system protecting itself!

###  See Which Containers Are Running

```bash
# See which containers are running
docker-compose ps

# Check the logs of the pool that failed
docker-compose logs app_blue --tail=20
docker-compose logs app_green --tail=20
````
##  Quick Fixes

If one of your app pools stops working, you can quickly restart it and check if it’s healthy again.

###  Restart the broken pool
```bash
docker-compose restart app_blue   # or app_green
````
###  Check if it's back

```bash
curl -H "X-App-Pool: blue" http://localhost:8080/
````
## "High Error Rate" Alert

**What Happened:**
More than **2%** of recent requests are failing with server errors.

**Why This Matters:**
- Users are seeing error pages instead of your app.  
- This could mean your app is struggling or a dependency is down.
````
### What To Check

```bash
# See recent errors in nginx
docker-compose logs nginx --tail=10 | grep "50x"

# Check both app logs for clues
docker-compose logs app_blue app_green --tail=15
````
###  Quick Actions

- Check if it's a temporary spike (wait 2 minutes)
- If errors continue, restart the problematic pool
- Monitor if error rate drops below 2%
````
### Planned Maintenance

To temporarily stop alerts during updates:

```bash
# Turn off alerting
docker-compose stop alert_watcher

# Do your maintenance work...

# Turn alerting back on
docker-compose start alert_watcher
````
