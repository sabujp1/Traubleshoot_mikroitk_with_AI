# MikroTik Centralized Logging & AI Troubleshooting Stack

A modern DevOps pipeline for MikroTik routers using **Loki**, **Promtail**, and **Grafana**. This stack includes pre-configured Syslog parsing and AI-driven troubleshooting skills.

## 🚀 Features
- **Centralized Logging**: Collect logs from multiple MikroTik routers via Syslog.
- **Log Aggregation**: Powered by Grafana Loki for high-efficiency storage.
- **Visualization**: Professional Grafana dashboards for monitoring BGP, Firewall, and System events.
- **AI Investigation**: Built-in prompt templates to use with AI agents (like Claude/ChatGPT) for automated troubleshooting.

## 🛠️ Tech Stack
- **Promtail**: Log collector & parser.
- **Loki**: Log storage engine.
- **Grafana**: Visualization & Alerting.
- **Docker**: Containerized deployment.

## 📥 Getting Started

### 1. Prerequisites
- Ubuntu Server (or any Linux distro with Docker).
- Docker & Docker Compose.
- See [Ubuntu Installation Guide](ubuntu_installation.md) for details.

### 2. Installation
Clone this repository and run the setup script:
```bash
chmod +x run.sh
./run.sh
```

### 3. MikroTik Configuration
Follow the instructions in [mikrotik_setup.md](mikrotik_setup.md) to point your router logs to this server.

### 4. AI Troubleshooting
Use the templates in [ai_troubleshooting_skills.md](ai_troubleshooting_skills.md) to analyze network issues. Paste your router config into `mikrotik_config_export.txt` for context-aware assistance.

## 📊 Sample Queries
Check out [logql_queries.md](logql_queries.md) for ready-to-use LogQL queries for:
- BGP state changes.
- Firewall drop monitoring.
- User authentication audits.

## 🔒 Security Note
Never push your actual `mikrotik_config_export.txt` to a public repository. It is included in `.gitignore` by default.

---
Built with ❤️ for Network Engineers.
