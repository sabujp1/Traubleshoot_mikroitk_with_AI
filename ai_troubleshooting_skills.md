# 🤖 AI Troubleshooting Skills for MikroTik

Structured prompt templates for AI-assisted log analysis using ChatGPT, Claude, or Gemini.
Each "Skill" is a ready-to-paste prompt — fill in the placeholders in `[brackets]` before sending.

---

## How to Use

1. **Get your logs** from Grafana → Explore using the LogQL queries below each skill
2. **Export your router config** (optional but recommended for context):
   ```routeros
   /export hide-sensitive
   ```
3. **Copy the prompt template**, paste your logs and config into it, send to the AI

---

## Skill 1 — BGP Disconnect Investigator

**When to use**: A BGP session drops and you want to know why.

**LogQL to get the logs first:**
```logql
{job="mikrotik_logs"} |= "bgp" |~ "established|idle|state changed|error" | last 50
```

**Prompt Template:**
```
I am a network engineer. My MikroTik router has a BGP session issue with peer [PEER_IP / PEER_AS].

Here are the relevant log lines from my Loki stack:
[PASTE LOGS HERE]

Here is my BGP configuration:
[PASTE /routing/bgp/connection print detail output]

Please:
1. Identify what caused the BGP session to drop (HoldTimer expired, TCP reset, route policy rejection, etc.)
2. Show a timeline of events leading up to the disconnect
3. Check if any interface or routing changes happened at the same timestamp
4. Provide the exact RouterOS commands to fix the root cause
```

---

## Skill 2 — Firewall Attack Mapper

**When to use**: You see unexpected firewall drops and want to understand if it's an attack.

**LogQL to get the logs first:**
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" | last 100
```

**To focus on a specific IP:**
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" |= "[SRC_IP]"
```

**Prompt Template:**
```
I am a network engineer. My MikroTik firewall is generating these drop logs:

[PASTE FIREWALL LOGS HERE]

My current firewall rules:
[PASTE /ip firewall filter print output]

Please:
1. Group the drops by source IP, destination port, and protocol
2. Build a timeline of the activity
3. Classify the behaviour: port scan / brute-force / DDoS / misconfigured client
4. Recommend MikroTik firewall rules or address-list entries to block the threat
5. Provide the exact RouterOS commands to implement your recommendations
```

---

## Skill 3 — Login Security Auditor

**When to use**: You want to audit who is accessing your router.

**LogQL to get the logs first:**
```logql
{job="mikrotik_logs"} |= "account" |~ "logged in|login failure|logged out"
```

**Prompt Template:**
```
I am a network engineer. Here are the authentication logs from my MikroTik router:

[PASTE AUTH LOGS HERE]

My current user and service configuration:
[PASTE /user print and /ip service print output]

Please:
1. Count total successful logins vs failed login attempts
2. List the top source IPs for failed logins with their attempt counts
3. Identify any logins at unusual hours (define "unusual" as outside 06:00–22:00)
4. Identify which services (SSH, Winbox, Web) are most targeted
5. Recommend security hardening steps specific to what you see in the logs
6. Provide RouterOS commands to implement the recommendations (e.g., disable unused services, add IP allowlists)
```

---

## Skill 4 — Interface Flapping Detector

**When to use**: An interface keeps going up and down.

**LogQL to get the logs first:**
```logql
{job="mikrotik_logs"} |= "interface" |~ "link up|link down" |= "[INTERFACE_NAME]"
```

**Prompt Template:**
```
I am a network engineer. This interface on my MikroTik is flapping: [INTERFACE_NAME]

Here are the interface event logs:
[PASTE LOGS HERE]

Interface configuration:
[PASTE /interface print detail where name=[INTERFACE_NAME]]

Please:
1. Calculate the mean time between link-down events
2. Determine if the flapping is random (hardware/physical) or periodic (negotiation/config issue)
3. Suggest causes: SFP issue, cable, auto-negotiation mismatch, MTU, remote device config
4. Provide RouterOS commands to diagnose further (e.g., force speed/duplex, check SFP diagnostic)
5. Recommend a fix
```

---

## Skill 5 — BGP Route Count Anomaly

**When to use**: You're receiving fewer or more BGP routes than expected.

**LogQL to get the logs first:**
```logql
{job="mikrotik_logs"} |= "bgp" | last 30
```

**Also query the router directly:**
```bash
python mikrotik_api_query.py --host [ROUTER_IP] --user api-user --password [PASSWORD] --no-ssl
```

**Prompt Template:**
```
I am a network engineer. My MikroTik BGP setup shows unexpected route counts.

Current route count from REST API: [PASTE OUTPUT FROM mikrotik_api_query.py]

BGP peer configuration:
[PASTE /routing/bgp/connection print detail]

Recent BGP logs:
[PASTE BGP LOGS]

Expected routes from peer [PEER_IP/AS]: approximately [EXPECTED_COUNT]

Please:
1. Identify why the route count may be lower or higher than expected
2. Check if any route filtering (prefix-lists, route-maps) could be dropping routes
3. Suggest diagnostic commands to run on the router
4. Recommend configuration fixes
```

---

## Skill 6 — Full System Health Check

**When to use**: General health check after an incident or before a maintenance window.

**LogQL to get the logs:**
```logql
# Errors in the last hour
{job="mikrotik_logs", severity=~"err|crit"} [1h]
```

**Prompt Template:**
```
I am a network engineer. Please do a full health assessment of my MikroTik router.

Router logs (last 1 hour, errors and warnings only):
[PASTE LOGS]

Current router config export:
[PASTE /export hide-sensitive]

Current metrics from REST API:
[PASTE OUTPUT FROM mikrotik_api_query.py]

Please:
1. Summarize the health status (🟢 Good / 🟡 Warning / 🔴 Critical) for each area:
   - BGP sessions
   - Firewall
   - Interfaces
   - Authentication
   - System resources
2. List any issues found, ordered by severity
3. Provide specific RouterOS commands to address each issue
```

---

## Skill 7 — Context-Aware Config vs Log Correlation

**When to use**: Something is broken but you're not sure if it's config or network.

**Prompt Template:**
```
I am a network engineer troubleshooting an issue on my MikroTik: [DESCRIBE THE ISSUE]

Relevant log lines:
[PASTE LOGS]

Full router config:
[PASTE /export hide-sensitive]

Please:
1. Identify all config sections relevant to this issue
2. Correlate the logs with the config — what config is causing this behaviour?
3. Distinguish between a configuration mistake vs a network/external event
4. Provide the exact RouterOS commands to resolve the issue
5. Suggest monitoring queries I should set up in Grafana to detect this faster next time
```

---

## Quick Reference — LogQL Starters

| Issue | LogQL Query |
|---|---|
| All errors | `{job="mikrotik_logs", severity=~"err\|crit"}` |
| BGP events | `{job="mikrotik_logs"} \|= "bgp"` |
| Firewall drops | `{job="mikrotik_logs"} \|= "firewall" \|= "drop"` |
| Login failures | `{job="mikrotik_logs"} \|= "login failure"` |
| Interface flaps | `{job="mikrotik_logs"} \|~ "link up\|link down"` |
| Specific router | `{job="mikrotik_logs", host="router-01"}` |

---

> **Tip**: Always use `hide-sensitive` when exporting configs: `/export hide-sensitive` — this redacts passwords before you paste into an AI chat.
