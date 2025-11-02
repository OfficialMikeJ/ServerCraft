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
    
    info "Please enter your ServerCraft repository URL:"
    read -p "Repository URL (or press Enter for local setup): " REPO_URL
    
    if [ -n "$REPO_URL" ]; then
        git clone "$REPO_URL" . >> "$LOG_FILE" 2>&1
        log "Repository cloned successfully"
    else
        log "Skipping repository clone (local setup)"
    fi
}

# Configure environment
configure_environment() {
    log "Configuring environment variables..."
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    
    # Get domain name
    echo ""
    info "Domain Configuration"
    read -p "Enter your domain name (e.g., panel.yourdomain.com): " DOMAIN_NAME
    read -p "Is this a static IP? (yes/no): " IS_STATIC
    
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
}

# Setup SSL/Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1
    else
        yum install -y certbot python3-certbot-nginx >> "$LOG_FILE" 2>&1
    fi
    
    if [ "$IS_STATIC" = "yes" ]; then
        info "Static IP detected. Obtaining SSL certificate..."
        certbot certonly --standalone -d "$DOMAIN_NAME" --non-interactive --agree-tos \
            --email "admin@${DOMAIN_NAME}" >> "$LOG_FILE" 2>&1
        
        # Setup auto-renewal
        (crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet") | crontab -
        
        log "SSL certificate obtained and auto-renewal configured"
    else
        info "Dynamic IP detected."
        echo ""
        echo "For dynamic IPs, you have two options:"
        echo "1. Use DuckDNS (Free)"
        echo "2. Use Cloudflare (Free with API)"
        read -p "Choose option (1 or 2): " DNS_OPTION
        
        if [ "$DNS_OPTION" = "1" ]; then
            setup_duckdns
        else
            setup_cloudflare
        fi
    fi
}

# Setup DuckDNS
setup_duckdns() {
    log "Setting up DuckDNS..."
    
    read -p "Enter your DuckDNS subdomain (e.g., myserver): " DUCK_SUBDOMAIN
    read -p "Enter your DuckDNS token: " DUCK_TOKEN
    
    # Create DuckDNS update script
    mkdir -p /root/duckdns
    cat > /root/duckdns/duck.sh << EOF
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=${DUCK_SUBDOMAIN}&token=${DUCK_TOKEN}&ip=" | curl -k -o /root/duckdns/duck.log -K -
EOF
    
    chmod +x /root/duckdns/duck.sh
    
    # Test DuckDNS
    /root/duckdns/duck.sh
    if grep -q "OK" /root/duckdns/duck.log; then
        log "DuckDNS configured successfully"
    else
        warning "DuckDNS test failed. Please check your credentials"
    fi
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /root/duckdns/duck.sh >/dev/null 2>&1") | crontab -
    
    # Obtain SSL certificate
    certbot certonly --manual --preferred-challenges dns -d "${DUCK_SUBDOMAIN}.duckdns.org" \
        --non-interactive --agree-tos --email "admin@${DUCK_SUBDOMAIN}.duckdns.org" \
        >> "$LOG_FILE" 2>&1
    
    log "SSL certificate obtained for DuckDNS domain"
}

# Setup Cloudflare
setup_cloudflare() {
    log "Setting up Cloudflare..."
    
    read -p "Enter your Cloudflare API key: " CF_API_KEY
    read -p "Enter your Cloudflare email: " CF_EMAIL
    read -p "Enter your Zone ID: " CF_ZONE_ID
    read -p "Enter your domain record name (e.g., panel.yourdomain.com): " CF_RECORD_NAME
    
    # Create Cloudflare credentials file
    mkdir -p /root/.secrets
    cat > /root/.secrets/cloudflare.ini << EOF
dns_cloudflare_email = ${CF_EMAIL}
dns_cloudflare_api_key = ${CF_API_KEY}
EOF
    
    chmod 600 /root/.secrets/cloudflare.ini
    
    # Install Cloudflare plugin
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y python3-certbot-dns-cloudflare >> "$LOG_FILE" 2>&1
    fi
    
    # Obtain SSL certificate
    certbot certonly --dns-cloudflare \
        --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
        -d "$CF_RECORD_NAME" \
        --non-interactive --agree-tos --email "$CF_EMAIL" \
        >> "$LOG_FILE" 2>&1
    
    log "SSL certificate obtained via Cloudflare"
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
    docker-compose up -d >> "$LOG_FILE" 2>&1
    
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
    echo "  • SSL Certificates: /etc/letsencrypt/live/"
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
    echo "  • Issues: https://github.com/yourusername/servercraft/issues"
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
