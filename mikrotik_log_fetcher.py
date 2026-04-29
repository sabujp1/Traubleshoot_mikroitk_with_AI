import requests
import json
import argparse
from datetime import datetime, timedelta

def query_loki(query, limit=100, minutes=60):
    url = "http://localhost:3100/loki/api/v1/query_range"
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=minutes)
    
    params = {
        'query': query,
        'limit': limit,
        'start': int(start_time.timestamp() * 1e9),
        'end': int(end_time.timestamp() * 1e9),
        'direction': 'backward'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if data['status'] == 'success':
            for stream in data['data']['result']:
                labels = stream['stream']
                for value in stream['values']:
                    timestamp_ns, message = value
                    timestamp = datetime.fromtimestamp(int(timestamp_ns) / 1e9).strftime('%Y-%m-%d %H:%M:%S')
                    results.append(f"[{timestamp}] {labels.get('host', 'unknown')} | {labels.get('module', 'syslog')} | {message}")
        
        # Sort by timestamp ascending for readability
        results.reverse()
        return "\n".join(results)
    except Exception as e:
        return f"Error querying Loki: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch MikroTik logs from Loki for AI analysis.")
    parser.add_argument("--query", type=str, default='{job="mikrotik_logs"}', help='LogQL query (default: {job="mikrotik_logs"})')
    parser.add_argument("--limit", type=int, default=50, help="Number of log lines to fetch")
    parser.add_argument("--minutes", type=int, default=60, help="Time window in minutes")
    
    args = parser.parse_args()
    
    print(f"--- Fetching last {args.limit} logs from Loki ---")
    logs = query_loki(args.query, args.limit, args.minutes)
    print(logs)
    print("--- End of Logs ---")
