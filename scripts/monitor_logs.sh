#!/bin/bash

###############################################################################
# GW2 WvW Builder - Log Monitoring Script
# Version: 1.0.0
# Purpose: Monitor backend logs in real-time with filtering
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="/home/roddy/GW2_WvWbuilder"
LOG_FILE="$PROJECT_ROOT/backend.log"

# Function to display help
show_help() {
    cat << EOF
🔍 GW2 WvW Builder - Log Monitor

Usage: $0 [OPTIONS]

OPTIONS:
    -f, --follow        Follow logs in real-time (default)
    -e, --errors        Show only errors
    -w, --warnings      Show only warnings
    -i, --info          Show only info logs
    -a, --all           Show all logs (no filtering)
    -n, --lines N       Show last N lines (default: 50)
    -c, --clean         Clean old logs (keep last 7 days)
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Follow all logs with color
    $0 -e               # Show only errors
    $0 -n 100           # Show last 100 lines
    $0 -c               # Clean old logs

EOF
    exit 0
}

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Log file not found: $LOG_FILE"
    echo "Backend may not be running or logs are in a different location."
    exit 1
fi

# Default options
FOLLOW=true
FILTER=""
LINES=50
MODE="follow"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            MODE="follow"
            shift
            ;;
        -e|--errors)
            FILTER="ERROR"
            MODE="filter"
            shift
            ;;
        -w|--warnings)
            FILTER="WARNING"
            MODE="filter"
            shift
            ;;
        -i|--info)
            FILTER="INFO"
            MODE="filter"
            shift
            ;;
        -a|--all)
            FILTER=""
            MODE="all"
            shift
            ;;
        -n|--lines)
            LINES="$2"
            FOLLOW=false
            MODE="tail"
            shift 2
            ;;
        -c|--clean)
            echo -e "${BLUE}[INFO]${NC} Cleaning old logs..."
            find "$PROJECT_ROOT" -name "*.log" -mtime +7 -delete 2>/dev/null || true
            echo -e "${GREEN}[SUCCESS]${NC} Old logs cleaned (kept last 7 days)"
            exit 0
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown option: $1"
            show_help
            ;;
    esac
done

# Header
clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║          GW2 WvW Builder - Log Monitor                   ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo -e "${BLUE}Log file:${NC} $LOG_FILE"
echo -e "${BLUE}Mode:${NC} $MODE"
if [ -n "$FILTER" ]; then
    echo -e "${BLUE}Filter:${NC} $FILTER"
fi
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Function to colorize logs
colorize_log() {
    sed -E \
        -e "s/(ERROR|CRITICAL)/$(echo -e ${RED})\\1$(echo -e ${NC})/g" \
        -e "s/(WARNING)/$(echo -e ${YELLOW})\\1$(echo -e ${NC})/g" \
        -e "s/(INFO)/$(echo -e ${GREEN})\\1$(echo -e ${NC})/g" \
        -e "s/(DEBUG)/$(echo -e ${CYAN})\\1$(echo -e ${NC})/g" \
        -e "s/(HTTP\/1\.1\" [2][0-9]{2})/$(echo -e ${GREEN})\\1$(echo -e ${NC})/g" \
        -e "s/(HTTP\/1\.1\" [4-5][0-9]{2})/$(echo -e ${RED})\\1$(echo -e ${NC})/g" \
        -e "s/(\[NEW CODE\])/$(echo -e ${MAGENTA})\\1$(echo -e ${NC})/g"
}

# Execute based on mode
case $MODE in
    follow)
        if [ -n "$FILTER" ]; then
            tail -f "$LOG_FILE" | grep --line-buffered "$FILTER" | colorize_log
        else
            tail -f "$LOG_FILE" | colorize_log
        fi
        ;;
    filter)
        if [ -n "$FILTER" ]; then
            tail -n "$LINES" "$LOG_FILE" | grep "$FILTER" | colorize_log
        else
            tail -n "$LINES" "$LOG_FILE" | colorize_log
        fi
        ;;
    tail)
        tail -n "$LINES" "$LOG_FILE" | colorize_log
        ;;
    all)
        tail -f "$LOG_FILE" | colorize_log
        ;;
esac
