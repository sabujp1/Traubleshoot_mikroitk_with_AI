#!/bin/bash

# Simple script to start the MikroTik Logging Stack on Ubuntu

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is not installed. Please follow the instructions in ubuntu_installation.md first.' >&2
  exit 1
fi

# Ensure firewall port for Syslog is open
echo "Ensuring UDP port 1514 is open in UFW..."
sudo ufw allow 1514/udp > /dev/null

# Start the stack
echo "Starting Loki, Promtail, and Grafana..."
docker compose up -d

echo "------------------------------------------------"
echo "Stack is running!"
echo "Grafana: http://localhost:3000"
echo "Loki API: http://localhost:3100/ready"
echo "Promtail Syslog: Listening on UDP/1514"
echo "------------------------------------------------"
echo "Next steps:"
echo "1. Configure your MikroTik router (see mikrotik_setup.md)"
echo "2. Add Loki as a datasource in Grafana (URL: http://loki:3100)"
