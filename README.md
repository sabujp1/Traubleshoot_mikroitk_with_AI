# 🚀 MikroTik Centralized Logging & AI Troubleshooting Stack

> **Production-ready** log collection, storage, visualization, and AI-assisted troubleshooting for MikroTik RouterOS networks.

---

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Deployment](#deployment)
5. [Configure MikroTik Router](#configure-mikrotik-router)
6. [Verify Logs in Grafana](#verify-logs-in-grafana)
7. [Troubleshooting Logs Not Arriving](#troubleshooting-logs-not-arriving)
8. [MikroTik REST API Queries](#mikrotik-rest-api-queries)
9. [LogQL Query Reference](#logql-query-reference)
10. [AI Troubleshooting Workflow](#ai-troubleshooting-workflow)
11. [Security](#security)

---

## 🏗️ Architecture

```
MikroTik Router(s)
  │  Syslog UDP → port 1514
  ▼
Promtail (port 9080 / UDP 1514)
  │  Parse + Label + Forward
  ▼
Loki (port 3100)
  │  Store & Index
  ▼
Grafana (port 3000)
  │  Visualize & Alert
  ▼
AI (ChatGPT / Claude) — Paste logs for root-cause analysis
```

**Data Flow:**
1. MikroTik sends BSD Syslog (RFC3164) over **UDP to port 1514**
2. Promtail receives, parses, and labels each log entry
3. Loki stores logs indexed by labels (`host`, `module`, `severity`, `tags`)
4. Grafana queries Loki using LogQL to display dashboards and alerts

---

## 📁 Project Structure

```
.
├── docker-compose.yml              # Orchestrates Loki + Promtail + Grafana
├── loki-config.yaml                # Loki storage & ingestion configuration
├── promtail-config.yaml            # Promtail syslog listener & parsing rules
├── grafana-provisioning/
│   └── datasources/
│       └── loki.yaml               # Auto-provisions Loki in Grafana on startup
├── mikrotik_setup.md               # RouterOS CLI commands (syslog + REST API)
├── mikrotik_api_query.py           # Python script to query router via REST API
├── logql_queries.md                # Ready-to-use LogQL queries
├── ai_troubleshooting_skills.md    # AI prompt templates for diagnostics
├── run.sh                          # One-command startup script
└── ubuntu_installation.md          # Docker setup on Ubuntu
```

---

## ✅ Prerequisites

| Requirement | Notes |
|---|---|
| Ubuntu 20.04+ server | The machine that will receive logs |
| Docker Engine | `docker -v` to check |
| Docker Compose v2+ | `docker compose version` to check |
| MikroTik RouterOS v6.x or v7.x | Any model that supports remote syslog |
| Network reachability | Router must be able to reach server on **UDP/1514** |

Install Docker on Ubuntu:
```bash
# See ubuntu_installation.md for the full guide
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

---

## 🚀 Deployment

### Step 1 — Clone the Repository

```bash
git clone https://github.com/sabujp1/Traubleshoot_mikroitk_with_AI.git
cd Traubleshoot_mikroitk_with_AI
```

### Step 2 — Start the Stack

```bash
# Quick start (recommended)
chmod +x run.sh && ./run.sh

# Or manually
docker compose up -d
```

### Step 3 — Confirm All Containers Are Running

```bash
docker ps
```

Expected output — all three containers should show `Up` status:

```
CONTAINER ID   IMAGE                    STATUS          PORTS
xxxxxxxxxxxx   grafana/grafana:latest   Up (healthy)    0.0.0.0:3000->3000/tcp
xxxxxxxxxxxx   grafana/promtail:3.0.0   Up              0.0.0.0:1514->1514/udp, 0.0.0.0:9080->9080/tcp
xxxxxxxxxxxx   grafana/loki:3.0.0       Up (healthy)    0.0.0.0:3100->3100/tcp
```

### Step 4 — Verify Loki is Ready

```bash
curl http://localhost:3100/ready
# Expected: ready
```

---

## 🔧 Configure MikroTik Router

> ⚠️ **This is the most common reason logs don't arrive.** Follow these steps exactly.

### Step 1 — Create the Remote Logging Action

Connect to your router via Winbox or SSH and run:

```routeros
/system logging action
add name=loki-promtail \
    target=remote \
    remote=<SERVER_IP> \
    remote-port=1514 \
    bsd-syslog=yes \
    syslog-facility=local0 \
    syslog-severity=auto
```

> Replace `<SERVER_IP>` with your Ubuntu server's IP address.

**Why `bsd-syslog=yes`?** — Promtail is configured for RFC3164 (BSD syslog). Without this flag, MikroTik sends a non-standard format that Promtail cannot parse.

**Why port `1514`?** — Port 514 is the default but is often blocked. Our stack uses 1514 to avoid conflicts.

### Step 2 — Add Logging Rules

```routeros
/system logging
add action=loki-promtail topics=info
add action=loki-promtail topics=warning
add action=loki-promtail topics=error
add action=loki-promtail topics=critical
add action=loki-promtail topics=bgp
add action=loki-promtail topics=firewall
add action=loki-promtail topics=interface
add action=loki-promtail topics=system
add action=loki-promtail topics=account
```

### Step 3 — Verify Router Configuration

```routeros
# Confirm the action was created correctly
/system logging action print where name=loki-promtail

# Confirm the rules exist
/system logging print where action=loki-promtail
```

---

## 📊 Verify Logs in Grafana

### 1. Open Grafana

Navigate to: **`http://<SERVER_IP>:3000`**

Login: `admin` / `admin`

> ℹ️ Loki is **automatically provisioned** as a data source — no manual setup needed.

### 2. Go to Explore

- Click **Explore** (compass icon in the left sidebar)
- Select **Loki** from the data source dropdown

### 3. Run a Test Query

```logql
{job="mikrotik_logs"}
```

If logs appear → ✅ Everything is working!

If logs don't appear → See [Troubleshooting](#troubleshooting-logs-not-arriving) below.

---

## 🔍 Troubleshooting — Logs Not Arriving

Work through these checks **in order**. Each step narrows down where the pipeline is broken.

### Check 1 — Is the server firewall open?

```bash
# Check if port 1514 is open
sudo ufw status
# If UFW is active and 1514 is not listed:
sudo ufw allow 1514/udp
sudo ufw reload
```

### Check 2 — Are packets actually arriving at the server?

Run this on the server **while the router is sending logs**:

```bash
sudo tcpdump -i any udp port 1514 -n -vv
```

- **Packets appear** → packets are arriving, problem is in Promtail/Loki → go to Check 3
- **No packets** → network/firewall issue between router and server → check routing, firewall, and MikroTik config

### Check 3 — Is Promtail receiving and parsing logs?

```bash
# Watch Promtail logs in real time
docker logs promtail -f
```

Look for:
- `msg="Listening on address"` → good, it's bound to the UDP port
- `level=error` → a configuration or parsing error — read the message carefully
- `msg="Entry sent"` → logs are being forwarded to Loki successfully

Check the Promtail metrics page:
```bash
curl http://localhost:9080/metrics | grep syslog_messages_total
```

A non-zero counter here means Promtail is receiving logs.

### Check 4 — Is Loki receiving logs?

```bash
# Check Loki logs
docker logs loki -f

# Query Loki directly via its API
curl -G "http://localhost:3100/loki/api/v1/labels" | python3 -m json.tool
```

If you see `job` in the labels list, Loki has received at least one log.

### Check 5 — Verify the MikroTik action has `bsd-syslog=yes`

```routeros
/system logging action print where name=loki-promtail
```

Confirm the output shows `bsd-syslog: yes`. If not:

```routeros
/system logging action set [find name=loki-promtail] bsd-syslog=yes
```

### Check 6 — Verify the correct port on MikroTik

```routeros
/system logging action print where name=loki-promtail
```

Confirm `remote-port: 1514`. If it shows `514`, fix it:

```routeros
/system logging action set [find name=loki-promtail] remote-port=1514
```

### Check 7 — Restart the stack after config changes

```bash
docker compose down
docker compose up -d
# Wait 15 seconds then re-test
sleep 15 && curl http://localhost:3100/ready
```

---

## 🔌 MikroTik REST API Queries

Query live router data directly from the command line using the included Python script.

### Setup — Enable REST API on RouterOS (v7.1+ only)

```routeros
# Enable HTTP web service (REST API is automatic)
/ip service set www disabled=no port=80

# Create a read-only API user (recommended over using admin)
/user group add name=api-readonly policy=read,api,rest-api
/user add name=api-user group=api-readonly password=StrongPassword123
```

### Run the Query Script

```bash
# Install the required Python library
pip install requests

# Query your router
python mikrotik_api_query.py --host <ROUTER_IP> --user api-user --password StrongPassword123 --no-ssl
```

**Sample output:**
```
Connecting to MikroTik router at 192.168.88.1...

--- MikroTik Router Status ---
Running Interfaces : 6
BGP Peers          : 4
BGP Routes         : 15830
------------------------------
```

### Available Queries

| Metric | API Endpoint | Description |
|---|---|---|
| Running Interfaces | `/rest/interface?running=true` | Interfaces currently UP |
| BGP Connections | `/rest/routing/bgp/connection` | Configured BGP peers |
| BGP Routes | `/rest/routing/route?bgp=true` | Routes learned via BGP |

---

## 📊 LogQL Query Reference

Use these in **Grafana → Explore** with the Loki data source selected.

### All MikroTik Logs
```logql
{job="mikrotik_logs"}
```

### BGP Session Events (Up/Down)
```logql
{job="mikrotik_logs"} |= "bgp" |~ "state changed|established|idle"
```

### Firewall Drops
```logql
{job="mikrotik_logs"} |= "firewall" |= "forward" |~ "drop|reject"
```

### Firewall Drops from a Specific IP
```logql
{job="mikrotik_logs"} |= "firewall" |= "192.168.1.100"
```

### Login / Authentication Events
```logql
{job="mikrotik_logs"} |= "account" |~ "logged in|login failure|logged out"
```

### Interface Up/Down Events
```logql
{job="mikrotik_logs"} |= "interface" |~ "link up|link down|changed"
```

### Errors & Warnings Only
```logql
{job="mikrotik_logs", severity=~"err|warning|crit"}
```

### Logs from a Specific Router
```logql
{job="mikrotik_logs", host="router-core-01"}
```

### Log Rate (Logs per Minute)
```logql
rate({job="mikrotik_logs"}[1m])
```

> See `logql_queries.md` for more examples.

---

## 🤖 AI Troubleshooting Workflow

When you see an issue in Grafana, use this workflow:

1. **Copy the relevant log lines** from Grafana Explore
2. **Export your router config** for context:
   ```routeros
   /export file=config
   ```
3. **Paste both** into an AI assistant (ChatGPT, Claude, Gemini) using a prompt from `ai_troubleshooting_skills.md`
4. Example prompt template:
   ```
   I am a network engineer managing MikroTik routers. Here are my recent logs:
   
   [PASTE LOGS]
   
   And my router config:
   
   [PASTE CONFIG]
   
   Please identify the root cause and suggest a fix.
   ```

> See `ai_troubleshooting_skills.md` for topic-specific prompt templates (BGP, Firewall, Auth).

---

## 🔒 Security

- **Grafana**: Change the default `admin/admin` password immediately after first login
- **Loki**: Not exposed to the internet — only accessible within the Docker network
- **Syslog**: Consider IP-allowlisting port 1514 to only accept traffic from your router IPs:
  ```bash
  sudo ufw allow from <ROUTER_IP> to any port 1514 proto udp
  sudo ufw deny 1514/udp
  ```
- **API User**: Never use the `admin` account for REST API access — use the `api-readonly` group
- **Secrets**: Never commit real passwords or router configs to public repositories — see `.gitignore`

---

## 🛣️ Roadmap

- [ ] Pre-built Grafana dashboard JSON exports (BGP, Firewall, Auth)
- [ ] Telegram/Slack alerting integration
- [ ] Multi-router support with per-router dashboards
- [ ] Automatic BGP flap detection alerts
- [ ] PPPoE session tracking

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📜 License

MIT

---

> Built for network engineers who want **visibility + automation + intelligence** in one stack. ⭐
