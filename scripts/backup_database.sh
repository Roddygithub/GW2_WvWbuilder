#!/bin/bash

###############################################################################
# GW2 WvW Builder - Database Backup Script
# Version: 1.0.0
# Purpose: Weekly database backup (overwrites previous backup)
# Schedule: Sunday 2:00 AM via cron
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/home/roddy/GW2_WvWbuilder"
DB_PATH="$PROJECT_ROOT/backend/gw2_wvwbuilder.db"
BACKUP_DIR="$PROJECT_ROOT/backups"
BACKUP_FILE="$BACKUP_DIR/gw2_wvwbuilder.db.backup"
LOG_FILE="$BACKUP_DIR/backup.log"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

###############################################################################
# Main Backup Process
###############################################################################

log_info "=========================================="
log_info "Starting Database Backup"
log_info "=========================================="

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    log_error "Database not found: $DB_PATH"
    exit 1
fi

# Get database size
DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
log_info "Database size: $DB_SIZE"

# Check if old backup exists
if [ -f "$BACKUP_FILE" ]; then
    OLD_BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    OLD_BACKUP_DATE=$(stat -c %y "$BACKUP_FILE" | cut -d' ' -f1)
    log_info "Previous backup found: $OLD_BACKUP_SIZE (from $OLD_BACKUP_DATE)"
    log_info "Overwriting previous backup..."
fi

# Create backup (overwrite existing)
if cp -f "$DB_PATH" "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_success "Backup created successfully"
    log_info "Backup location: $BACKUP_FILE"
    log_info "Backup size: $BACKUP_SIZE"
    
    # Verify backup integrity
    if [ -f "$BACKUP_FILE" ]; then
        if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" > /dev/null 2>&1; then
            log_success "Backup integrity verified"
        else
            log_error "Backup integrity check failed"
            exit 1
        fi
    fi
else
    log_error "Backup failed"
    exit 1
fi

# Cleanup old logs (keep last 30 days)
find "$BACKUP_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

log_info "=========================================="
log_success "Backup Completed Successfully"
log_info "=========================================="

# Summary
cat << EOF | tee -a "$LOG_FILE"

📊 Backup Summary:
------------------
Database: $DB_PATH
Backup: $BACKUP_FILE
Size: $BACKUP_SIZE
Date: $(date +'%Y-%m-%d %H:%M:%S')
Status: ✅ SUCCESS

EOF

exit 0
