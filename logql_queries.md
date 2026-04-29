# Essential LogQL Queries for MikroTik

Use these queries in the **Grafana Explore** tab to find specific network events.

## 1. BGP Session Events
**Goal**: Find when BGP peers go up or down.
```logql
{job="mikrotik_logs"} |= "BGP" |~ "state changed"
```

## 2. Firewall Drops
**Goal**: Monitor traffic being dropped by your firewall rules.
*(Note: Requires the pipeline labels in Promtail config to work pre-processed, or use line filters)*
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop"
```
To see drops for a specific IP:
```logql
{job="mikrotik_logs"} |= "firewall" |= "drop" |= "192.168.88.10"
```

## 3. User Authentication Attempts
**Goal**: See who is trying to log into the router (WinBox, SSH, Web).
```logql
{job="mikrotik_logs"} |= "system,info,account"
```

## 4. Interface Changes
**Goal**: Track physical or virtual interface flapping.
```logql
{job="mikrotik_logs"} |= "interface" |~ "link down|link up"
```

## 5. DHCP Leases
**Goal**: See when new devices join the network.
```logql
{job="mikrotik_logs"} |= "dhcp" |= "assigned"
```

---
> [!NOTE]
> All queries assume the `job="mikrotik_logs"` label which is set in `promtail-config.yaml`.
