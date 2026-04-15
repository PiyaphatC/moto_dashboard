#!/bin/bash
# Starts the Streamlit dashboard and exposes it publicly via Cloudflare Tunnel.
# Usage: bash start.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8501

echo "Starting Streamlit on port $PORT..."
streamlit run "$SCRIPT_DIR/dashboard.py" \
  --server.port $PORT \
  --server.headless true \
  --server.fileWatcherType poll \
  --browser.gatherUsageStats false &

STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

# Give Streamlit a moment to boot
sleep 3

echo ""
echo "Starting Cloudflare Tunnel..."
echo "Your public URL will appear below — share it with anyone."
echo "The dashboard auto-refreshes every 30 s when the Excel file changes."
echo "Press Ctrl+C to stop everything."
echo ""

# Trap Ctrl+C to kill Streamlit too
trap "kill $STREAMLIT_PID 2>/dev/null; exit" INT TERM

cloudflared tunnel --url http://localhost:$PORT
