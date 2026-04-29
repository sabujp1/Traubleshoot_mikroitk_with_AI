# MikroTik RouterOS Logging Configuration

To send logs to your new Loki stack, you need to configure a remote logging action and point your desired log topics to that action.

## 1. Create a Remote Logging Action
Replace `<PROMTAIL_IP>` with the IP address of the machine running Docker. Port `1514` matches the one configured in `docker-compose.yml`.

```routeros
/system logging action
add name=promtail-loki remote=<PROMTAIL_IP> remote-port=1514 target=remote
```

## 2. Configure Logging Rules
Add rules to send specific logs to the `promtail-loki` action.

### Essential Logs (Info, Errors, Warnings)
```routeros
/system logging
add action=promtail-loki topics=info
add action=promtail-loki topics=error
add action=promtail-loki topics=warning
add action=promtail-loki topics=critical
```

### BGP Logs
```routeros
/system logging
add action=promtail-loki topics=bgp
```

### Firewall Logs (Requires "Log" checked in firewall rules)
```routeros
/system logging
add action=promtail-loki topics=firewall
```

### Login/Authentication Logs
```routeros
/system logging
add action=promtail-loki topics=system,info,account
```

## 3. Verify Configuration
Check if the router is sending logs:
```routeros
/log print where action=promtail-loki
```

---
> [!TIP]
> Ensure your machine's firewall allows UDP traffic on port `1514` from the router's IP.
