#!/bin/bash
#
# Script: install_services.sh
# Description: Install and enable systemd services for GW2 WvW Builder
# Usage: sudo ./install_services.sh
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Installing GW2 WvW Builder Services ===${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root${NC}"
    exit 1
fi

# Create user if not exists
if ! id "gw2app" &>/dev/null; then
    echo -e "${GREEN}Creating gw2app user...${NC}"
    useradd -r -s /bin/false -m -d /opt/gw2_wvw_builder gw2app
fi

# Create log directory
echo -e "${GREEN}Creating log directory...${NC}"
mkdir -p /var/log/gw2_wvw_builder
chown -R gw2app:gw2app /var/log/gw2_wvw_builder

# Install backend service
echo -e "${GREEN}Installing backend service...${NC}"
cp ../systemd/gw2_backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gw2_backend.service

# Install frontend service (optional)
read -p "Install frontend service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Installing frontend service...${NC}"
    cp ../systemd/gw2_frontend.service /etc/systemd/system/
    systemctl enable gw2_frontend.service
else
    echo -e "${YELLOW}Skipping frontend service (serving via Nginx is recommended)${NC}"
fi

echo -e "${GREEN}=== Installation Complete ===${NC}"
echo -e ""
echo -e "${YELLOW}Service Commands:${NC}"
echo -e "Start backend:   sudo systemctl start gw2_backend"
echo -e "Stop backend:    sudo systemctl stop gw2_backend"
echo -e "Restart backend: sudo systemctl restart gw2_backend"
echo -e "Status:          sudo systemctl status gw2_backend"
echo -e "Logs:            sudo journalctl -u gw2_backend -f"
echo -e ""
echo -e "${YELLOW}Important:${NC}"
echo -e "1. Ensure /opt/gw2_wvw_builder exists"
echo -e "2. Ensure .env file is properly configured"
echo -e "3. Ensure poetry venv is at /opt/gw2_wvw_builder/backend/.venv"
echo -e "4. Test manually before starting service"
