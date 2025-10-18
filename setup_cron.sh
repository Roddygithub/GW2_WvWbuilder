#!/bin/bash
# ==============================
# Setup Auto-Learning Cron Job
# GW2_WvWbuilder v4.1
# ==============================

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  GW2_WvWbuilder v4.1 — Setup Auto-Learning Cron           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get absolute path
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo -e "${YELLOW}🔹 Configuration:${NC}"
echo -e "   Project: ${GREEN}$PROJECT_DIR${NC}"
echo -e "   Backend: ${GREEN}$BACKEND_DIR${NC}"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "GW2_WvWbuilder KB refresh"; then
    echo -e "${YELLOW}⚠️  Cron job already exists. Removing old entry...${NC}"
    crontab -l 2>/dev/null | grep -v "GW2_WvWbuilder KB refresh" | crontab -
fi

# Add new cron job
echo -e "${YELLOW}🔹 Adding cron job (daily at 3:00 AM)...${NC}"

# Create cron entry
CRON_ENTRY="0 3 * * * cd $BACKEND_DIR && poetry run python app/core/kb/refresh.py --with-llm --auto >> $PROJECT_DIR/kb_refresh.log 2>&1  # GW2_WvWbuilder KB refresh"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo -e "${GREEN}✅ Cron job added successfully${NC}"
echo ""

# Display current crontab
echo -e "${YELLOW}📋 Current crontab:${NC}"
crontab -l | grep "GW2_WvWbuilder"
echo ""

echo -e "${BLUE}ℹ️  KB Refresh Schedule:${NC}"
echo -e "   Frequency: ${GREEN}Daily at 3:00 AM${NC}"
echo -e "   Command:   ${GREEN}poetry run python app/core/kb/refresh.py --with-llm --auto${NC}"
echo -e "   Log file:  ${GREEN}$PROJECT_DIR/kb_refresh.log${NC}"
echo ""

echo -e "${BLUE}🧪 Test the refresh manually:${NC}"
echo -e "   ${YELLOW}cd backend && poetry run python app/core/kb/refresh.py --with-llm${NC}"
echo ""

echo -e "${BLUE}🗑️  To remove the cron job:${NC}"
echo -e "   ${YELLOW}crontab -l | grep -v 'GW2_WvWbuilder KB refresh' | crontab -${NC}"
echo ""

echo -e "${GREEN}✅ Auto-learning setup complete!${NC}"
