#!/bin/bash

###############################################################################
# GW2 WvW Builder - Infrastructure Setup Script
# Version: 1.0.0
# Purpose: Setup production infrastructure (systemd, nginx, backups, monitoring)
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "============================================"
    echo "$1"
    echo "============================================"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root for system services
if [ "$EUID" -ne 0 ] && [ "$1" == "--system" ]; then 
    print_error "Please run with sudo for system-wide installation"
    exit 1
fi

PROJECT_ROOT="/home/roddy/GW2_WvWbuilder"

print_header "GW2 WvW Builder - Infrastructure Setup"

###############################################################################
# 1. Setup Backup Script
###############################################################################

print_header "STEP 1: Backup Configuration"

chmod +x "$PROJECT_ROOT/scripts/backup_database.sh"
chmod +x "$PROJECT_ROOT/scripts/monitor_logs.sh"

# Create backups directory
mkdir -p "$PROJECT_ROOT/backups"

print_success "Backup script configured"

# Setup cron job for weekly backup (Sunday 2:00 AM)
print_info "Setting up weekly backup cron job..."

CRON_CMD="0 2 * * 0 $PROJECT_ROOT/scripts/backup_database.sh >> $PROJECT_ROOT/backups/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup_database.sh"; then
    print_info "Cron job already exists, skipping..."
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    print_success "Cron job added: Weekly backup every Sunday at 2:00 AM"
fi

# Test backup script
print_info "Testing backup script..."
if bash "$PROJECT_ROOT/scripts/backup_database.sh"; then
    print_success "Backup script test passed"
else
    print_warning "Backup script test failed (database may not exist yet)"
fi

###############################################################################
# 2. Setup systemd Service (requires sudo)
###############################################################################

print_header "STEP 2: systemd Service Configuration"

if [ "$1" == "--system" ]; then
    print_info "Installing systemd service..."
    
    # Copy service file
    cp "$PROJECT_ROOT/scripts/systemd/gw2-backend.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable gw2-backend.service
    
    print_success "systemd service installed and enabled"
    print_info "To start: sudo systemctl start gw2-backend"
    print_info "To check status: sudo systemctl status gw2-backend"
    print_info "To view logs: sudo journalctl -u gw2-backend -f"
else
    print_warning "systemd service NOT installed (requires --system flag with sudo)"
    print_info "To install: sudo $0 --system"
    print_info "Service file available at: $PROJECT_ROOT/scripts/systemd/gw2-backend.service"
fi

###############################################################################
# 3. Setup Nginx (requires sudo)
###############################################################################

print_header "STEP 3: Nginx Configuration"

if [ "$1" == "--system" ]; then
    print_info "Checking if Nginx is installed..."
    
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx not installed. Install with: sudo apt install nginx"
    else
        print_info "Nginx found"
        
        # Check if config already exists
        if [ -f /etc/nginx/sites-available/gw2-wvwbuilder ]; then
            print_warning "Nginx config already exists, skipping..."
        else
            # Copy nginx config
            cp "$PROJECT_ROOT/scripts/nginx/gw2-wvwbuilder.conf" /etc/nginx/sites-available/
            
            # Create symlink
            ln -sf /etc/nginx/sites-available/gw2-wvwbuilder.conf /etc/nginx/sites-enabled/
            
            print_success "Nginx config installed"
            print_warning "IMPORTANT: Edit /etc/nginx/sites-available/gw2-wvwbuilder.conf"
            print_warning "  - Change 'gw2builder.example.com' to your domain"
            print_warning "  - Update SSL certificate paths"
            
            # Test nginx config
            if nginx -t 2>/dev/null; then
                print_success "Nginx config test passed"
                print_info "To reload: sudo systemctl reload nginx"
            else
                print_error "Nginx config test failed - please fix manually"
            fi
        fi
    fi
else
    print_warning "Nginx config NOT installed (requires --system flag with sudo)"
    print_info "Config file available at: $PROJECT_ROOT/scripts/nginx/gw2-wvwbuilder.conf"
fi

###############################################################################
# 4. Setup SSL/HTTPS with Let's Encrypt
###############################################################################

print_header "STEP 4: SSL/HTTPS Configuration"

