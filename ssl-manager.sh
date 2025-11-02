#!/bin/bash

###############################################################################
# ServerCraft SSL Certificate Manager
# Handles SSL certificates for both Static and Dynamic IPs
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVERCRAFT_DIR="/opt/servercraft"
LOG_FILE="/var/log/servercraft-ssl.log"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if certbot is installed
check_certbot() {
    if ! command -v certbot &> /dev/null; then
        error "Certbot is not installed. Please install it first."
    fi
}

# Check SSL certificate status
check_certificate() {
    local domain=$1
    log "Checking SSL certificate for $domain..."
    
    if [ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
        local expiry=$(openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$domain/fullchain.pem" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry" +%s)
        local now_epoch=$(date +%s)
        local days_left=$(( ($expiry_epoch - $now_epoch) / 86400 ))
        
        if [ $days_left -lt 30 ]; then
            warning "Certificate expires in $days_left days!"
            return 1
        else
            log "Certificate is valid for $days_left days"
            return 0
        fi
    else
        error "No certificate found for $domain"
        return 1
    fi
}

# Obtain new certificate (Static IP)
obtain_static_certificate() {
    local domain=$1
    local email=$2
    
    log "Obtaining certificate for $domain (Static IP)..."
    
    certbot certonly --standalone \
        -d "$domain" \
        --non-interactive \
        --agree-tos \
        --email "$email" \
        --preferred-challenges http \
        >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "Certificate obtained successfully"
        return 0
    else
        error "Failed to obtain certificate"
        return 1
    fi
}

# Obtain certificate with DNS challenge (Dynamic IP)
obtain_dynamic_certificate() {
    local domain=$1
    local email=$2
    local provider=$3
    
    log "Obtaining certificate for $domain (Dynamic IP via $provider)..."
    
    case $provider in
        duckdns)
            certbot certonly --manual \
                --preferred-challenges dns \
                -d "$domain" \
                --non-interactive \
                --agree-tos \
                --email "$email" \
                >> "$LOG_FILE" 2>&1
            ;;
        cloudflare)
            certbot certonly --dns-cloudflare \
                --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
                -d "$domain" \
                --non-interactive \
                --agree-tos \
                --email "$email" \
                >> "$LOG_FILE" 2>&1
            ;;
        *)
            error "Unsupported DNS provider: $provider"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log "Certificate obtained successfully"
        return 0
    else
        error "Failed to obtain certificate"
        return 1
    fi
}

# Renew certificate
renew_certificate() {
    local domain=$1
    
    log "Renewing certificate for $domain..."
    
    # Update dynamic DNS if applicable
    if [ -f "/root/duckdns/duck.sh" ]; then
        log "Updating DuckDNS..."
        /root/duckdns/duck.sh
        sleep 10
    fi
    
    certbot renew --force-renewal >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "Certificate renewed successfully"
        
        # Reload nginx
        if [ -f "$SERVERCRAFT_DIR/docker-compose.yml" ]; then
            cd "$SERVERCRAFT_DIR"
            docker-compose restart nginx >> "$LOG_FILE" 2>&1
            log "Nginx reloaded"
        fi
        
        return 0
    else
        error "Failed to renew certificate"
        return 1
    fi
}

# Setup auto-renewal cron job
setup_auto_renewal() {
    log "Setting up automatic renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/servercraft-renew-ssl << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/servercraft-ssl-renewal.log"
echo "[$(date)] Starting SSL renewal check" >> "$LOG_FILE"

# Update dynamic DNS if applicable
if [ -f "/root/duckdns/duck.sh" ]; then
    /root/duckdns/duck.sh >> "$LOG_FILE" 2>&1
    sleep 10
fi

# Renew certificates
certbot renew --quiet >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] Certificate check/renewal successful" >> "$LOG_FILE"
    
    # Reload nginx
    if [ -f "/opt/servercraft/docker-compose.yml" ]; then
        cd /opt/servercraft
        docker-compose restart nginx >> "$LOG_FILE" 2>&1
    fi
