#!/bin/bash

# Launch script for Streamlit GUI application in detached mode
# This script starts the Streamlit app and displays the URL

echo "=========================================="
echo "PDF to AstraDB - Docling GUI Launcher"
echo "=========================================="
echo ""

# Get the project root directory (parent of scripts folder)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "myvenv" ] && [ ! -d "env" ]; then
    echo "⚠️  Warning: No virtual environment found"
    echo "   Consider creating one with: python -m venv venv"
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment (venv)..."
    source venv/bin/activate
elif [ -d "myvenv" ]; then
    echo "🔧 Activating virtual environment (myvenv)..."
    source myvenv/bin/activate
elif [ -d "env" ]; then
    echo "🔧 Activating virtual environment (env)..."
    source env/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create a .env file with required credentials"
    exit 1
fi

# Check if app_gui_docling.py exists
if [ ! -f "app_gui_docling.py" ]; then
    echo "❌ Error: app_gui_docling.py not found"
    exit 1
fi

# Set port (default 8501, can be overridden)
PORT=${1:-8501}

# Create log directory
mkdir -p logs

# Log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/streamlit_${TIMESTAMP}.log"

echo "🚀 Starting Streamlit application..."
echo "📝 Log file: $LOG_FILE"
echo ""

# Start Streamlit in background
nohup streamlit run app_gui_docling.py \
    --server.port=$PORT \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    > "$LOG_FILE" 2>&1 &

# Get the process ID
PID=$!

# Wait a moment for the server to start
sleep 3

# Check if process is still running
if ps -p $PID > /dev/null; then
    echo "✅ Streamlit application started successfully!"
    echo ""
    echo "📊 Application Details:"
    echo "   - Process ID: $PID"
    echo "   - Port: $PORT"
    echo "   - Log file: $LOG_FILE"
    echo ""
    echo "🌐 Access the application at:"
    echo "   - Local: http://localhost:$PORT"
    echo "   - Network: http://$(hostname):$PORT"
    echo ""
    echo "🛑 To stop the application, run:"
    echo "   kill $PID"
    echo ""
    echo "📋 To view logs in real-time, run:"
    echo "   tail -f $LOG_FILE"
    echo ""
    
    # Save PID to file for easy stopping
    echo $PID > logs/streamlit.pid
    echo "💾 PID saved to logs/streamlit.pid"
    echo ""
else
    echo "❌ Error: Failed to start Streamlit application"
    echo "   Check the log file for details: $LOG_FILE"
    exit 1
fi

# Made with Bob
