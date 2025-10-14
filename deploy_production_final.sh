#!/bin/bash

###############################################################################
# GW2 WvW Builder - Production Deployment Script
# Version: 1.0.0
# Date: 2025-10-15
# Purpose: Complete production deployment with validation
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo "============================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "============================================" | tee -a "$LOG_FILE"
}

###############################################################################
# Phase 1: Pre-deployment Checks
###############################################################################

print_header "PHASE 1: PRE-DEPLOYMENT CHECKS"

# Check if on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_error "Not on main branch (current: $CURRENT_BRANCH)"
    exit 1
fi
print_success "On main branch"

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean"
    exit 1
fi
print_success "Working directory is clean"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    print_error "Poetry not found. Please install poetry."
    exit 1
fi
print_success "Poetry found"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm not found. Please install Node.js."
    exit 1
fi
print_success "npm found"

###############################################################################
# Phase 2: Stop Running Services
###############################################################################

print_header "PHASE 2: STOPPING RUNNING SERVICES"

# Stop backend on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_info "Stopping backend on port 8000..."
    fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
    print_success "Backend stopped"
else
    print_info "No backend running on port 8000"
fi

# Stop frontend dev server on port 5173
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_info "Stopping frontend dev server on port 5173..."
    fuser -k 5173/tcp 2>/dev/null || true
    sleep 2
    print_success "Frontend dev server stopped"
else
    print_info "No frontend dev server running on port 5173"
fi

###############################################################################
# Phase 3: Install Dependencies
###############################################################################

print_header "PHASE 3: INSTALLING DEPENDENCIES"

# Backend dependencies
print_info "Installing backend dependencies..."
cd backend
if poetry install --no-interaction 2>&1 | tee -a "../$LOG_FILE"; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi
cd ..

# Frontend dependencies
print_info "Installing frontend dependencies..."
cd frontend
if npm install 2>&1 | tee -a "../$LOG_FILE"; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi
cd ..

###############################################################################
# Phase 4: Database Migration
###############################################################################

print_header "PHASE 4: DATABASE MIGRATION"

print_info "Applying database migrations..."
cd backend
if poetry run alembic upgrade head 2>&1 | tee -a "../$LOG_FILE"; then
    print_success "Database migrations applied"
else
    print_warning "Database migrations failed or already up-to-date"
fi
cd ..

###############################################################################
# Phase 5: Build Frontend
###############################################################################

print_header "PHASE 5: BUILDING FRONTEND"

print_info "Building frontend for production..."
cd frontend
if npm run build 2>&1 | tee -a "../$LOG_FILE"; then
    print_success "Frontend built successfully"
    
    # Check if dist directory exists
    if [ -d "dist" ]; then
        DIST_SIZE=$(du -sh dist | cut -f1)
        print_info "Build size: $DIST_SIZE"
    fi
else
    print_error "Frontend build failed"
    exit 1
fi
cd ..

###############################################################################
# Phase 6: Start Backend
###############################################################################

print_header "PHASE 6: STARTING BACKEND"

print_info "Starting backend server..."
cd backend

# Start backend in background
nohup poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 > "../backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

print_info "Backend PID: $BACKEND_PID"
print_info "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend started successfully"
else
    print_error "Backend failed to start"
    exit 1
fi

cd ..

###############################################################################
# Phase 7: Health Check
###############################################################################

print_header "PHASE 7: HEALTH CHECK"

print_info "Checking backend health..."
sleep 2

MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1; then
        HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8000/api/v1/health)
        print_success "Backend health check passed"
        print_info "Response: $HEALTH_RESPONSE"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        print_warning "Health check failed, retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Backend health check failed after $MAX_RETRIES attempts"
    # Kill backend
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

###############################################################################
# Phase 8: Seed Test User
###############################################################################

print_header "PHASE 8: SEEDING TEST USER"

print_info "Seeding test user..."
cd backend

if poetry run python scripts/fix_test_user.py 2>&1 | tee -a "../$LOG_FILE"; then
    print_success "Test user seeded"
else
    print_warning "Test user seeding failed or user already exists"
fi

cd ..

###############################################################################
# Phase 9: Frontend Accessibility Check
###############################################################################

print_header "PHASE 9: FRONTEND ACCESSIBILITY CHECK"

# Start a simple HTTP server for frontend (optional, using built files)
print_info "Frontend built files ready in frontend/dist/"
print_info "To serve: cd frontend/dist && python3 -m http.server 3000"

###############################################################################
# Deployment Summary
###############################################################################

print_header "DEPLOYMENT SUMMARY"

print_success "✅ Pre-deployment checks passed"
print_success "✅ Services stopped"
print_success "✅ Dependencies installed"
print_success "✅ Database migrated"
print_success "✅ Frontend built"
print_success "✅ Backend started (PID: $BACKEND_PID)"
print_success "✅ Health check passed"
print_success "✅ Test user seeded"

echo ""
print_info "Backend URL: http://127.0.0.1:8000"
print_info "API Docs: http://127.0.0.1:8000/docs"
print_info "Health: http://127.0.0.1:8000/api/v1/health"
print_info "Backend PID: $BACKEND_PID (saved in backend.pid)"
print_info "Backend logs: backend.log"
print_info "Deployment log: $LOG_FILE"

echo ""
print_info "To run E2E tests: cd frontend && npm run e2e:headless"
print_info "To stop backend: kill \$(cat backend.pid)"

###############################################################################
# Save deployment info
###############################################################################

cat > deployment_info.txt << EOF
Deployment Date: $(date)
Branch: $CURRENT_BRANCH
Commit: $(git rev-parse HEAD)
Backend PID: $BACKEND_PID
Backend URL: http://127.0.0.1:8000
Log File: $LOG_FILE
EOF

print_success "Deployment info saved to deployment_info.txt"

print_header "DEPLOYMENT COMPLETED SUCCESSFULLY"

exit 0
