# AI Troubleshooting Skills for MikroTik Logs

This document contains "Skills" (structured prompts) that you can use with AI agents to analyze your router logs.

## Skill 1: BGP Disconnect Investigator
**Command**: `Analyze BGP disconnect for peer [PEER_IP]`

**Prompt Template**:
> "Search the logs in `{job='mikrotik_logs'}` using LogQL for the peer IP `[PEER_IP]`. Look for 'BGP' related messages. Identify the last 'Established' state and the first 'Idle' or 'Connect' state thereafter. Explain the reason given in the log (e.g., HoldTimer expired, TCP connection reset) and check if there were any interface 'link down' events at the same timestamp."

## Skill 2: Firewall Attack Mapper
**Command**: `Map firewall drops for source [SRC_IP]`

**Prompt Template**:
> "Find all firewall drop logs where source IP is `[SRC_IP]`. Group the results by destination port and protocol. Generate a timeline of the activity. Based on the patterns, determine if this looks like a port scan, a brute-force attempt, or a misconfigured service."

## Skill 3: Login Security Auditor
**Command**: `Audit login attempts for the last 24 hours`

**Prompt Template**:
> "Retrieve logs with labels `{job='mikrotik_logs'}` and content filter `system,info,account`. Identify:
> 1. Total failed vs successful logins.
> 2. Top 3 source IPs for failed logins.
> 3. Any logins occurring at unusual hours.
> Suggest if any IP addresses should be added to a dynamic blacklist."

## Skill 4: Interface Health Check
**Command**: `Check health of interface [INTERFACE_NAME]`

**Prompt Template**:
> "Analyze logs for `[INTERFACE_NAME]`. Count how many 'link down' events occurred in the last hour. Compare this to the 'link up' events. If the ratio is high, suggest potential physical layer issues (SFP, cable) vs configuration issues."

## Skill 5: Context-Aware Troubleshooting
**Command**: `Analyze logs for [ISSUE] using my router config`

**Prompt Template**:
> "Read the router configuration in `mikrotik_config_export.txt`. Then, query the logs in `{job='mikrotik_logs'}` for `[ISSUE]`. Correlate any errors found in the logs with the relevant configuration sections (e.g., Firewall rules, BGP peer settings, or Interface configurations). Identify if the issue is caused by a configuration mismatch or a network anomaly."

---

## How to use these with AI
1.  **Export your config**: Run `/export hide-sensitive` on your MikroTik and paste the output into `mikrotik_config_export.txt`.
2.  **Ask the AI**: Copy the **Prompt Template** into your AI chat...
