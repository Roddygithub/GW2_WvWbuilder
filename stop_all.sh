#!/bin/bash
# ==============================
# Script Stop – GW2_WvWBuilder v4.0
# ==============================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Arrêt GW2_WvWBuilder v4.0                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🔹 Arrêt backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend arrêté${NC}"
    fi
    rm .backend.pid
fi

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🔹 Arrêt frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend arrêté${NC}"
    fi
    rm .frontend.pid
fi

# Stop Ollama (optional, keep running for other uses)
if [ -f .ollama.pid ]; then
    echo -e "${YELLOW}🔹 Ollama reste actif (utilisable pour d'autres projets)${NC}"
    echo -e "${YELLOW}   Pour arrêter Ollama: pkill ollama${NC}"
    rm .ollama.pid
fi

# Clean up ports
echo -e "${YELLOW}🔹 Nettoyage des ports...${NC}"
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Tous les services sont arrêtés${NC}"
echo ""
