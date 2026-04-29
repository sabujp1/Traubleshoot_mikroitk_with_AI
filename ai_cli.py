import requests
import urllib3
import json
import sys
import os
from mikrotik_api_query import MikrotikAPI

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_config():
    """Load config from environment."""
    config = {
        "host": os.getenv("MIKROTIK_HOST"),
        "user": os.getenv("MIKROTIK_USER"),
        "password": os.getenv("MIKROTIK_PASSWORD"),
        "no_ssl": os.getenv("MIKROTIK_NO_SSL", "true").lower() == "true",
        "log_path": "/var/log/mikrotik/routers.log"
    }
    
    if not all([config["host"], config["user"], config["password"]]):
        print("❌ Error: Missing MikroTik environment variables (MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASSWORD).")
        return None
    
    return config

def get_latest_logs(file_path, lines=20):
    """Read the last N lines from the log file."""
    if not os.path.exists(file_path):
        return f"⚠️ Log file not found at {file_path}. (Check if rsyslog is running)."
    
    try:
        with open(file_path, "r") as f:
            content = f.readlines()
            return "".join(content[-lines:])
    except Exception as e:
        return f"❌ Error reading logs: {str(e)}"

def main():
    config = get_config()
    if not config:
        sys.exit(1)
    
    # 1. Gather live data from MikroTik API
    print(f"📡 Gathering live data from MikroTik at {config['host']}...")
    api = MikrotikAPI(config["host"], config["user"], config["password"], use_ssl=not config["no_ssl"])
    
    router_data = {
        "running_interfaces": api.get_running_interfaces_count(),
        "bgp_peers": api.get_bgp_peers_count(),
        "bgp_routes": api.get_bgp_routes_count()
    }
    
    # 2. Get latest logs from the local file
    print(f"📄 Reading latest logs from {config['log_path']}...")
    latest_logs = get_latest_logs(config["log_path"])
    
    # 3. Output as a formatted Prompt for AI
    print("\n" + "="*50)
    print("🚀 MIKROTIK FULL SNAPSHOT (STATUS + LOGS)")
    print("="*50)
    print("\nCopy the text below and paste it into Claude/Gemini/ChatGPT:\n")
    print("-" * 30)
    print(f"I am troubleshooting my MikroTik router ({config['host']}).")
    print("\n--- LIVE STATUS ---")
    print(f"- Active Interfaces: {router_data['running_interfaces']}")
    print(f"- BGP Neighbors: {router_data['bgp_peers']}")
    print(f"- BGP Routes Learned: {router_data['bgp_routes']}")
    
    print("\n--- RECENT LOGS ---")
    print(latest_logs)
    
    print("\n--- TASK ---")
    print("Analyze the status and recent logs above. Identify any anomalies, security threats, or routing issues, and suggest precise RouterOS commands to resolve them.")
    print("-" * 30)
    print("="*50)

if __name__ == "__main__":
    main()
