#!/bin/bash
# ==============================
# Script Auto – GW2_WvWBuilder v4.0
# IA Tactique McM Autonome (Auto Mode Soft-Only + LLM Ollama)
# ==============================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  GW2_WvWBuilder v4.0 — IA Tactique McM Autonome           ║${NC}"
echo -e "${BLUE}║  Auto Mode (Soft-Only) + LLM Ollama/Mistral               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# --- Variables d'environnement pour LLM Ollama/Mistral ---
export LLM_ENGINE=ollama
export LLM_MODEL=mistral:7b
export LLM_ENDPOINT=http://localhost:11434

# --- Nettoyage des ports si occupés ---
echo -e "${YELLOW}🔹 Nettoyage des ports...${NC}"
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1

# --- Vérification Ollama installé ---
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama n'est pas installé. Installation requise:${NC}"
    echo -e "${YELLOW}   curl -fsSL https://ollama.com/install.sh | sh${NC}"
    echo -e "${YELLOW}   Puis: ollama pull mistral:7b${NC}"
    echo ""
    echo -e "${BLUE}ℹ️  Le système fonctionnera en mode fallback heuristique sans LLM.${NC}"
    OLLAMA_AVAILABLE=false
else
    OLLAMA_AVAILABLE=true
fi

# --- Lancer Ollama/Mistral en arrière-plan (si disponible) ---
if [ "$OLLAMA_AVAILABLE" = true ]; then
    echo -e "${YELLOW}🔹 Lancement Ollama/Mistral (7B) en arrière-plan...${NC}"
    
    # Check if model is available
    if ! ollama list | grep -q "mistral:7b"; then
        echo -e "${YELLOW}⚠️  Modèle mistral:7b non trouvé. Téléchargement...${NC}"
        ollama pull mistral:7b
    fi
    
    # Start Ollama serve if not running
    if ! pgrep -x "ollama" > /dev/null; then
        nohup ollama serve > ollama.log 2>&1 &
        sleep 2
    fi
    
    echo -e "${GREEN}✅ Ollama prêt${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama non disponible - Mode fallback heuristique actif${NC}"
fi

# --- Vérification Poetry installé ---
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry n'est pas installé. Installation requise:${NC}"
    echo -e "${YELLOW}   curl -sSL https://install.python-poetry.org | python3 -${NC}"
    exit 1
fi

# --- Lancer le backend FastAPI ---
echo -e "${YELLOW}🔹 Lancement backend FastAPI...${NC}"
cd backend

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}   Installation des dépendances backend...${NC}"
    poetry install
fi

# Start backend
nohup poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait for backend to be ready
echo -e "${YELLOW}   Attente du backend...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend prêt (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend timeout. Vérifiez backend.log${NC}"
        exit 1
    fi
    sleep 1
done

# --- Vérification npm installé ---
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm n'est pas installé. Installation Node.js requise.${NC}"
    exit 1
fi

# --- Lancer le frontend React/Vite ---
echo -e "${YELLOW}🔹 Lancement frontend React...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installation des dépendances frontend...${NC}"
    npm install
fi

# Start frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to be ready
echo -e "${YELLOW}   Attente du frontend...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend prêt (PID: $FRONTEND_PID)${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend timeout. Vérifiez frontend.log${NC}"
        exit 1
    fi
    sleep 1
done

# --- Feedback final ---
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Tout est lancé avec succès !                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo -e "   Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "   Swagger Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   Frontend:     ${GREEN}http://localhost:5173${NC}"
echo -e "   Optimize:     ${GREEN}http://localhost:5173/optimize${NC}"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "   Backend:  ${YELLOW}tail -f backend.log${NC}"
echo -e "   Frontend: ${YELLOW}tail -f frontend.log${NC}"
if [ "$OLLAMA_AVAILABLE" = true ]; then
    echo -e "   Ollama:   ${YELLOW}tail -f ollama.log${NC}"
fi
echo ""
echo -e "${BLUE}🔧 Configuration LLM:${NC}"
echo -e "   LLM_ENGINE:   ${GREEN}$LLM_ENGINE${NC}"
echo -e "   LLM_MODEL:    ${GREEN}$LLM_MODEL${NC}"
echo -e "   LLM_ENDPOINT: ${GREEN}$LLM_ENDPOINT${NC}"
echo ""
echo -e "${BLUE}🎮 Mode Auto (Soft-Only):${NC}"
echo -e "   ✅ Aucun quota dur par profession"
echo -e "   ✅ Objectifs soft pondérés (saturation, diversité, synergies)"
echo -e "   ✅ Adaptation continue via KB (GW2 API)"
if [ "$OLLAMA_AVAILABLE" = true ]; then
    echo -e "   ✅ LLM enrichi (Ollama + Mistral 7B)"
else
    echo -e "   ⚠️  Fallback heuristique (LLM non disponible)"
fi
echo ""
echo -e "${GREEN}🚀 Ouvre le navigateur sur http://localhost:5173/optimize${NC}"
echo -e "${YELLOW}   Pour arrêter: ./stop_all.sh${NC}"
echo ""

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
if [ "$OLLAMA_AVAILABLE" = true ]; then
    pgrep -x "ollama" > .ollama.pid || true
fi
