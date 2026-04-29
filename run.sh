#!/bin/bash
set -e

# ─────────────────────────────────────────────────────────────────────────────
# MikroTik Logging Stack — Startup Script
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════════════╗"
echo "  ║   MikroTik Logging Stack (Loki + Promtail)       ║"
echo "  ╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Check Docker ─────────────────────────────────────────────────────────────
if ! command -v docker &> /dev/null; then
  echo -e "${RED}✗ Docker is not installed.${NC}"
  echo "  Run: curl -fsSL https://get.docker.com | sh"
  echo "  Then see ubuntu_installation.md for full setup."
  exit 1
fi
echo -e "${GREEN}✓ Docker is available${NC}"

# ── Check Docker Compose ──────────────────────────────────────────────────────
if ! docker compose version &> /dev/null; then
  echo -e "${RED}✗ Docker Compose v2 not found.${NC}"
  echo "  Run: sudo apt install docker-compose-plugin"
  exit 1
fi
echo -e "${GREEN}✓ Docker Compose is available${NC}"

# ── Open firewall port ────────────────────────────────────────────────────────
if command -v ufw &> /dev/null; then
  echo -e "${YELLOW}→ Opening UDP port 1514 (MikroTik syslog)...${NC}"
  sudo ufw allow 1514/udp > /dev/null 2>&1 || true
  echo -e "${GREEN}✓ UFW rule applied${NC}"
fi

# ── Start containers ──────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}→ Starting Loki, Promtail, and Grafana...${NC}"
docker compose up -d

# ── Wait for Loki to be healthy ───────────────────────────────────────────────
echo ""
echo -e "${YELLOW}→ Waiting for Loki to be ready...${NC}"
RETRIES=15
until curl -s http://localhost:3100/ready | grep -q "ready" || [ $RETRIES -eq 0 ]; do
  echo -n "."
  sleep 2
  RETRIES=$((RETRIES-1))
done
echo ""

if curl -s http://localhost:3100/ready | grep -q "ready"; then
  echo -e "${GREEN}✓ Loki is ready${NC}"
else
  echo -e "${RED}✗ Loki did not become ready in time. Check: docker logs loki${NC}"
fi

# ── Print summary ─────────────────────────────────────────────────────────────
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${CYAN}────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}  Stack is running! Access your services:${NC}"
echo ""
echo -e "  📊 Grafana        : ${CYAN}http://${SERVER_IP}:3000${NC}  (admin / admin)"
echo -e "  💾 Loki API       : ${CYAN}http://${SERVER_IP}:3100/ready${NC}"
echo -e "  📡 Syslog Listener: ${CYAN}UDP ${SERVER_IP}:1514${NC}"
echo -e "  📈 Promtail UI    : ${CYAN}http://${SERVER_IP}:9080${NC}"
echo -e "${CYAN}────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${YELLOW}  Next steps:${NC}"
echo "  1. Configure your MikroTik router — see: mikrotik_setup.md"
echo "     Key command:"
echo "     /system logging action add name=loki-promtail target=remote \\"
echo "       remote=${SERVER_IP} remote-port=1514 bsd-syslog=yes"
echo ""
echo "  2. Open Grafana and go to Explore → Loki"
echo "     Query: {job=\"mikrotik_logs\"}"
echo ""
echo "  3. If no logs appear, run this to debug:"
echo "     sudo tcpdump -i any udp port 1514 -n"
echo "     docker logs promtail -f"
echo ""
echo "  4. Use the AI Explorer to query your router:"
echo "     export MIKROTIK_HOST=\"[ROUTER_IP]\""
echo "     export MIKROTIK_USER=\"api-user\""
echo "     export MIKROTIK_PASSWORD=\"password\""
echo "     python3 mikrotik_explorer.py system/resource"
echo ""