if [ "$1" == "--system" ]; then
    if ! command -v certbot &> /dev/null; then
        print_warning "Certbot not installed. Install with:"
        print_info "  sudo apt install certbot python3-certbot-nginx"
    else
        print_info "Certbot found"
        print_info "To get SSL certificate, run:"
        print_info "  sudo certbot --nginx -d your-domain.com"
        print_info "  (Replace your-domain.com with your actual domain)"
    fi
else
    print_warning "SSL setup requires --system flag with sudo"
    print_info "After installing certbot, run:"
    print_info "  sudo certbot --nginx -d your-domain.com"
fi

###############################################################################
# 5. Setup Log Rotation
###############################################################################

print_header "STEP 5: Log Rotation"

if [ "$1" == "--system" ]; then
    print_info "Setting up log rotation..."
    
    cat > /etc/logrotate.d/gw2-wvwbuilder << 'EOF'
/home/roddy/GW2_WvWbuilder/backend.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 roddy roddy
    postrotate
        systemctl reload gw2-backend 2>/dev/null || true
    endscript
}

/var/log/nginx/gw2-builder-*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload nginx 2>/dev/null || true
    endscript
}
EOF
    
    print_success "Log rotation configured (14 days retention)"
else
    print_warning "Log rotation NOT configured (requires --system flag)"
fi

###############################################################################
# 6. Setup Monitoring Aliases
###############################################################################

print_header "STEP 6: Monitoring Commands"

print_info "Adding monitoring aliases to ~/.bashrc..."

# Check if aliases already exist
if ! grep -q "GW2 WvW Builder Aliases" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# GW2 WvW Builder Aliases
alias gw2-logs='~/GW2_WvWbuilder/scripts/monitor_logs.sh'
alias gw2-logs-errors='~/GW2_WvWbuilder/scripts/monitor_logs.sh -e'
alias gw2-backup='~/GW2_WvWbuilder/scripts/backup_database.sh'
alias gw2-status='systemctl status gw2-backend'
alias gw2-restart='sudo systemctl restart gw2-backend'
alias gw2-start='sudo systemctl start gw2-backend'
alias gw2-stop='sudo systemctl stop gw2-backend'
EOF
    
    print_success "Monitoring aliases added to ~/.bashrc"
    print_info "Run 'source ~/.bashrc' to load aliases"
else
    print_info "Monitoring aliases already exist"
fi

###############################################################################
# Summary
###############################################################################

print_header "INSTALLATION SUMMARY"

cat << EOF

✅ Infrastructure Setup Complete!

📋 What was configured:
--------------------
$(if [ "$1" == "--system" ]; then
    echo "✅ Backup script (weekly, Sunday 2:00 AM)"
    echo "✅ systemd service (auto-restart)"
    echo "✅ Nginx reverse proxy"
    echo "✅ Log rotation (14 days)"
    echo "✅ Monitoring aliases"
else
    echo "✅ Backup script (weekly, Sunday 2:00 AM)"
    echo "⚠️  systemd service (needs sudo)"
    echo "⚠️  Nginx reverse proxy (needs sudo)"
    echo "⚠️  Log rotation (needs sudo)"
    echo "✅ Monitoring aliases"
fi)

🔧 Available Commands:
--------------------
gw2-logs              Monitor logs in real-time
gw2-logs-errors       Show only errors
gw2-backup            Run manual backup
$(if [ "$1" == "--system" ]; then
    echo "gw2-status            Check backend status"
    echo "gw2-restart           Restart backend"
    echo "gw2-start             Start backend"
    echo "gw2-stop              Stop backend"
fi)

📁 Important Files:
--------------------
Backend service: /etc/systemd/system/gw2-backend.service
Nginx config: /etc/nginx/sites-available/gw2-wvwbuilder.conf
Backup script: $PROJECT_ROOT/scripts/backup_database.sh
Monitor script: $PROJECT_ROOT/scripts/monitor_logs.sh
Backups dir: $PROJECT_ROOT/backups/

$(if [ "$1" != "--system" ]; then
    echo ""
    echo "⚠️  To install system services (nginx, systemd):"
    echo "   sudo $0 --system"
fi)

🚀 Next Steps:
--------------------
1. Edit Nginx config with your domain name
2. Get SSL certificate: sudo certbot --nginx -d your-domain.com
3. Start backend: sudo systemctl start gw2-backend
4. Check status: systemctl status gw2-backend
5. Monitor logs: gw2-logs

EOF

exit 0
