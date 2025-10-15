#!/bin/bash
# Clean restart script for GW2 WvW Builder frontend

echo "🧹 Cleaning cache and rebuilding..."

# Kill any running dev servers on port 5173 and 5174
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true

# Remove cache and build artifacts
rm -rf node_modules/.vite
rm -rf dist
rm -rf .cache

echo "✅ Cache cleared"
echo "🚀 Starting fresh dev server..."

# Start dev server
npm run dev
