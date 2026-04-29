# 📊 LogQL Query Reference for MikroTik Logs

Use these queries in **Grafana → Explore** with the **Loki** data source selected.
All queries assume `job="mikrotik_logs"` which is set in `promtail-config.yaml`.

---

## 🔵 Basic Queries

### All MikroTik logs
```logql
{job="mikrotik_logs"}
```

### Logs from a specific router (by hostname)
```logql
{job="mikrotik_logs", host="router-core-01"}
```

### Errors and critical messages only
```logql
{job="mikrotik_logs", severity=~"err|crit|emerg"}
```

### Errors and warnings
```logql
{job="mikrotik_logs", severity=~"err|warning|crit"}
```

### Logs from a specific topic/module
```logql
{job="mikrotik_logs", module="bgp"}
```

---

## 🟢 BGP Queries

### All BGP events
```logql
{job="mikrotik_logs"} |= "bgp"
```

### BGP session state changes (up/down)
```logql
{job="mikrotik_logs"} |= "bgp" |~ "state changed|established|idle|connect|active"
```

### BGP session drops only
```logql
{job="mikrotik_logs"} |= "bgp" |~ "idle|disconnect|error"
```

### BGP events for a specific peer IP
```logql
{job="mikrotik_logs"} |= "bgp" |= "192.0.2.1"
```

### BGP holdtimer expired events
```logql
{job="mikrotik_logs"} |= "bgp" |= "hold timer expired"
```

### Count BGP state changes per hour (for a graph panel)
```logql
count_over_time({job="mikrotik_logs"} |= "bgp" |= "state changed" [1h])
```

---

## 🔴 Firewall Queries

### All firewall drops
```logql
{job="mikrotik_logs"} |= "firewall" |~ "drop|reject"
```

### Firewall drops on a specific chain
```logql
{job="mikrotik_logs"} |= "firewall" |= "forward" |= "drop"
```

### Drops from a specific source IP
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" |= "192.168.1.100"
```

### Drops targeting a specific destination port (e.g., SSH brute force)
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" |= "Dport=22"
```

### Firewall drop rate per minute (use in graph panel)
```logql
rate({job="mikrotik_logs"} |= "firewall" |= "drop" [1m])
```

### Top dropped protocols (use with log volume panel)
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" | regexp `proto (?P<proto>[^ ,]+)` | label_format proto=proto
```

---

## 🟡 Authentication & Login Queries

### All login events
```logql
{job="mikrotik_logs"} |= "account" |~ "logged in|login failure|logged out"
```

### Failed logins only
```logql
{job="mikrotik_logs"} |= "login failure"
```

### Successful logins
```logql
{job="mikrotik_logs"} |= "logged in"
```

### Login events from a specific IP
```logql
{job="mikrotik_logs"} |= "account" |= "192.168.1.50"
```

### Failed login rate per minute (anomaly detection)
```logql
rate({job="mikrotik_logs"} |= "login failure" [1m])
```

---

## 🔷 Interface Queries

### All interface state changes
```logql
{job="mikrotik_logs"} |= "interface" |~ "link up|link down|changed"
```

### Link down events only (flap detection)
```logql
{job="mikrotik_logs"} |= "link down"
```

### Events for a specific interface
```logql
{job="mikrotik_logs"} |= "interface" |= "ether1"
```

### Interface flap rate (link down events per 5 minutes)
```logql
count_over_time({job="mikrotik_logs"} |= "link down" [5m])
```

---

## 🟠 System & Resource Queries

### All system messages
```logql
{job="mikrotik_logs"} |= "system"
```

### Router reboots / system restarts
```logql
{job="mikrotik_logs"} |~ "system started|rebooting|shutdown"
```

### DHCP lease events
```logql
{job="mikrotik_logs"} |= "dhcp" |~ "assigned|deassigned|bound"
```

### DNS queries (if logging enabled)
```logql
{job="mikrotik_logs"} |= "dns"
```

### OSPF events
```logql
{job="mikrotik_logs"} |= "ospf" |~ "neighbor|state|hello"
```

---

## 📈 Rate & Volume Queries (For Dashboard Panels)

### Total log volume per minute
```logql
rate({job="mikrotik_logs"}[1m])
```

### Log volume by severity (use in stacked bar chart)
```logql
sum by (severity) (rate({job="mikrotik_logs"}[5m]))
```

### Log volume by router (multi-router setup)
```logql
sum by (host) (rate({job="mikrotik_logs"}[5m]))
```

### BGP events per hour
```logql
sum(count_over_time({job="mikrotik_logs"} |= "bgp" [1h]))
```

### Firewall drops per minute (alert threshold)
```logql
sum(rate({job="mikrotik_logs"} |= "firewall" |= "drop" [1m]))
```

---

## 🔍 Advanced Pattern Matching

### Extract and filter by a specific subnet
```logql
{job="mikrotik_logs"} |= "firewall" | regexp `(?P<src_ip>\d+\.\d+\.\d+\.\d+)` | src_ip =~ "10\\.0\\.0\\..*"
```

### Exclude noisy topics from view
```logql
{job="mikrotik_logs"} != "dhcp" != "dns" != "meter"
```

### Logs in the last 15 minutes (time range filter)
```logql
{job="mikrotik_logs"} [15m]
```

---

## 💡 Useful Tips

| Tip | Detail |
|---|---|
| `\|=` | Case-sensitive substring filter (fast) |
| `\|~` | Regex filter (powerful, slower) |
| `!=` | Exclude lines containing string |
| `!~` | Exclude lines matching regex |
| `\| regexp` | Extract named capture groups from log line |
| `\| label_format` | Rename or transform extracted labels |
| `rate()` | Logs per second over a time window |
| `count_over_time()` | Total count over a time window |

> **Remember**: Always start with a label selector like `{job="mikrotik_logs"}` — Loki requires at least one label to begin a query.
