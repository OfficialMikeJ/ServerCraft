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
        info "Dynamic IP detected. Let's Encrypt setup with Dynamic DNS..."
        echo ""
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║     Let's Encrypt SSL for Dynamic IP                     ║"
        echo "╚══════════════════════════════════════════════════════════╝"
        echo ""
        echo "Choose your Dynamic DNS provider for Let's Encrypt:"
        echo ""
        echo "1. DuckDNS (Free & Easy)"
        echo "   • Free subdomain (yourname.duckdns.org)"
        echo "   • Automatic IP updates every 5 minutes"
        echo "   • Let's Encrypt SSL certificate"
        echo ""
        echo "2. Cloudflare (Your own domain)"
        echo "   • Use your existing domain"
        echo "   • API-based IP updates"
        echo "   • Let's Encrypt + Cloudflare SSL"
        echo ""
        echo "3. Skip (Configure manually later)"
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
                warning "SSL setup skipped. Configure manually later."
                info "See: https://letsencrypt.org/docs/"
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
    echo "═══════════════════════════════════════════════════"
    info "DuckDNS Setup Instructions"
    echo "═══════════════════════════════════════════════════"
    echo "1. Go to: https://www.duckdns.org"
    echo "2. Sign in with any account (Google, GitHub, etc.)"
    echo "3. Create a subdomain (e.g., 'myserver')"
    echo "4. Copy your token from the top of the page"
    echo ""
    
    if [ -t 0 ]; then
        read -p "Enter your DuckDNS subdomain (without .duckdns.org): " DUCK_SUBDOMAIN
        read -p "Enter your DuckDNS token: " DUCK_TOKEN
    else
        error "Non-interactive mode requires DUCK_SUBDOMAIN and DUCK_TOKEN variables"
    fi
    
    # Validate input
    if [ -z "$DUCK_SUBDOMAIN" ] || [ -z "$DUCK_TOKEN" ]; then
        error "DuckDNS subdomain and token are required!"
    fi
    
    # Create DuckDNS update script
    mkdir -p /root/duckdns
    cat > /root/duckdns/duck.sh << EOF
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=${DUCK_SUBDOMAIN}&token=${DUCK_TOKEN}&ip=" | curl -k -o /root/duckdns/duck.log -K -
EOF
    
    chmod +x /root/duckdns/duck.sh
    
    # Test DuckDNS connection
    log "Testing DuckDNS connection..."
    /root/duckdns/duck.sh
    sleep 3
    
    if grep -q "OK" /root/duckdns/duck.log 2>/dev/null; then
        log "✓ DuckDNS configured successfully!"
    else
        error "✗ DuckDNS test failed! Check subdomain and token. Log: $(cat /root/duckdns/duck.log 2>/dev/null || echo 'No log file')"
    fi
    
    # Add to crontab for IP updates every 5 minutes
    (crontab -l 2>/dev/null | grep -v "duckdns"; echo "*/5 * * * * /root/duckdns/duck.sh >/dev/null 2>&1") | crontab -
    log "✓ DuckDNS auto-update scheduled (every 5 minutes)"
    
    # Update domain to DuckDNS
    FULL_DOMAIN="${DUCK_SUBDOMAIN}.duckdns.org"
    log "Your domain: ${FULL_DOMAIN}"
    
    # Update environment files
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://${FULL_DOMAIN}|g" "$SERVERCRAFT_DIR/backend/.env"
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://${FULL_DOMAIN}|g" "$SERVERCRAFT_DIR/frontend/.env"
    
    # Wait for DNS propagation
    log "Waiting for DNS propagation (30 seconds)..."
    sleep 30
    
    # Obtain Let's Encrypt certificate
    log "Obtaining Let's Encrypt SSL certificate for ${FULL_DOMAIN}..."
    certbot certonly --standalone \
        -d "${FULL_DOMAIN}" \
        --non-interactive \
        --agree-tos \
        --email "admin@${FULL_DOMAIN}" \
        --preferred-challenges http \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✓ Let's Encrypt SSL certificate obtained!"
        
        # Create renewal hook to update DuckDNS before renewal
        mkdir -p /etc/letsencrypt/renewal-hooks/pre
        cat > /etc/letsencrypt/renewal-hooks/pre/duckdns-update.sh << 'EOFHOOK'
