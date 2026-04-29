import requests
import urllib3
import json
import argparse
import sys

# Disable InsecureRequestWarning if using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MikrotikAPI:
    def __init__(self, host, username, password, use_ssl=True):
        self.host = host
        self.username = username
        self.password = password
        self.protocol = "https" if use_ssl else "http"
        self.base_url = f"{self.protocol}://{self.host}/rest"
        self.auth = (self.username, self.password)

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(
                url, 
                auth=self.auth, 
                params=params, 
                verify=False, # Ignore self-signed cert warnings
                timeout=10
            )
            response.raise_for_status()
            
            # If the response is empty, return an empty list
            if not response.text:
                return []
                
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying {endpoint}: {e}")
            return None

    def get_running_interfaces_count(self):
        """Get the count of currently running interfaces."""
        # Querying /rest/interface with running=true
        data = self._get("interface", params={"running": "true"})
        if data is not None:
            return len(data)
        return 0

    def get_bgp_peers_count(self):
        """Get the count of BGP peers (Connections in ROSv7)."""
        # Note: In ROS v6 this would be routing/bgp/peer
        data = self._get("routing/bgp/connection")
        if data is not None:
            return len(data)
        return 0

    def get_bgp_routes_count(self):
        """Get the count of BGP routes."""
        # Querying /rest/routing/route with bgp=true (or origin=bgp)
        data = self._get("routing/route", params={"bgp": "true"})
        if data is not None:
            return len(data)
        return 0

def main():
    parser = argparse.ArgumentParser(description="MikroTik RouterOS REST API Query Tool")
    parser.add_argument("--host", required=True, help="Router IP address or hostname")
    parser.add_argument("--user", required=True, help="Router username")
    parser.add_argument("--password", required=True, help="Router password")
    parser.add_argument("--no-ssl", action="store_true", help="Use HTTP instead of HTTPS")
    
    args = parser.parse_args()
    
    print(f"Connecting to MikroTik router at {args.host}...")
    api = MikrotikAPI(args.host, args.user, args.password, use_ssl=not args.no_ssl)
    
    interfaces = api.get_running_interfaces_count()
    bgp_peers = api.get_bgp_peers_count()
    bgp_routes = api.get_bgp_routes_count()
    
    print("\n--- MikroTik Router Status ---")
    print(f"Running Interfaces : {interfaces}")
    print(f"BGP Peers          : {bgp_peers}")
    print(f"BGP Routes         : {bgp_routes}")
    print("------------------------------")

if __name__ == "__main__":
    main()
