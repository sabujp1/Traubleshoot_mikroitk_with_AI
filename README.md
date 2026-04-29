# 🚀 MikroTik Centralized Logging & AI Troubleshooting Stack

A production-ready logging and troubleshooting platform for MikroTik networks using **Loki**, **Promtail**, and **Grafana**, enhanced with AI-assisted diagnostics.

This project helps network engineers **centralize logs, visualize events, and troubleshoot issues faster using AI workflows**.

---

## 📌 Overview

Managing multiple MikroTik routers without centralized visibility is painful. This stack solves that by:

* Collecting logs from routers via **Syslog**
* Storing and indexing logs efficiently with **Loki**
* Visualizing network events in **Grafana**
* Using AI (ChatGPT/Claude) for faster root-cause analysis

---

## 🏗️ Architecture

```text
MikroTik Router(s)
        │
        ▼
    Promtail
        │
        ▼
      Loki
        │
        ▼
     Grafana
        │
        ▼
        AI (ChatGPT / Claude)
```

---

## ⚡ Key Features

* 📡 **Centralized Logging**
  Aggregate logs from multiple MikroTik routers

* 📊 **Real-time Visualization**
  Monitor BGP, firewall, authentication, and system logs in Grafana

* 🔍 **Powerful Log Search (LogQL)**
  Quickly filter and analyze logs

* 🤖 **AI-Powered Troubleshooting**
  Use pre-built prompts to debug issues faster

* 🐳 **Docker-based Deployment**
  Easy setup and portability

---

## 🧰 Tech Stack

* **Promtail** – Log collection & parsing
* **Loki** – Log storage & indexing
* **Grafana** – Visualization & alerting
* **Docker Compose** – Deployment

---

## 🚀 Quick Start

### 1. Prerequisites

* Linux server (Ubuntu recommended)
* Docker & Docker Compose installed

👉 See: `ubuntu_installation.md`

---

### 2. Installation

```bash
git clone https://github.com/sabujp1/Traubleshoot_mikroitk_with_AI.git
cd Traubleshoot_mikroitk_with_AI

chmod +x run.sh
./run.sh
```

---

## 🔗 Configure Loki Data Source in Grafana

After starting the stack, you must connect Grafana to Loki.

### 1. Open Grafana

```bash
http://<your-server-ip>:3000
```

Login:

```
admin / admin
```

---

### 2. Navigate to Data Sources

* Open menu (☰)
* Go to **Connections → Data Sources**
* Click **Add data source**

---

### 3. Select Loki

* Search for **Loki**
* Click the **Loki** data source

---

### 4. Configure Loki

Set the following:

```yaml
Name: Loki
URL: http://loki:3100
```

> If running outside Docker, use:

```
http://localhost:3100
```

---

### 5. Save & Test

Click:

```
Save & Test
```

Expected result:

```
Data source connected successfully
```

---

## 🔍 Verify Logs

Go to:

```
Explore → Select Loki
```

Try a basic query:

```logql
{job="mikrotik"}
```

If logs appear → everything is working ✅

---

## ⚠️ Common Issues

* ❌ Wrong URL → use `loki:3100` (Docker network)
* ❌ No logs → check Promtail config
* ❌ Connection failed → verify containers are running:

```bash
docker ps
```


### 3. Configure MikroTik

Follow:

```
mikrotik_setup.md
```

Example (Syslog config):

```bash
/system logging action add name=remote target=remote remote=YOUR_SERVER_IP
/system logging add topics=info action=remote
```

---

### 4. Access Grafana

```
http://<your-server-ip>:3000
```

Default login:

```
admin / admin
```

---

## 🤖 AI Troubleshooting Workflow

1. Export MikroTik config:

```bash
/export file=config
```

2. Paste into:

```
mikrotik_config_export.txt
```

3. Use prompts from:

```
ai_troubleshooting_skills.md
```

4. Analyze issues using AI tools like ChatGPT or Claude

---

## 📊 Example Use Cases

* 🔴 BGP session flapping detection
* 🔥 Firewall drop analysis
* 👤 PPPoE authentication issues
* ⚠️ System instability troubleshooting

---

## 🔍 Sample LogQL Queries

Check:

```
logql_queries.md
```

Includes:

* BGP state monitoring
* Login tracking
* Firewall drops

---

## 📁 Project Structure

```
.
├── docker-compose.yml
├── promtail-config.yaml
├── run.sh
├── mikrotik_setup.md
├── logql_queries.md
├── ai_troubleshooting_skills.md
└── ubuntu_installation.md
```

---

## 🔒 Security Notes

* Never upload real MikroTik configs to public repos
* Sensitive files are excluded via `.gitignore`
* Use private repos for production environments

---

## 🛣️ Roadmap

* [ ] Pre-built Grafana dashboards export
* [ ] Alerting integration (Slack/Telegram)
* [ ] AI auto-analysis pipeline
* [ ] Multi-tenant support

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## 📜 License

Add a license (MIT recommended)

---

## ⭐ Support

If this project helps, consider giving it a star ⭐

---

Built for network engineers who want **visibility + automation + intelligence** in one stack.
