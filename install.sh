#!/bin/bash

###############################################################################
# ServerCraft Automated Installation Script
# This script installs and configures ServerCraft Game Server Panel
# Supports: Ubuntu 20.04+, Debian 11+, CentOS 8+
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVERCRAFT_DIR="/opt/servercraft"
LOG_FILE="/var/log/servercraft-install.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root. Use: sudo bash install.sh"
    fi
}

# Detect OS
detect_os() {
    log "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        error "Cannot detect OS. /etc/os-release not found"
    fi
    
    log "Detected OS: $OS $VERSION"
    
    case $OS in
        ubuntu|debian)
            PACKAGE_MANAGER="apt"
            ;;
        centos|rhel|fedora)
            PACKAGE_MANAGER="yum"
            ;;
        *)
            warning "Unsupported OS: $OS. Proceeding with apt..."
            PACKAGE_MANAGER="apt"
            ;;
    esac
}

# Update system
update_system() {
    log "Updating system packages..."
    
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt update -y >> "$LOG_FILE" 2>&1
        apt upgrade -y >> "$LOG_FILE" 2>&1
    else
        yum update -y >> "$LOG_FILE" 2>&1
    fi
    
    log "System updated successfully"
}

# Install dependencies
install_dependencies() {
    log "Installing required dependencies..."
    
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y curl wget git ufw openssl >> "$LOG_FILE" 2>&1
    else
        yum install -y curl wget git firewalld openssl >> "$LOG_FILE" 2>&1
    fi
    
    log "Dependencies installed successfully"
}

# Install Docker
install_docker() {
    log "Checking Docker installation..."
    
    if command -v docker &> /dev/null; then
        log "Docker already installed: $(docker --version)"
        return
    fi
    
    log "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh >> "$LOG_FILE" 2>&1
    sh get-docker.sh >> "$LOG_FILE" 2>&1
    rm get-docker.sh
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    log "Docker installed successfully: $(docker --version)"
}

# Install Docker Compose
install_docker_compose() {
    log "Checking Docker Compose installation..."
    
    if command -v docker-compose &> /dev/null; then
        log "Docker Compose already installed: $(docker-compose --version)"
        return
    fi
    
    log "Installing Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose >> "$LOG_FILE" 2>&1
    chmod +x /usr/local/bin/docker-compose
    
    log "Docker Compose installed successfully: $(docker-compose --version)"
}

# Clone ServerCraft repository
clone_repository() {
    log "Setting up ServerCraft..."
    
    if [ -d "$SERVERCRAFT_DIR" ]; then
        warning "ServerCraft directory already exists. Backing up..."
        mv "$SERVERCRAFT_DIR" "${SERVERCRAFT_DIR}.backup.$(date +%s)"
    fi
    
    mkdir -p "$SERVERCRAFT_DIR"
    cd "$SERVERCRAFT_DIR"
    
    DEFAULT_REPO_URL="https://github.com/OfficialMikeJ/ServerCraft.git"
    
    if [ -n "$REPO_URL" ]; then
        info "Using repository from environment: $REPO_URL"
    elif [ -t 0 ]; then
        echo ""
        info "Repository Configuration"
        read -p "Enter ServerCraft repository URL (default: ${DEFAULT_REPO_URL}): " REPO_URL
        REPO_URL=${REPO_URL:-$DEFAULT_REPO_URL}
    else
        warning "Non-interactive mode - using default repository"
        REPO_URL=$DEFAULT_REPO_URL
    fi
    
    log "Cloning repository: $REPO_URL"
    git clone "$REPO_URL" . >> "$LOG_FILE" 2>&1 || error "Failed to clone repository"
    log "Repository cloned successfully"
}

# Configure environment
configure_environment() {
    log "Configuring environment variables..."
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Get domain name
    echo ""
    info "Domain Configuration"
    
    if [ -t 0 ]; then
        read -p "Enter your domain name (e.g., panel.yourdomain.com): " DOMAIN_NAME
        read -p "Is this a static IP? (yes/no): " IS_STATIC
    else
        warning "Non-interactive mode - using defaults"
        DOMAIN_NAME=${DOMAIN_NAME:-"panel.localhost"}
        IS_STATIC=${IS_STATIC:-"no"}
    fi
    
    # Create directories if they don't exist
    mkdir -p "$SERVERCRAFT_DIR/backend"
    mkdir -p "$SERVERCRAFT_DIR/frontend"
    
    # Backend .env
    cat > "$SERVERCRAFT_DIR/backend/.env" << EOF
MONGO_URL=mongodb://mongo:27017
DB_NAME=servercraft
CORS_ORIGINS=https://${DOMAIN_NAME},https://www.${DOMAIN_NAME}
JWT_SECRET_KEY=${JWT_SECRET}
EOF
    
    # Frontend .env
    cat > "$SERVERCRAFT_DIR/frontend/.env" << EOF
REACT_APP_BACKEND_URL=https://${DOMAIN_NAME}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
    
    log "Environment configured successfully"
    log "JWT Secret generated and saved"
    log "Domain configured: ${DOMAIN_NAME}"
}

