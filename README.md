# 🚀 MikroTik Centralized Logging & AI Troubleshooting Stack

> **Production-ready** centralized log collection, storage, visualization, and AI-assisted troubleshooting for MikroTik RouterOS networks — powered by **Promtail + Loki + Grafana**, fully containerized with Docker.

---

## 📋 Table of Contents

1. [Architecture](#-architecture)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Quick Deployment](#-quick-deployment)
5. [Configure MikroTik Router](#-configure-mikrotik-router)
6. [Verify Logs in Grafana](#-verify-logs-in-grafana)
7. [Troubleshooting — Logs Not Arriving](#-troubleshooting--logs-not-arriving)
8. [MikroTik REST API Queries](#-mikrotik-rest-api-queries)
9. [LogQL Query Reference](#-logql-query-reference)
10. [AI Troubleshooting Workflow](#-ai-troubleshooting-workflow)
11. [Security](#-security)
12. [Roadmap](#️-roadmap)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 MikroTik Router(s)                       │
│           BSD Syslog / RFC3164 over UDP                  │
└────────────────────────┬────────────────────────────────┘
                         │  UDP → Port 1514
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     Promtail                             │
│   • Listens on UDP/1514 for syslog                       │
│   • Parses RFC3164 format                                │
│   • Adds labels: host, module, severity, tags            │
│   • Forwards to Loki via HTTP                            │
│                     Port 9080 (metrics/UI)               │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP push
                         ▼
┌─────────────────────────────────────────────────────────┐
│                       Loki                               │
│   • Stores and indexes log streams                       │
│   • Queryable via LogQL                                  │
│                     Port 3100                            │
└────────────────────────┬────────────────────────────────┘
                         │  LogQL queries
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     Grafana                              │
│   • Dashboards, Explore, Alerting                        │
│   • Loki auto-provisioned as data source                 │
│                     Port 3000                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
               🤖 AI Assistant (ChatGPT / Claude)
               Paste logs for root-cause analysis
```

**All services run in Docker on the same host, connected via an internal `loki-net` bridge network.**

---

## 📁 Project Structure

```
.
├── docker-compose.yml                    # Orchestrates Loki + Promtail + Grafana
├── promtail-config.yaml                  # Syslog UDP listener & RFC3164 parsing rules
├── grafana-provisioning/
│   └── datasources/
│       └── loki.yaml                     # Auto-provisions Loki data source in Grafana
├── mikrotik_setup.md                     # RouterOS CLI commands (syslog + REST API)
├── mikrotik_api_query.py                 # Python — query router live via REST API
├── logql_queries.md                      # 30+ ready-to-use LogQL queries
├── ai_troubleshooting_skills.md          # 7 AI prompt templates for diagnostics
├── run.sh                                # One-command startup script with health check
├── ubuntu_installation.md               # Docker setup guide for Ubuntu
└── .gitignore                            # Excludes sensitive configs & runtime data
```

> ℹ️ **`loki-config.yaml` is intentionally excluded from git** (via `.gitignore`). The Loki 3.0.0 image ships with a working built-in config at `/etc/loki/local-config.yaml`. Mounting a custom file caused startup failures on fresh server clones because the file didn't exist yet.

---

## ✅ Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Ubuntu Server | 20.04+ | `lsb_release -a` |
| Docker Engine | 24+ | `docker -v` |
| Docker Compose | v2+ (plugin) | `docker compose version` |
| MikroTik RouterOS | v6.x or v7.x | Any model with remote syslog support |
| Network path | UDP/1514 open | Router must reach server on UDP port 1514 |

### Install Docker on Ubuntu
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

> See `ubuntu_installation.md` for the full step-by-step guide.

---

## 🚀 Quick Deployment

### Step 1 — Clone the Repository

```bash
git clone https://github.com/sabujp1/Traubleshoot_mikroitk_with_AI.git
cd Traubleshoot_mikroitk_with_AI
```

### Step 2 — Open the Firewall

```bash
sudo ufw allow 1514/udp   # MikroTik syslog
sudo ufw allow 3000/tcp   # Grafana UI
sudo ufw allow 3100/tcp   # Loki API (optional, internal use)
sudo ufw reload
```

### Step 3 — Start the Stack

```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
docker compose up -d
```

### Step 4 — Confirm All Containers Are Healthy

```bash
docker ps
```

All three containers must show `Up` or `Up (healthy)`:

```
CONTAINER ID   IMAGE                    STATUS              PORTS
xxxxxxxxxxxx   grafana/grafana:latest   Up                  0.0.0.0:3000->3000/tcp
xxxxxxxxxxxx   grafana/promtail:3.0.0   Up                  0.0.0.0:1514->1514/udp, 0.0.0.0:9080->9080/tcp
xxxxxxxxxxxx   grafana/loki:3.0.0       Up (healthy)        0.0.0.0:3100->3100/tcp
```

### Step 5 — Verify Loki is Ready

```bash
curl http://localhost:3100/ready
# Expected response: ready
```

---

## 🔧 Configure MikroTik Router

> ⚠️ **This is the #1 reason logs don't arrive.** Follow these commands exactly — two flags are critical: `bsd-syslog=yes` and `remote-port=1514`.

Connect to your MikroTik via **Winbox Terminal** or **SSH**, then run:

### Step 1 — Create the Remote Logging Action

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

Replace `<SERVER_IP>` with your Ubuntu server's IP address.

| Parameter | Value | Why It Matters |
|---|---|---|
| `target=remote` | remote | Sends logs over the network |
| `remote=<SERVER_IP>` | Your server IP | Where Promtail is listening |
| `remote-port=1514` | **1514** | **Must match Docker port mapping — not the default 514** |
| `bsd-syslog=yes` | **yes** | **Enables RFC3164 format — required for Promtail to parse it** |
| `syslog-facility=local0` | local0 | Standard facility for network devices |

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

### Step 3 — Verify on the Router

```routeros
# Confirm the action was created
/system logging action print where name=loki-promtail

# Confirm the rules are active
/system logging print where action=loki-promtail

# Watch live logs to confirm topics are firing
/log print follow
```

---

## 📊 Verify Logs in Grafana

### 1. Open Grafana

```
http://<SERVER_IP>:3000
```

Login: `admin` / `admin` *(change this after first login)*

> ✅ **Loki is auto-provisioned** — no manual data source setup required.

### 2. Go to Explore

- Click the **Explore** icon (🧭) in the left sidebar
- Select **Loki** from the data source dropdown

### 3. Run a Test Query

```logql
{job="mikrotik_logs"}
```

Click **Run query**. If log lines appear → ✅ **Everything is working.**

---

## 🔍 Troubleshooting — Logs Not Arriving

Work through these checks **in order**. Each step isolates exactly where the pipeline is broken.

---

### Check 1 — Are all containers running?

```bash
docker ps
```

All three (`loki`, `promtail`, `grafana`) must be `Up`. If any are `Exited`:
```bash
docker logs <container_name>
```

---

### Check 2 — Is the server firewall open?

```bash
sudo ufw status | grep 1514
```

If port 1514 is not listed as `ALLOW`:
```bash
sudo ufw allow 1514/udp
sudo ufw reload
```

---

### Check 3 — Are UDP packets arriving at the server?

Run this on the server **while MikroTik is active**:

```bash
sudo tcpdump -i any udp port 1514 -n -vv
```

- ✅ **Packets appear** → Network path is fine → Check 4
- ❌ **No packets** → Problem is between router and server (routing, firewall, wrong IP/port)

---

### Check 4 — Is Promtail receiving and forwarding logs?

```bash
docker logs promtail -f
```

Look for:
- ✅ `msg="Listening on address" address=0.0.0.0:1514` → bound correctly
- ✅ `msg="successfully sent"` → logs reaching Loki
- ❌ `level=error` → read the message carefully for the fix

Check Promtail metrics (non-zero = receiving logs):
```bash
curl -s http://localhost:9080/metrics | grep syslog_messages_total
```

---

### Check 5 — Has Loki received any logs?

```bash
# Should list labels including "job" if logs have arrived
curl -s http://localhost:3100/loki/api/v1/labels | python3 -m json.tool
```

Also check Loki logs:
```bash
docker logs loki -f
```

---

### Check 6 — Verify MikroTik action has the two critical flags

```routeros
/system logging action print where name=loki-promtail
```

Confirm these two values:
- `bsd-syslog: yes` ← **If `no`, logs cannot be parsed**
- `remote-port: 1514` ← **If `514`, logs go to the wrong port**

Fix if needed:
```routeros
/system logging action set [find name=loki-promtail] bsd-syslog=yes remote-port=1514
```

---

### Check 7 — Restart after any config changes

```bash
docker compose down
docker compose up -d
sleep 15
curl http://localhost:3100/ready
```

---

### Quick Diagnostic Summary Table

| Symptom | Most Likely Cause | Fix |
|---|---|---|
| Container `loki` keeps restarting | Config file mount issue | Remove custom config mount, use built-in |
| No packets in `tcpdump` | Firewall or wrong IP/port on router | Check UFW + MikroTik action `remote` and `remote-port` |
| Packets arrive but nothing in Loki | `bsd-syslog=yes` missing | Set `bsd-syslog=yes` on MikroTik logging action |
| Promtail `error` in logs | YAML indentation bug in config | Validate `promtail-config.yaml` with `docker run --rm -v $(pwd)/promtail-config.yaml:/etc/promtail/config.yml grafana/promtail:3.0.0 --config.file=/etc/promtail/config.yml --check-syntax` |
| Grafana shows "Data source error" | Wrong Loki URL | Use `http://loki:3100` (Docker network name) |

---

## 🔌 MikroTik REST API Queries

Query live data directly from your router using the included Python script.
Requires **RouterOS v7.1+**.

### Enable REST API on the Router

```routeros
# Enable HTTP web service (REST API activates automatically)
/ip service set www disabled=no port=80

# Create a read-only API user (do NOT use admin for this)
/user group add name=api-readonly policy=read,api,rest-api
/user add name=api-user group=api-readonly password=StrongPassword123
```

### Run the Query Script

```bash
# Install the Python dependency
pip install requests

# Run — replace with your router's IP
python mikrotik_api_query.py \
    --host 192.168.88.1 \
    --user api-user \
    --password StrongPassword123 \
    --no-ssl
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

### What the Script Queries

| Metric | REST Endpoint | Description |
|---|---|---|
| Running Interfaces | `GET /rest/interface?running=true` | Count of interfaces currently UP |
| BGP Peers | `GET /rest/routing/bgp/connection` | Configured BGP sessions |
| BGP Routes | `GET /rest/routing/route?bgp=true` | Routes learned via BGP |

---

## 📊 LogQL Query Reference

Use these in **Grafana → Explore** with the Loki data source.

### Basics

```logql
# All MikroTik logs
{job="mikrotik_logs"}

# Logs from a specific router by hostname
{job="mikrotik_logs", host="router-core-01"}

# Errors and warnings only
{job="mikrotik_logs", severity=~"err|warning|crit"}
```

### BGP

```logql
# BGP state changes (established, idle, up, down)
{job="mikrotik_logs"} |= "bgp" |~ "state changed|established|idle"

# BGP peer drops
{job="mikrotik_logs"} |= "bgp" |= "idle"
```

### Firewall

```logql
# All firewall drops
{job="mikrotik_logs"} |= "firewall" |~ "drop|reject"

# Drops involving a specific source IP
{job="mikrotik_logs"} |= "firewall" |= "192.168.1.100"

# Firewall actions on the forward chain
{job="mikrotik_logs"} |= "forward" |= "drop"
```

### Authentication

```logql
# All login events (success + failure)
{job="mikrotik_logs"} |= "account" |~ "logged in|login failure|logged out"

# Failed logins only
{job="mikrotik_logs"} |= "login failure"
```

### Interface Events

```logql
# Interface up/down events
{job="mikrotik_logs"} |= "interface" |~ "link up|link down|changed"
```

### Rate Metrics

```logql
# Logs per minute (useful for traffic graphs)
rate({job="mikrotik_logs"}[1m])

# BGP events per hour
rate({job="mikrotik_logs"} |= "bgp" [1h])
```

> See `logql_queries.md` for more examples.

---

## 🤖 AI Troubleshooting Workflow

When you spot an issue in Grafana, use this 4-step workflow:

**Step 1** — Copy the relevant log lines from Grafana Explore

**Step 2** — Export your router config:
```routeros
/export file=config
# Then download from Files menu in Winbox
```

**Step 3** — Paste both into an AI assistant using a prompt template:

```
I am a network engineer managing MikroTik routers.

Here are my recent logs from Grafana/Loki:
[PASTE LOGS HERE]

Here is my current router configuration:
[PASTE CONFIG HERE]

Please:
1. Identify the root cause of the issue
2. Explain why it's happening
3. Provide the exact RouterOS commands to fix it
```

**Step 4** — See `ai_troubleshooting_skills.md` for topic-specific templates (BGP flapping, firewall drops, PPPoE auth failures).

---

## 🔒 Security

| Area | Recommendation |
|---|---|
| Grafana password | Change `admin/admin` immediately after first login |
| Syslog port | Restrict UDP/1514 to router IPs only: `sudo ufw allow from <ROUTER_IP> to any port 1514 proto udp` |
| REST API user | Never use `admin` — use the `api-readonly` group |
| Loki exposure | Do not expose port 3100 to the internet — it has no built-in auth |
| Git hygiene | Never commit real passwords or router configs — check `.gitignore` |

---

## 🛣️ Roadmap

- [ ] Pre-built Grafana dashboard JSON exports (BGP, Firewall, Auth panels)
- [ ] Telegram / Slack alerting integration
- [ ] Multi-router per-device dashboards
- [ ] Automatic BGP flap detection with alerting
- [ ] PPPoE session tracking panel

---

## 🔀 Git — Push & Deploy

### First time setup (from your local machine)

```bash
cd path/to/loki

# Stage all updated files
git add \
  docker-compose.yml \
  promtail-config.yaml \
  grafana-provisioning/ \
  mikrotik_setup.md \
  mikrotik_api_query.py \
  logql_queries.md \
  ai_troubleshooting_skills.md \
  run.sh \
  README.md \
  .gitignore

# Commit
git commit -m "fix: correct syslog pipeline, add REST API query script, update all docs"

# Push
git push origin main
```

### Pull and redeploy on the server

```bash
ssh root@<SERVER_IP>
cd ~/Traubleshoot_mikroitk_with_AI

git pull

# Restart the stack to apply any config changes
docker compose down
docker compose up -d

# Verify
docker ps
curl http://localhost:3100/ready
```

### What is committed vs ignored

| File | Committed | Reason |
|---|---|---|
| `docker-compose.yml` | ✅ Yes | Core infrastructure definition |
| `promtail-config.yaml` | ✅ Yes | Syslog parsing config |
| `grafana-provisioning/` | ✅ Yes | Auto-provisions Loki in Grafana |
| `mikrotik_api_query.py` | ✅ Yes | REST API query script |
| `*.md` docs | ✅ Yes | Documentation |
| `run.sh` | ✅ Yes | Startup script |
| `loki-config.yaml` | ❌ No | Loki uses built-in default — not needed on server |
| `mikrotik_config_export.txt` | ❌ No | **Contains sensitive router config** |
| `loki-data/`, `grafana-data/` | ❌ No | Runtime Docker volumes — not needed in git |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

MIT

---

> Built for network engineers who want **visibility + automation + intelligence** in one stack. ⭐
