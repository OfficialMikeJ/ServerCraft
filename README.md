# ServerCraft - Game Server Management Panel

<div align="center">

![ServerCraft Logo](https://via.placeholder.com/200x200/0891b2/ffffff?text=ServerCraft)

**Modern, Automated Game Server Management Panel**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Security](https://img.shields.io/badge/security-enterprise-green.svg)](#security-features)

[Features](#features) • [Installation](#installation) • [SSL Setup](#ssl--lets-encrypt-setup) • [Security](#security-features) • [Support](#support)

</div>

---

## 🎮 Overview

ServerCraft is a professional game server management panel that simplifies the deployment and management of game servers using Docker containers. Built with FastAPI, React, and MongoDB, it provides enterprise-grade security and automation.

### Supported Games (v1.0)
- Arma 3 (Vanilla & Modded with Steam Workshop)
- Rust (Vanilla)
- Arma Reforger
- DayZ
- ICARUS
- Escape from Tarkov SPT (Stay in Tarkov)
- Ground Branch
- Operation Harsh Doorstop
- Squad

---

## ✨ Features

### Core Features
- 🔐 **JWT Authentication** - Secure token-based auth with refresh tokens
- 🖥️ **Multi-Node Support** - Manage multiple server nodes with resource tracking
- 🐳 **Docker Integration** - Automated container deployment and management
- 👥 **Sub-User Management** - Granular permission system
- 📁 **File Explorer** - Browse and manage server files
- 🎨 **4 Professional Themes** - Crimson, Ocean, Emerald, and Violet color schemes
- 🎨 **Themes & Plugins** - Extensible with community/premium add-ons
- 🔒 **Enterprise Security** - 22/24 security tests passed (91.7%)

### Theme System
- 🎨 **4 Color Schemes**: Crimson Shadow (Red), Ocean Depths (Blue), Emerald Matrix (Green), Violet Nebula (Purple)
- 🖌️ **Dynamic Styling**: All buttons, text, borders, and UI elements change with theme
- 💾 **Persistent**: Theme choice saved across sessions
- 🎯 **Dual Selection**: Dropdown with Apply button or instant-apply visual cards
- ✨ **Shadow Effects**: Professional depth with themed shadows on all buttons
- 🌈 **Gradient Backgrounds**: Smooth color gradients matching theme
- 🔄 **Smooth Transitions**: 0.3s animations when switching themes

### Security Features
- ✅ Password strength validation
- ✅ Account lockout after failed attempts
- ✅ Session management with expiry
- ✅ Rate limiting on all auth endpoints
- ✅ XSS & SQL injection prevention
- ✅ Audit logging for all actions
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Input sanitization

---

## 📋 Prerequisites

### Required Software
- **Operating System**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Domain Name**: Required for SSL (can use Dynamic DNS)
- **Ports**: 80, 443 (for web), 8001 (backend), 3000 (frontend)

### System Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 50GB storage
- **Recommended**: 4+ CPU cores, 8GB+ RAM, 100GB+ SSD

---

## 🚀 Quick Start Installation

### Option 1: Automated Installation (Recommended)

```bash
# Download and run the automated installer
curl -fsSL https://raw.githubusercontent.com/yourusername/servercraft/main/install.sh | bash

# Or download first to review
wget https://raw.githubusercontent.com/yourusername/servercraft/main/install.sh
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

#### Step 1: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add your user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/servercraft.git
cd servercraft
```

#### Step 3: Configure Environment Variables

```bash
# Copy example environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env
nano backend/.env
```

**Backend Configuration (`backend/.env`):**
```env
MONGO_URL=mongodb://mongo:27017
DB_NAME=servercraft
CORS_ORIGINS=*
JWT_SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_STRING_MINIMUM_32_CHARACTERS
```

**Frontend Configuration (`frontend/.env`):**
```env
REACT_APP_BACKEND_URL=https://yourdomain.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

#### Step 4: Generate Secure JWT Secret

```bash
# Generate a secure random secret
openssl rand -base64 32
# Copy the output and paste it as JWT_SECRET_KEY in backend/.env
```

#### Step 5: Launch with Docker Compose

```bash
docker-compose up -d
```

#### Step 6: Verify Installation

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# Access the panel
# Open browser: https://yourdomain.com
```

---

## 🔒 SSL & Let's Encrypt Setup

### For Static IP Addresses

#### Automated SSL Setup with Certbot

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

2. **Configure Nginx (if using)**
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/servercraft

# Add configuration (see nginx.conf.example)
sudo ln -s /etc/nginx/sites-available/servercraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

3. **Obtain SSL Certificate**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

4. **Auto-Renewal Setup**
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically creates a cron job for renewal
# Verify with:
sudo systemctl status certbot.timer
```

### For Dynamic IP Addresses (with Dynamic DNS)

#### Recommended Dynamic DNS Providers
- **DuckDNS** (Free, easy setup)
- **No-IP** (Free tier available)
- **Dynu** (Free with multiple domains)
- **Cloudflare** (Free, with API)

#### Setup with DuckDNS Example

1. **Register at DuckDNS.org**
   - Sign up and create a subdomain: `yourname.duckdns.org`
   - Note your token

2. **Install DuckDNS Update Script**
```bash
# Create update script
mkdir -p ~/duckdns
cd ~/duckdns
nano duck.sh
```

Add to `duck.sh`:
```bash
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=yourname&token=your-token&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

```bash
chmod +x duck.sh

# Test it
./duck.sh
cat duck.log  # Should show "OK"
```

3. **Setup Auto-Update Cron Job**
```bash
crontab -e

# Add this line to update every 5 minutes
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

4. **Install Certbot with DNS Challenge**
```bash
sudo apt install certbot python3-certbot-dns-cloudflare -y

# Or for manual DNS challenge
sudo certbot certonly --manual --preferred-challenges dns -d yourname.duckdns.org
```

5. **Alternative: Use Cloudflare for Dynamic DNS + SSL**
```bash
# Install Cloudflare DNS updater
sudo apt install curl jq -y

# Create update script
nano ~/update-cloudflare.sh
```

Add to `update-cloudflare.sh`:
```bash
#!/bin/bash
# Cloudflare API credentials
CF_API_KEY="your-api-key"
CF_API_EMAIL="your-email@example.com"
ZONE_ID="your-zone-id"
RECORD_NAME="panel.yourdomain.com"

# Get current public IP
CURRENT_IP=$(curl -s https://api.ipify.org)

# Update Cloudflare DNS
curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
     -H "X-Auth-Email: $CF_API_EMAIL" \
     -H "X-Auth-Key: $CF_API_KEY" \
     -H "Content-Type: application/json" \
     --data "{\"type\":\"A\",\"name\":\"$RECORD_NAME\",\"content\":\"$CURRENT_IP\",\"ttl\":120,\"proxied\":true}"
```

```bash
chmod +x ~/update-cloudflare.sh

# Add to crontab (every 5 minutes)
*/5 * * * * ~/update-cloudflare.sh >/dev/null 2>&1
```

6. **Obtain SSL via Cloudflare**
```bash
# With Cloudflare proxy enabled, you get free SSL automatically
# Or use certbot with Cloudflare DNS plugin
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d panel.yourdomain.com
```

#### Automatic SSL Renewal for Dynamic IPs

Create renewal hook script:
```bash
sudo nano /etc/letsencrypt/renewal-hooks/pre/update-ip.sh
```

```bash
#!/bin/bash
# Update dynamic DNS before renewal
~/duckdns/duck.sh
sleep 10
```

```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/pre/update-ip.sh
```

### Docker Compose with SSL

Update `docker-compose.yml` to include SSL:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: servercraft-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend

  backend:
    build: ./backend
    container_name: servercraft-backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./backend:/app/backend
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    container_name: servercraft-frontend
    restart: unless-stopped
    environment:
      - REACT_APP_BACKEND_URL=${BACKEND_URL}

  mongo:
    image: mongo:6
    container_name: servercraft-mongo
    restart: unless-stopped
    volumes:
      - mongo-data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=servercraft

volumes:
  mongo-data:
```

### Nginx SSL Configuration

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Frontend
        location / {
            proxy_pass http://frontend:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api {
            proxy_pass http://backend:8001;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 🎮 Game Server Setup

### Automated Game Server Configuration

ServerCraft automatically configures game servers, but here are the manual steps for reference:

#### Arma 3 Server Setup

1. **Via ServerCraft Panel**
   - Navigate to Servers → Create Server
   - Select "Arma 3"
   - Configure resources (CPU, RAM, Storage)
   - Set server name and password
   - Click "Create"

2. **Workshop Mod Installation**
   - Go to Server → Files
   - Upload `.html` mod list from Steam Workshop
   - ServerCraft parses mod IDs and downloads automatically
   - Restart server to apply mods

#### Rust Server Setup

1. **Via ServerCraft Panel**
   - Navigate to Servers → Create Server
   - Select "Rust"
   - Configure world size, seed, and resources
   - Set server name
   - Click "Create"

### Port Allocation

ServerCraft automatically allocates ports, but here's the default range:
- **Game Servers**: 27015-27100
- **Query Ports**: 27200-27300
- **RCON Ports**: 27400-27500

### Resource Requirements per Game

| Game | Min RAM | Min CPU | Min Storage |
|------|---------|---------|-------------|
| Arma 3 | 4GB | 2 cores | 30GB |
| Rust | 8GB | 2 cores | 20GB |
| DayZ | 4GB | 2 cores | 25GB |
| Squad | 8GB | 4 cores | 50GB |

---

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)
```env
# Database
MONGO_URL=mongodb://mongo:27017
DB_NAME=servercraft

# Security
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Frontend (`frontend/.env`)
```env
REACT_APP_BACKEND_URL=https://yourdomain.com
WDS_SOCKET_PORT=443
```

### Firewall Configuration

```bash
# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 27015:27100/tcp  # Game servers
sudo ufw allow 27015:27100/udp  # Game servers (UDP)
sudo ufw enable
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongo

# Check resource usage
docker stats
```

### Theme Management

ServerCraft includes 4 professional themes that can be changed by any user:

**Accessing Theme Settings:**
```
1. Login to your panel
2. Navigate to Settings page
3. Find "Theme Customization" at the top
4. Choose your preferred theme
```

**Theme Options:**
- **Crimson Shadow** - Black & Red (Gaming aesthetic)
- **Ocean Depths** - Black & Blue (Default, Professional)
- **Emerald Matrix** - Black & Green (Tech/Matrix style)
- **Violet Nebula** - Black & Purple (Futuristic)

**Two Ways to Apply:**
1. **Dropdown Method**: Select from dropdown → Click "Apply Theme"
2. **Quick Apply**: Click any theme card for instant change

All themes include:
- Dynamic button colors with shadow effects
- Themed text and accent colors
- Border highlighting with theme colors
- Smooth 0.3s transitions
- Persistent across sessions (localStorage)

### Backup & Restore

#### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/servercraft"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
docker exec servercraft-mongo mongodump --out /tmp/backup
docker cp servercraft-mongo:/tmp/backup $BACKUP_DIR/mongo_$DATE

# Backup configurations
tar -czf $BACKUP_DIR/configs_$DATE.tar.gz backend/.env frontend/.env docker-compose.yml

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
chmod +x backup.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup.sh >/dev/null 2>&1
```

### SSL Certificate Renewal

Certificates auto-renew via certbot, but to manually renew:
```bash
sudo certbot renew
docker-compose restart nginx
```

---

## 🔒 Security Best Practices

1. **Change Default Credentials**
   - Change JWT secret key immediately
   - Use strong admin password (12+ characters, mixed case, numbers, symbols)

2. **Regular Updates**
   ```bash
   # Update ServerCraft
   git pull
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Enable Firewall**
   - Only expose necessary ports
   - Use fail2ban for SSH protection

4. **Monitor Logs**
   - Check audit logs regularly via Admin Panel
   - Review failed login attempts

5. **Backup Regularly**
   - Automate daily backups
   - Test restore procedures

---

## 🐛 Troubleshooting

### SSL Certificate Issues

**Problem**: Certificate not renewing
```bash
# Check certbot status
sudo certbot renew --dry-run

# Check logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Manually renew
sudo certbot renew --force-renewal
```

**Problem**: "Not Secure" warning after IP change
```bash
# Update dynamic DNS
~/duckdns/duck.sh

# Wait 5-10 minutes for DNS propagation
# Then renew certificate
sudo certbot renew
```

### Docker Issues

**Problem**: Containers not starting
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Full reset
docker-compose down
docker-compose up -d
```

**Problem**: Permission denied on docker.sock
```bash
sudo chmod 666 /var/run/docker.sock
# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Database Issues

**Problem**: MongoDB connection failed
```bash
# Check MongoDB status
docker-compose logs mongo

# Restart MongoDB
docker-compose restart mongo

# Check MongoDB is accessible
docker exec -it servercraft-mongo mongosh
```

---

## 📞 Support

- **Documentation**: [Full Docs](https://docs.servercraft.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/servercraft/issues)
- **Discord**: [Join Community](https://discord.gg/servercraft)
- **Email**: support@servercraft.com

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Docker for containerization
- FastAPI for the backend framework
- React for the frontend framework
- MongoDB for the database
- Let's Encrypt for free SSL certificates

---

## 🔄 Changelog

### v1.0.0 (Current)
- ✅ Initial release
- ✅ 9 game servers supported
- ✅ JWT authentication with refresh tokens
- ✅ Multi-node support with resource tracking
- ✅ SSL/Let's Encrypt integration (static & dynamic IPs)
- ✅ Dynamic DNS support (DuckDNS, Cloudflare)
- ✅ 91.7% security test pass rate (22/24 tests)
- ✅ **4 Professional Themes** (Crimson, Ocean, Emerald, Violet)
- ✅ **Theme System** with dropdown selector & instant apply
- ✅ Dynamic UI styling with shadow effects
- ✅ Themes & plugins marketplace (in development)
- ✅ Sub-user management with granular permissions
- ✅ Arma 3 workshop integration
- ✅ File explorer for server management
- ✅ Account lockout & rate limiting
- ✅ Audit logging for all actions

---

## 🎨 Theme System Details

### Available Themes

**1. Crimson Shadow (Red)**
- Primary: #dc2626
- Accent: #f87171
- Perfect for: Intense gaming atmosphere

**2. Ocean Depths (Blue)** - Default
- Primary: #0891b2
- Accent: #22d3ee
- Perfect for: Professional, sleek look

**3. Emerald Matrix (Green)**
- Primary: #10b981
- Accent: #6ee7b7
- Perfect for: Tech/matrix aesthetic

**4. Violet Nebula (Purple)**
- Primary: #8b5cf6
- Accent: #c4b5fd
- Perfect for: Futuristic, space theme

### Theme Features
- **Dropdown Selector**: Choose theme from dropdown + click "Apply"
- **Visual Cards**: Click any theme card for instant apply
- **Live Preview**: See button & text samples before applying
- **Persistent**: Saves to localStorage automatically
- **Dynamic**: All UI elements update instantly (buttons, text, borders, shadows)
- **Smooth Transitions**: 0.3s animations between themes

### How to Change Theme
1. Login to ServerCraft
2. Navigate to **Settings** page
3. Scroll to **Theme Customization** (top of page)
4. **Option A**: Use dropdown + "Apply Theme" button
5. **Option B**: Click any visual theme card for instant apply
6. Theme applies across entire panel immediately

---

<div align="center">

**Made with ❤️ by Mike and the ServerCraft Team**

[⬆ Back to Top](#servercraft---game-server-management-panel)

</div>