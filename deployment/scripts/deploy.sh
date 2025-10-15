#!/bin/bash
#
# Script: deploy.sh
# Description: Complete deployment script for GW2 WvW Builder
# Usage: ./deploy.sh [staging|production]
#

set -e

# Configuration
ENVIRONMENT="${1:-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/opt/gw2_wvw_builder"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== GW2 WvW Builder Deployment ===${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo ""

# Load environment-specific config
if [ "$ENVIRONMENT" = "production" ]; then
    BRANCH="main"
    SERVICE_NAME="gw2_backend"
elif [ "$ENVIRONMENT" = "staging" ]; then
    BRANCH="develop"
    SERVICE_NAME="gw2_backend"
else
    echo -e "${RED}Invalid environment. Use: staging or production${NC}"
    exit 1
fi

# Pre-deployment checks
echo -e "${GREEN}[1/8] Pre-deployment checks...${NC}"
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

# Backup database
echo -e "${GREEN}[2/8] Creating database backup...${NC}"
"${PROJECT_ROOT}/deployment/scripts/backup_db.sh" sqlite

# Update code
echo -e "${GREEN}[3/8] Updating code from Git...${NC}"
cd "$PROJECT_ROOT"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Backend deployment
echo -e "${GREEN}[4/8] Deploying backend...${NC}"
cd "${PROJECT_ROOT}/backend"

# Install dependencies
poetry install --no-dev --no-interaction

# Run migrations
poetry run alembic upgrade head

# Frontend deployment
echo -e "${GREEN}[5/8] Building frontend...${NC}"
cd "${PROJECT_ROOT}/frontend"
npm ci --production
npm run build

# Restart services
echo -e "${GREEN}[6/8] Restarting services...${NC}"
sudo systemctl restart "$SERVICE_NAME"

# Reload nginx
sudo systemctl reload nginx

# Health check
echo -e "${GREEN}[7/8] Running health check...${NC}"
sleep 5
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    sudo systemctl status "$SERVICE_NAME"
    exit 1
fi

# Post-deployment
echo -e "${GREEN}[8/8] Post-deployment tasks...${NC}"
echo "Deployment completed at: $(date)" >> "${PROJECT_ROOT}/deployment/deployment.log"

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Branch: ${YELLOW}${BRANCH}${NC}"
echo -e "Service: ${YELLOW}${SERVICE_NAME}${NC}"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo -e "  Status:  sudo systemctl status ${SERVICE_NAME}"
echo -e "  Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo -e "  Monitor: python3 deployment/scripts/monitor_backend.py"