# Setup SSL/Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificates with Let's Encrypt..."
    
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1
    else
        yum install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1
    fi
    
    if [ "$IS_STATIC" = "yes" ]; then
        info "Static IP detected. Obtaining Let's Encrypt SSL certificate..."
        certbot certonly --standalone -d "$DOMAIN_NAME" --non-interactive --agree-tos \
            --email "admin@${DOMAIN_NAME}" >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            # Setup auto-renewal
            (crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet") | crontab -
            log "Let's Encrypt SSL certificate obtained and auto-renewal configured"
        else
            warning "SSL certificate generation failed. You can run 'sudo certbot certonly --standalone -d $DOMAIN_NAME' manually later."
        fi
    else
        info "Dynamic IP detected. Configuring Let's Encrypt with Dynamic DNS..."
        echo ""
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║     Let's Encrypt Setup for Dynamic IP                   ║"
        echo "╚══════════════════════════════════════════════════════════╝"
        echo ""
        echo "Choose your Dynamic DNS provider for Let's Encrypt SSL:"
        echo ""
        echo "1. DuckDNS (Free, Easy Setup)"
        echo "   - Free subdomain (yourname.duckdns.org)"
        echo "   - Automatic IP updates"
        echo "   - Let's Encrypt SSL support"
        echo ""
        echo "2. Cloudflare (Free with API)"
        echo "   - Use your own domain"
        echo "   - Automatic IP updates via API"
        echo "   - Free SSL with Cloudflare proxy"
        echo ""
        echo "3. Skip SSL Setup (Configure manually later)"
        echo ""
        
        if [ -t 0 ]; then
            read -p "Enter choice (1, 2, or 3): " DNS_CHOICE
        else
            warning "Non-interactive mode - skipping SSL setup"
            DNS_CHOICE="3"
        fi
        
        case $DNS_CHOICE in
            1)
                setup_duckdns
                ;;
            2)
                setup_cloudflare
                ;;
            3)
                warning "SSL setup skipped. You can configure it manually later."
                info "See: https://letsencrypt.org/docs/ for manual setup"
                ;;
            *)
                warning "Invalid choice. Skipping SSL setup."
                ;;
        esac
    fi
}

