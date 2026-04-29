import requests
import urllib3
import json
import sys
import os

# Disable InsecureRequestWarning for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def call_api(path, params=None):
    """
    Universal MikroTik REST API Caller.
    Path examples: 'interface', 'routing/bgp/connection', 'system/resource', 'ip/address'
    """
    host = os.getenv("MIKROTIK_HOST")
    user = os.getenv("MIKROTIK_USER")
    password = os.getenv("MIKROTIK_PASSWORD")
    no_ssl = os.getenv("MIKROTIK_NO_SSL", "true").lower() == "true"
    
    if not all([host, user, password]):
        return {"error": "Missing MikroTik environment variables (MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASSWORD)."}

    protocol = "http" if no_ssl else "https"
    url = f"{protocol}://{host}/rest/{path.lstrip('/')}"
    
    try:
        response = requests.get(
            url, 
            auth=(user, password), 
            params=params, 
            verify=False, 
            timeout=15
        )
        response.raise_for_status()
        
        if not response.text:
            return []
            
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "url": url}

def main():
    """
    CLI Usage:
    python3 mikrotik_explorer.py <path> [params_json]
    Example: python3 mikrotik_explorer.py interface '{"running":"true"}'
    """
    if len(sys.argv) < 2:
        print("\n--- MikroTik Universal Explorer ---")
        print("Usage: python3 mikrotik_explorer.py <path> [params_json]")
        print("\nCommon Paths:")
        print("  - interface")
        print("  - routing/bgp/connection")
        print("  - routing/route")
        print("  - system/resource")
        print("  - ip/address")
        print("\nExample: python3 mikrotik_explorer.py system/resource")
        sys.exit(0)

    path = sys.argv[1]
    params = None
    
    if len(sys.argv) > 2:
        try:
            params = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON parameters: {sys.argv[2]}")
            sys.exit(1)

    result = call_api(path, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
