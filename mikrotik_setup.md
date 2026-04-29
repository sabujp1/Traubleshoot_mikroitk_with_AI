# MikroTik RouterOS — Syslog & REST API Configuration

## ⚠️ Critical Notes Before You Start

> The Docker stack listens on **UDP port 1514**. MikroTik's default syslog port is 514.
> You MUST set `remote-port=1514` explicitly in the logging action, or logs will never arrive.

Replace **`<SERVER_IP>`** with the IP address of the machine running Docker in all commands below.

---

## Part 1: Configure Remote Syslog (Log Push)

### Step 1 — Create a Remote Logging Action

```routeros
/system logging action
add name=loki-promtail target=remote remote=<SERVER_IP> remote-port=1514 bsd-syslog=yes syslog-facility=local0 syslog-severity=auto
```

| Parameter | Value | Reason |
|---|---|---|
| `target=remote` | remote | Send logs over the network |
| `remote=<SERVER_IP>` | Your server IP | Where Promtail is running |
| `remote-port=1514` | 1514 | **Must match Docker port mapping** |
| `bsd-syslog=yes` | yes | RFC3164 format — what Promtail expects |
| `syslog-facility=local0` | local0 | Standard facility for network devices |

---

### Step 2 — Add Logging Rules (What to Send)

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

---

### Step 3 — Verify the Configuration

```routeros
# List all logging actions — confirm loki-promtail is present
/system logging action print

# List all logging rules — confirm they use loki-promtail
/system logging print

# Print recent log entries to confirm they match the topics
/log print
```

---

### Step 4 — Test Connectivity from MikroTik to Server

```routeros
# Test if the server is reachable on UDP 1514
/tool netwatch add host=<SERVER_IP> interval=10s type=icmp
```

Also, on your Ubuntu server, verify UDP packets are arriving:
```bash
# Listen on port 1514 and dump raw packets (run before testing)
sudo tcpdump -i any udp port 1514 -n -vv
```

If you see packets but logs still don't appear in Grafana, check Promtail logs:
```bash
docker logs promtail -f
```

---

## Part 2: Firewall Setup on Syslog Server

On the Ubuntu server running Docker, you must allow inbound UDP 1514:

```bash
# UFW
sudo ufw allow 1514/udp

# iptables (alternative)
sudo iptables -A INPUT -p udp --dport 1514 -j ACCEPT
```

---

## Part 3: Enable REST API Access

The `mikrotik_api_query.py` script uses the RouterOS REST API (requires **RouterOS v7.1+**).

### Step 1 — Enable the Web Service (HTTP for local/testing)

```routeros
/ip service set www disabled=no port=80
```

> For production, use HTTPS:
> ```routeros
> /ip service set www-ssl disabled=no certificate=<your-cert>
> ```

### Step 2 — Create a Read-Only API User (Recommended)

```routeros
/user group add name=api-readonly policy=read,api,rest-api
/user add name=api-user group=api-readonly password=StrongPassword123
```

### Step 3 — Test the REST API

From your server, run a quick test:
```bash
curl -sk http://<ROUTER_IP>/rest/interface -u api-user:StrongPassword123 | python3 -m json.tool
```

### Step 4 — Run the Python Query Script

```bash
# Install dependency
pip install requests

# Run with HTTP (testing)
python mikrotik_api_query.py --host <ROUTER_IP> --user api-user --password StrongPassword123 --no-ssl

# Run with HTTPS (production)
python mikrotik_api_query.py --host <ROUTER_IP> --user api-user --password StrongPassword123
```

**Expected output:**
```
--- MikroTik Router Status ---
Running Interfaces : 5
BGP Peers          : 3
BGP Routes         : 12450
------------------------------
```

---

## Part 4: Quick Troubleshooting Checklist

| Check | Command |
|---|---|
| Are containers running? | `docker ps` |
| Is Promtail receiving UDP? | `sudo tcpdump -i any udp port 1514 -n` |
| Any Promtail errors? | `docker logs promtail -f` |
| Loki ready? | `curl http://localhost:3100/ready` |
| MikroTik sending logs? | `/log print` on router |
| Server firewall open? | `sudo ufw status` |
| Correct port in action? | `/system logging action print` |
