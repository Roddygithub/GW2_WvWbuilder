#!/bin/bash
#
# Script: enable_https.sh
# Description: Setup Nginx reverse proxy with HTTPS using Let's Encrypt
# Usage: sudo ./enable_https.sh <domain>
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${1:-gw2builder.example.com}"
EMAIL="admin@${DOMAIN}"
NGINX_CONF="../nginx/gw2_wvw_builder.conf"
NGINX_AVAILABLE="/etc/nginx/sites-available/gw2_wvw_builder.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/gw2_wvw_builder.conf"

echo -e "${GREEN}=== GW2 WvW Builder - HTTPS Setup ===${NC}"
echo -e "Domain: ${YELLOW}${DOMAIN}${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root (use sudo)${NC}"
    exit 1
fi

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Warning: No domain provided, using default: ${DOMAIN}${NC}"
    echo -e "${YELLOW}Usage: sudo ./enable_https.sh your-domain.com${NC}"
    read -p "Continue with default domain? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Install dependencies
echo -e "${GREEN}[1/7] Installing dependencies...${NC}"
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y nginx certbot python3-certbot-nginx
elif command -v pacman &> /dev/null; then
    pacman -Syu --noconfirm nginx certbot certbot-nginx
else
    echo -e "${RED}Error: Unsupported package manager${NC}"
    exit 1
fi

# Step 2: Create certbot webroot
echo -e "${GREEN}[2/7] Creating certbot webroot...${NC}"
mkdir -p /var/www/certbot
chown -R www-data:www-data /var/www/certbot 2>/dev/null || chown -R http:http /var/www/certbot

# Step 3: Copy Nginx configuration
echo -e "${GREEN}[3/7] Installing Nginx configuration...${NC}"
sed "s/gw2builder.example.com/${DOMAIN}/g" "${NGINX_CONF}" > "${NGINX_AVAILABLE}"

# Step 4: Create symlink
echo -e "${GREEN}[4/7] Enabling site...${NC}"
ln -sf "${NGINX_AVAILABLE}" "${NGINX_ENABLED}"

# Step 5: Test Nginx configuration
echo -e "${GREEN}[5/7] Testing Nginx configuration...${NC}"
nginx -t

# Step 6: Reload Nginx
echo -e "${GREEN}[6/7] Reloading Nginx...${NC}"
systemctl reload nginx

# Step 7: Obtain SSL certificate
echo -e "${GREEN}[7/7] Obtaining SSL certificate...${NC}"
echo -e "${YELLOW}Note: Make sure DNS points to this server!${NC}"
read -p "Domain DNS configured? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx \
        -d "${DOMAIN}" \
        --non-interactive \
        --agree-tos \
        --email "${EMAIL}" \
        --redirect \
        --hsts \
        --staple-ocsp
    
    # Test auto-renewal
    echo -e "${GREEN}Testing certificate auto-renewal...${NC}"
    certbot renew --dry-run
    
    echo -e "${GREEN}✅ HTTPS setup complete!${NC}"
    echo -e "${GREEN}Your site is now available at: https://${DOMAIN}${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping certificate generation${NC}"
    echo -e "${YELLOW}Run manually: sudo certbot --nginx -d ${DOMAIN}${NC}"
fi

# Setup auto-renewal cron job
echo -e "${GREEN}Setting up certificate auto-renewal...${NC}"
CRON_JOB="0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'"
(crontab -l 2>/dev/null | grep -v "certbot renew"; echo "$CRON_JOB") | crontab -

echo -e "${GREEN}=== Setup Complete ===${NC}"
echo -e "Nginx configuration: ${NGINX_AVAILABLE}"
echo -e "Certificate location: /etc/letsencrypt/live/${DOMAIN}/"
echo -e "Auto-renewal: Configured (daily at 3 AM)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update backend to bind 127.0.0.1:8000"
echo -e "2. Update frontend to build for production"
echo -e "3. Test: curl https://${DOMAIN}/api/v1/health"
