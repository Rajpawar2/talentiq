#!/usr/bin/env bash
# ==============================================================================
# TalentIQ - Unified Single-Command Startup Script
# Starts both the FastAPI Backend and Vite Frontend concurrently.
# Cleanly terminates all child processes on Ctrl+C.
# ==============================================================================

set -e

# Resolve script directory (talentiq root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for terminal output
BOLD="\033[1m"
GREEN="\033[32m"
BLUE="\033[34m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}"
echo "  ╔════════════════════════════════════════════════════════════════════╗"
echo "  ║                           TalentIQ                                 ║"
echo "  ║        AI-Powered Adaptive Interview & Talent Platform             ║"
echo "  ╚════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# 1. Verify and prepare Backend Python Virtualenv
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${YELLOW}[!] Python virtual environment (.venv) not found in backend.${RESET}"
    echo -e "${BLUE}[*] Creating virtual environment and installing dependencies...${RESET}"
    python3 -m venv "$BACKEND_DIR/.venv"
    "$BACKEND_DIR/.venv/bin/pip" install --upgrade pip
    "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

# 2. Verify Frontend Dependencies
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}[!] Frontend node_modules not found.${RESET}"
    echo -e "${BLUE}[*] Running npm install in frontend...${RESET}"
    (cd "$FRONTEND_DIR" && npm install)
fi

# Track child PIDs for cleanup on exit
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo -e "\n${YELLOW}[*] Shutting down TalentIQ servers cleanly...${RESET}"
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    # Also kill any lingering processes on ports 8000 and 5173
    pkill -P $$ 2>/dev/null || true
    echo -e "${GREEN}[✓] All servers stopped.${RESET}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 3. Start Backend Server
echo -e "${GREEN}[+] Starting FastAPI Backend server on http://localhost:8000 ...${RESET}"
(
    cd "$BACKEND_DIR"
    exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

# Brief pause to allow backend port binding
sleep 1.5

# 4. Start Frontend Vite Server
echo -e "${GREEN}[+] Starting Vite Frontend dev server on http://localhost:5173 ...${RESET}"
(
    cd "$FRONTEND_DIR"
    exec npm run dev
) &
FRONTEND_PID=$!

echo -e "\n${BOLD}${GREEN}===================================================================="
echo -e " TalentIQ is running live!"
echo -e "  ➜ Frontend Application: ${CYAN}http://localhost:5173${GREEN}"
echo -e "  ➜ Backend API:          ${CYAN}http://localhost:8000${GREEN}"
echo -e "  ➜ Interactive Swagger:  ${CYAN}http://localhost:8000/docs${GREEN}"
echo -e "====================================================================${RESET}\n"
echo -e "${YELLOW}Press Ctrl+C at any time to stop both servers.${RESET}\n"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
