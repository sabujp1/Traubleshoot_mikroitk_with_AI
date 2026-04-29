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
7. [AI Troubleshooting & Skills](#-ai-troubleshooting--skills)
8. [LogQL Query Reference](#-logql-query-reference)
9. [Security](#-security)
10. [Roadmap](#️-roadmap)

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
├── mikrotik_log_fetcher.py              # Fetches logs from Loki for AI analysis
├── mikrotik_api_query.py                # Core API library for MikroTik REST API
├── mikrotik_setup.md                     # Step-by-step router configuration guide
├── logql_queries.md                      # 30+ ready-to-use LogQL queries
├── ai_troubleshooting_skills.md          # AI prompt templates for diagnostics
├── run.sh                                # One-command startup script with health check
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

> 💡 **Note**: Docker installation is required on the host machine.

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

### Step 5 — Configure MikroTik Credentials

Set your router details as environment variables so the AI tools can access them:

```bash
export MIKROTIK_HOST="[YOUR_ROUTER_IP]"
export MIKROTIK_USER="admin"
export MIKROTIK_PASSWORD="yourpassword"
```

> 💡 **Tip**: Add these to your `~/.bashrc` to make them permanent.

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

## 🤖 AI Troubleshooting Workflow

There are two ways to use this stack with AI:

### Method A: Automated (Best for AI Agents)
If you are using an AI agent in your terminal (like Claude CLI, Gemini CLI, or Antigravity), you don't need to copy-paste. Just tell the AI:
> "Fetch the last 50 logs using `mikrotik_log_fetcher.py` and analyze my BGP config."

The AI will run the script, read the output, and provide a diagnosis automatically.

### Method B: Manual (Best for ChatGPT/Web)
When using a web-based AI:
1. **Identify** the problematic logs in Grafana.
2. **Copy** the logs and your current router configuration.
3. **Paste** them into the AI using one of the templates in `ai_troubleshooting_skills.md`.
4. **Follow** the AI's step-by-step diagnostic and fix commands.

---

## 🛠️ Automated Tools for AI

| Tool | Purpose | Usage |
|---|---|---|
| `mikrotik_log_fetcher.py` | Fetches live logs from Loki | `python3 mikrotik_log_fetcher.py --limit 50` |
| `mikrotik_api_query.py` | Queries live router metrics (BGP, Int) | `python3 mikrotik_api_query.py --host <IP>` |


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

### Example Prompt

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

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

MIT

---

> Built for network engineers who want **visibility + automation + intelligence** in one stack. ⭐