# Setup DuckDNS with Let's Encrypt
setup_duckdns() {
    log "Setting up DuckDNS with Let's Encrypt..."
    
    echo ""
    info "DuckDNS Setup"
    echo "1. Sign up at https://www.duckdns.org (free)"
    echo "2. Create a subdomain (e.g., myserver)"
    echo "3. Get your token from DuckDNS dashboard"
    echo ""
    
    if [ -t 0 ]; then
        read -p "Enter your DuckDNS subdomain (without .duckdns.org): " DUCK_SUBDOMAIN
        read -p "Enter your DuckDNS token: " DUCK_TOKEN
    else
        error "Non-interactive mode requires DUCK_SUBDOMAIN and DUCK_TOKEN environment variables"
    fi
    
    # Create DuckDNS update script
    mkdir -p /root/duckdns
    cat > /root/duckdns/duck.sh << EOF
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=${DUCK_SUBDOMAIN}&token=${DUCK_TOKEN}&ip=" | curl -k -o /root/duckdns/duck.log -K -
EOF
    
    chmod +x /root/duckdns/duck.sh
    
    # Test DuckDNS
    log "Testing DuckDNS connection..."
    /root/duckdns/duck.sh
    sleep 2
    
    if grep -q "OK" /root/duckdns/duck.log; then
        log "DuckDNS configured successfully!"
    else
        error "DuckDNS test failed. Please check your subdomain and token. Log: $(cat /root/duckdns/duck.log)"
    fi
    
    # Add to crontab for automatic IP updates every 5 minutes
    (crontab -l 2>/dev/null | grep -v duckdns; echo "*/5 * * * * /root/duckdns/duck.sh >/dev/null 2>&1") | crontab -
    log "DuckDNS auto-update configured (every 5 minutes)"
    
    # Update domain name to DuckDNS domain
    DOMAIN_NAME="${DUCK_SUBDOMAIN}.duckdns.org"
    
    # Update environment files with new domain
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://${DOMAIN_NAME}|g" "$SERVERCRAFT_DIR/backend/.env"
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://${DOMAIN_NAME}|g" "$SERVERCRAFT_DIR/frontend/.env"
    
    # Wait for DNS propagation
    log "Waiting for DNS propagation (30 seconds)..."
    sleep 30
    
    # Obtain Let's Encrypt SSL certificate
    log "Obtaining Let's Encrypt SSL certificate for ${DOMAIN_NAME}..."
    certbot certonly --standalone -d "${DOMAIN_NAME}" \
        --non-interactive --agree-tos --email "admin@${DOMAIN_NAME}" \
        --preferred-challenges http >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "Let's Encrypt SSL certificate obtained successfully!"
        
        # Setup renewal with DuckDNS update
        cat > /etc/letsencrypt/renewal-hooks/pre/duckdns-update.sh << 'EOF'
#!/bin/bash
/root/duckdns/duck.sh
sleep 10
EOF
        chmod +x /etc/letsencrypt/renewal-hooks/pre/duckdns-update.sh
        
        # Add certbot renewal to crontab
        (crontab -l 2>/dev/null | grep -v "certbot renew"; echo "0 0,12 * * * certbot renew --quiet") | crontab -
        
        log "SSL auto-renewal configured with DuckDNS IP updates"
    else
        warning "Let's Encrypt certificate generation failed. Check logs at $LOG_FILE"
        warning "You can retry manually with: sudo certbot certonly --standalone -d ${DOMAIN_NAME}"
    fi
}

# Setup Cloudflare with Let's Encrypt
setup_cloudflare() {
    log "Setting up Cloudflare with Let's Encrypt..."
    
    echo ""
    info "Cloudflare Setup"
    echo "1. Add your domain to Cloudflare (free account)"
    echo "2. Get your API key: My Profile -> API Tokens -> Global API Key"
    echo "3. Get Zone ID: Dashboard -> Select domain -> Zone ID (right sidebar)"
    echo ""
    
    if [ -t 0 ]; then
        read -p "Enter your Cloudflare email: " CF_EMAIL
        read -p "Enter your Cloudflare Global API Key: " CF_API_KEY
        read -p "Enter your Zone ID: " CF_ZONE_ID
        read -p "Enter your full domain (e.g., panel.yourdomain.com): " CF_DOMAIN
    else
        error "Non-interactive mode requires CF_EMAIL, CF_API_KEY, CF_ZONE_ID, CF_DOMAIN environment variables"
    fi
    
    # Install Cloudflare DNS plugin
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y python3-certbot-dns-cloudflare >> "$LOG_FILE" 2>&1
    else
        yum install -y python3-certbot-dns-cloudflare >> "$LOG_FILE" 2>&1
    fi
    
    # Create Cloudflare credentials file
    mkdir -p /root/.secrets
    cat > /root/.secrets/cloudflare.ini << EOF
dns_cloudflare_email = ${CF_EMAIL}
dns_cloudflare_api_key = ${CF_API_KEY}
EOF
    chmod 600 /root/.secrets/cloudflare.ini
    
    # Update domain name
    DOMAIN_NAME="${CF_DOMAIN}"
    
    # Update environment files
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://${DOMAIN_NAME}|g" "$SERVERCRAFT_DIR/backend/.env"
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://${DOMAIN_NAME}|g" "$SERVERCRAFT_DIR/frontend/.env"
    
    # Obtain Let's Encrypt certificate using Cloudflare DNS
    log "Obtaining Let's Encrypt SSL certificate via Cloudflare DNS..."
    certbot certonly --dns-cloudflare \
        --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
        -d "$DOMAIN_NAME" \
        --non-interactive --agree-tos --email "$CF_EMAIL" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "Let's Encrypt SSL certificate obtained successfully!"
        
        # Setup auto-renewal
        (crontab -l 2>/dev/null | grep -v "certbot renew"; echo "0 0,12 * * * certbot renew --quiet") | crontab -
        
        log "SSL auto-renewal configured"
        info "Note: With Cloudflare proxy enabled (orange cloud), you also get Cloudflare's SSL"
    else
        warning "Let's Encrypt certificate generation failed. Check logs at $LOG_FILE"
        info "Alternative: Enable Cloudflare proxy (orange cloud) for free SSL without certbot"
    fi
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw --force enable >> "$LOG_FILE" 2>&1
        ufw allow 22/tcp >> "$LOG_FILE" 2>&1  # SSH
        ufw allow 80/tcp >> "$LOG_FILE" 2>&1  # HTTP
        ufw allow 443/tcp >> "$LOG_FILE" 2>&1 # HTTPS
        ufw allow 27015:27100/tcp >> "$LOG_FILE" 2>&1  # Game servers
        ufw allow 27015:27100/udp >> "$LOG_FILE" 2>&1  # Game servers UDP
        log "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        systemctl start firewalld
        systemctl enable firewalld
        firewall-cmd --permanent --add-port=22/tcp >> "$LOG_FILE" 2>&1
        firewall-cmd --permanent --add-port=80/tcp >> "$LOG_FILE" 2>&1
        firewall-cmd --permanent --add-port=443/tcp >> "$LOG_FILE" 2>&1
        firewall-cmd --permanent --add-port=27015-27100/tcp >> "$LOG_FILE" 2>&1
        firewall-cmd --permanent --add-port=27015-27100/udp >> "$LOG_FILE" 2>&1
        firewall-cmd --reload >> "$LOG_FILE" 2>&1
        log "Firewalld configured"
    else
        warning "No firewall detected. Please configure manually"
    fi
}

