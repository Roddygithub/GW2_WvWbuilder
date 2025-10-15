#!/bin/bash
#
# Script: backup_db.sh
# Description: Automated database backup for GW2 WvW Builder
# Usage: ./backup_db.sh [--type sqlite|postgres]
# Cron: 0 3 * * 0 /opt/gw2_wvw_builder/deployment/scripts/backup_db.sh
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/opt/gw2_wvw_builder"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="/var/log/gw2_wvw_builder/backup.log"
RETENTION_DAYS=30

# Database configuration
DB_TYPE="${1:-sqlite}"  # sqlite or postgres
SQLITE_DB_PATH="${PROJECT_ROOT}/backend/data/app.db"
PG_DATABASE="${PG_DATABASE:-gw2_wvw_builder}"
PG_USER="${PG_USER:-gw2app}"
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "=== Starting database backup ==="
log "Type: $DB_TYPE"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LATEST="${BACKUP_DIR}/backup_latest"

case "$DB_TYPE" in
    sqlite)
        log "Backing up SQLite database..."
        
        if [ ! -f "$SQLITE_DB_PATH" ]; then
            log_error "SQLite database not found: $SQLITE_DB_PATH"
            exit 1
        fi
        
        # Create timestamped backup
        BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.db"
        cp "$SQLITE_DB_PATH" "$BACKUP_FILE"
        
        # Create/update latest backup symlink
        ln -sf "$BACKUP_FILE" "${BACKUP_LATEST}.db"
        
        # Compress old backups (except latest)
        find "$BACKUP_DIR" -name "backup_*.db" -mtime +1 -type f -exec gzip {} \;
        
        # Verify backup
        if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
            BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            log_success "SQLite backup created: $BACKUP_FILE ($BACKUP_SIZE)"
        else
            log_error "Backup verification failed"
            rm "$BACKUP_FILE"
            exit 1
        fi
        ;;
    
    postgres)
        log "Backing up PostgreSQL database..."
        
        # Check if pg_dump is available
        if ! command -v pg_dump &> /dev/null; then
            log_error "pg_dump not found. Install postgresql-client"
            exit 1
        fi
        
        # Create backup with custom format (supports compression)
        BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.dump"
        
        PGPASSWORD="$PG_PASSWORD" pg_dump \
            -h "$PG_HOST" \
            -p "$PG_PORT" \
            -U "$PG_USER" \
            -F c \
            -b \
            -v \
            -f "$BACKUP_FILE" \
            "$PG_DATABASE" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            # Create/update latest backup symlink
            ln -sf "$BACKUP_FILE" "${BACKUP_LATEST}.dump"
            
            BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            log_success "PostgreSQL backup created: $BACKUP_FILE ($BACKUP_SIZE)"
        else
            log_error "PostgreSQL backup failed"
            [ -f "$BACKUP_FILE" ] && rm "$BACKUP_FILE"
            exit 1
        fi
        ;;
    
    *)
        log_error "Unknown database type: $DB_TYPE"
        echo "Usage: $0 [sqlite|postgres]"
        exit 1
        ;;
esac

# Cleanup old backups (older than retention period)
log "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "backup_*" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)
log "Deleted $DELETED_COUNT old backup(s)"

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "backup_*" -type f | wc -l)

log "Backup statistics:"
log "  - Total backups: $BACKUP_COUNT"
log "  - Total size: $TOTAL_SIZE"
log "  - Backup directory: $BACKUP_DIR"

log_success "Backup completed successfully"
log "=== Backup finished ==="

# Optional: Send notification (email, webhook, etc.)
# Example with curl webhook:
# curl -X POST https://your-webhook.com/backup \
#     -H "Content-Type: application/json" \
#     -d "{\"status\":\"success\",\"timestamp\":\"$TIMESTAMP\",\"size\":\"$BACKUP_SIZE\"}"

exit 0