#!/bin/bash
# Update DuckDNS IP before SSL renewal
/root/duckdns/duck.sh
sleep 10
EOFHOOK
        chmod +x /etc/letsencrypt/renewal-hooks/pre/duckdns-update.sh
        
        # Add certbot renewal (runs twice daily)
        (crontab -l 2>/dev/null | grep -v "certbot renew"; echo "0 0,12 * * * certbot renew --quiet") | crontab -
        
        log "✓ SSL auto-renewal configured (checks twice daily)"
        log "✓ DuckDNS IP update before each renewal configured"
        
        # Update DOMAIN_NAME for final summary
        DOMAIN_NAME="${FULL_DOMAIN}"
    else
        warning "✗ Let's Encrypt certificate failed. Check $LOG_FILE"
        warning "Retry with: sudo certbot certonly --standalone -d ${FULL_DOMAIN}"
    fi
}

# Setup Cloudflare with Let's Encrypt
setup_cloudflare() {
    log "Setting up Cloudflare with Let's Encrypt..."
    
    echo ""
    echo "═══════════════════════════════════════════════════"
    info "Cloudflare Setup Instructions"
    echo "═══════════════════════════════════════════════════"
    echo "1. Add your domain to Cloudflare (free)"
    echo "2. Update nameservers at your domain registrar"
    echo "3. Get API Key: My Profile → API Tokens → Global API Key"
    echo "4. Get Zone ID: Dashboard → Select domain → Zone ID"
    echo ""
    
    if [ -t 0 ]; then
        read -p "Enter your Cloudflare email: " CF_EMAIL
        read -p "Enter your Global API Key: " CF_API_KEY
        read -p "Enter your Zone ID: " CF_ZONE_ID
        read -p "Enter your domain (e.g., panel.example.com): " CF_DOMAIN
    else
        error "Non-interactive mode requires CF_EMAIL, CF_API_KEY, CF_ZONE_ID, CF_DOMAIN variables"
    fi
    
    # Validate input
    if [ -z "$CF_EMAIL" ] || [ -z "$CF_API_KEY" ] || [ -z "$CF_ZONE_ID" ] || [ -z "$CF_DOMAIN" ]; then
        error "All Cloudflare credentials are required!"
    fi
    
    # Install Cloudflare DNS plugin
    log "Installing Cloudflare DNS plugin..."
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt install -y python3-certbot-dns-cloudflare >> "$LOG_FILE" 2>&1
    else
        yum install -y python3-certbot-dns-cloudflare >> "$LOG_FILE" 2>&1
    fi
    
    # Create Cloudflare credentials
    mkdir -p /root/.secrets
    cat > /root/.secrets/cloudflare.ini << EOF
dns_cloudflare_email = ${CF_EMAIL}
dns_cloudflare_api_key = ${CF_API_KEY}
EOF
    chmod 600 /root/.secrets/cloudflare.ini
    log "✓ Cloudflare credentials saved"
    
    # Update environment files
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://${CF_DOMAIN}|g" "$SERVERCRAFT_DIR/backend/.env"
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://${CF_DOMAIN}|g" "$SERVERCRAFT_DIR/frontend/.env"
    
    # Obtain Let's Encrypt certificate via Cloudflare DNS
    log "Obtaining Let's Encrypt SSL via Cloudflare DNS..."
    certbot certonly --dns-cloudflare \
        --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
        -d "$CF_DOMAIN" \
        --non-interactive \
        --agree-tos \
        --email "$CF_EMAIL" \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "✓ Let's Encrypt SSL certificate obtained!"
        
        # Setup auto-renewal
        (crontab -l 2>/dev/null | grep -v "certbot renew"; echo "0 0,12 * * * certbot renew --quiet") | crontab -
        
        log "✓ SSL auto-renewal configured (checks twice daily)"
        info "Tip: Enable Cloudflare proxy (orange cloud) for additional DDoS protection"
        
        # Update DOMAIN_NAME for final summary
        DOMAIN_NAME="${CF_DOMAIN}"
    else
        warning "✗ Let's Encrypt certificate failed. Check $LOG_FILE"
        info "Alternative: Enable Cloudflare proxy for automatic SSL (no certbot needed)"
    fi
}

# Duplicate functions removed - using updated versions above

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