else
    echo "[$(date)] Certificate renewal failed" >> "$LOG_FILE"
fi
EOF
    
    chmod +x /usr/local/bin/servercraft-renew-ssl
    
    # Add to crontab (daily at 2 AM and 2 PM)
    (crontab -l 2>/dev/null | grep -v servercraft-renew-ssl; echo "0 2,14 * * * /usr/local/bin/servercraft-renew-ssl") | crontab -
    
    log "Auto-renewal configured (runs daily at 2 AM and 2 PM)"
}

# Test SSL configuration
test_ssl() {
    local domain=$1
    
    log "Testing SSL configuration for $domain..."
    
    # Test certificate
    if openssl s_client -connect "$domain:443" -servername "$domain" </dev/null 2>/dev/null | openssl x509 -noout -text &> /dev/null; then
        log "SSL certificate is valid and accessible"
        
        # Test HTTPS connection
        if curl -IsS "https://$domain" &> /dev/null; then
            log "HTTPS connection successful"
            return 0
        else
            warning "HTTPS connection failed"
            return 1
        fi
    else
        warning "SSL certificate test failed"
        return 1
    fi
}

# Backup certificates
backup_certificates() {
    local backup_dir="/root/ssl-backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    log "Backing up SSL certificates..."
    
    mkdir -p "$backup_dir"
    tar -czf "$backup_dir/letsencrypt-$timestamp.tar.gz" /etc/letsencrypt
    
    log "Certificates backed up to $backup_dir/letsencrypt-$timestamp.tar.gz"
    
    # Keep only last 5 backups
    cd "$backup_dir"
    ls -t letsencrypt-*.tar.gz | tail -n +6 | xargs -r rm
}

# Show certificate info
show_certificate_info() {
    local domain=$1
    
    if [ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
        echo ""
        echo "Certificate Information for $domain:"
        echo "======================================"
        openssl x509 -in "/etc/letsencrypt/live/$domain/fullchain.pem" -noout -subject -issuer -dates
        echo ""
    else
        error "No certificate found for $domain"
    fi
}

# Main menu
show_menu() {
    clear
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║        ServerCraft SSL Certificate Manager              ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "1. Check certificate status"
    echo "2. Obtain new certificate (Static IP)"
    echo "3. Obtain new certificate (Dynamic IP)"
    echo "4. Renew certificate"
    echo "5. Setup auto-renewal"
    echo "6. Test SSL configuration"
    echo "7. Backup certificates"
    echo "8. Show certificate info"
    echo "9. Exit"
    echo ""
    read -p "Select option [1-9]: " choice
    
    case $choice in
        1)
            read -p "Enter domain name: " domain
            check_certificate "$domain"
            ;;
        2)
            read -p "Enter domain name: " domain
            read -p "Enter email address: " email
            obtain_static_certificate "$domain" "$email"
            ;;
        3)
            read -p "Enter domain name: " domain
            read -p "Enter email address: " email
            echo "DNS Providers: duckdns, cloudflare"
            read -p "Enter DNS provider: " provider
            obtain_dynamic_certificate "$domain" "$email" "$provider"
            ;;
        4)
            read -p "Enter domain name: " domain
            renew_certificate "$domain"
            ;;
        5)
            setup_auto_renewal
            ;;
        6)
            read -p "Enter domain name: " domain
            test_ssl "$domain"
            ;;
        7)
            backup_certificates
            ;;
        8)
            read -p "Enter domain name: " domain
            show_certificate_info "$domain"
            ;;
        9)
            exit 0
            ;;
        *)
            error "Invalid option"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Main
main() {
    check_certbot
    
    if [ "$1" = "--check" ]; then
        check_certificate "$2"
    elif [ "$1" = "--renew" ]; then
        renew_certificate "$2"
    elif [ "$1" = "--auto-setup" ]; then
        setup_auto_renewal
    else
        show_menu
    fi
}

main "$@"
