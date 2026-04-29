# Ubuntu Installation Guide: MikroTik Logging Stack

Since you are using Ubuntu, follow these steps to install Docker and set up your logging environment.

## 1. Install Docker & Docker Compose
Run the following commands to install the official Docker engine:

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

# Install Docker packages:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## 2. Manage Docker as a non-root user
To avoid using `sudo` for every docker command:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 3. Configure Firewall (UFW)
You must allow the MikroTik router to send logs to port `1514/udp`.
```bash
sudo ufw allow 1514/udp
sudo ufw allow 3000/tcp  # For Grafana Web UI
```

## 4. Launch the Logging Stack
Navigate to your project directory and start the containers:
```bash
cd ~/Desktop/loki
docker compose up -d
```

## 5. Verify Installation
Check if the services are running:
```bash
docker compose ps
```
You should see `loki`, `promtail`, and `grafana` in the "Up" status.

---
> [!IMPORTANT]
> If you encounter a "permission denied" error when reading `promtail-config.yaml`, ensure the file has read permissions: `chmod 644 promtail-config.yaml`.