# Start ServerCraft
start_servercraft() {
    log "Starting ServerCraft..."
    
    cd "$SERVERCRAFT_DIR"
    
    # Try docker-compose (older) or docker compose (newer)
    if docker-compose up -d >> "$LOG_FILE" 2>&1; then
        log "ServerCraft started with docker-compose"
    elif docker compose up -d >> "$LOG_FILE" 2>&1; then
        log "ServerCraft started with docker compose"
    else
        error "Failed to start ServerCraft. Check logs at $LOG_FILE"
    fi
    
    log "ServerCraft started successfully"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > /etc/systemd/system/servercraft.service << EOF
[Unit]
Description=ServerCraft Game Server Panel
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${SERVERCRAFT_DIR}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable servercraft.service
    
    log "Systemd service created and enabled"
}

# Print summary
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          ServerCraft Installation Complete!              ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    log "Installation completed successfully!"
    echo ""
    info "Access your panel at: https://${DOMAIN_NAME}"
    echo ""
    echo "Important Information:"
    echo "  • Installation directory: $SERVERCRAFT_DIR"
    echo "  • Log file: $LOG_FILE"
    echo "  • JWT Secret: (saved in backend/.env)"
    if [ "$IS_STATIC" = "yes" ]; then
        echo "  • SSL Certificates: /etc/letsencrypt/live/"
    else
        echo "  • SSL: Not configured (dynamic IP - configure manually)"
    fi
    echo ""
    echo "Next Steps:"
    echo "  1. Open your browser to https://${DOMAIN_NAME}"
    echo "  2. Register an admin account"
    echo "  3. Add your first server node"
    echo "  4. Create a game server"
    echo ""
    echo "Commands:"
    echo "  • View logs: docker-compose -f ${SERVERCRAFT_DIR}/docker-compose.yml logs -f"
    echo "  • Restart: systemctl restart servercraft"
    echo "  • Stop: systemctl stop servercraft"
    echo "  • Status: systemctl status servercraft"
    echo ""
    echo "Support:"
    echo "  • Documentation: https://docs.servercraft.com"
    echo "  • Issues: https://github.com/OfficialMikeJ/ServerCraft/issues"
    echo ""
}

# Main installation flow
main() {
    clear
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║      ServerCraft Automated Installation Script          ║"
    echo "║                                                          ║"
    echo "║  This script will install and configure ServerCraft     ║"
    echo "║  Game Server Management Panel                           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    # Create log file
    touch "$LOG_FILE"
    
    check_root
    detect_os
    update_system
    install_dependencies
    install_docker
    install_docker_compose
    clone_repository
    configure_environment
    setup_ssl
    configure_firewall
    start_servercraft
    create_systemd_service
    print_summary
}

# Run main function
main "$@"
