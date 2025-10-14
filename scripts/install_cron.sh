#!/bin/bash

###############################################################################
# Install Cron Job for Database Backup
# Run this script to setup weekly database backup
###############################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/home/roddy/GW2_WvWbuilder"

echo -e "${YELLOW}Installing cron job for weekly database backup...${NC}"

# Check if cron is installed
if ! command -v crontab &> /dev/null; then
    echo -e "${YELLOW}cron not found. Installing...${NC}"
    sudo apt update
    sudo apt install -y cron
fi

# Backup script path
BACKUP_SCRIPT="$PROJECT_ROOT/scripts/backup_database.sh"

# Cron job entry: Every Sunday at 2:00 AM
CRON_CMD="0 2 * * 0 $BACKUP_SCRIPT >> $PROJECT_ROOT/backups/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup_database.sh"; then
    echo -e "${YELLOW}Cron job already exists!${NC}"
    echo "Current cron jobs:"
    crontab -l | grep backup_database.sh
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo -e "${GREEN}✅ Cron job installed successfully!${NC}"
    echo ""
    echo "Schedule: Every Sunday at 2:00 AM"
    echo "Command: $CRON_CMD"
fi

echo ""
echo "To view all cron jobs: crontab -l"
echo "To remove cron job: crontab -e (then delete the line)"

exit 0
