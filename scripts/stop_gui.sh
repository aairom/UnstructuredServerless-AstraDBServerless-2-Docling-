#!/bin/bash

# Stop script for Streamlit GUI application
# This script stops the running Streamlit application

echo "=========================================="
echo "PDF to AstraDB - Stop GUI Application"
echo "=========================================="
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if PID file exists
PID_FILE="logs/streamlit.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ No PID file found at: $PID_FILE"
    echo "   The application may not be running or was started manually."
    echo ""
    echo "🔍 Searching for Streamlit processes..."
    
    # Search for running Streamlit processes
    PIDS=$(pgrep -f "streamlit run app_gui_docling.py")
    
    if [ -z "$PIDS" ]; then
        echo "   No Streamlit processes found."
        exit 0
    else
        echo "   Found Streamlit process(es): $PIDS"
        echo ""
        read -p "   Do you want to stop these processes? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $PIDS
            echo "✅ Processes stopped"
        else
            echo "❌ Operation cancelled"
        fi
        exit 0
    fi
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Stopping Streamlit application (PID: $PID)..."
    
    # Try graceful shutdown first
    kill $PID
    
    # Wait for process to stop
    sleep 2
    
    # Check if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Process still running, forcing shutdown..."
        kill -9 $PID
        sleep 1
    fi
    
    # Verify process stopped
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ Streamlit application stopped successfully"
        rm "$PID_FILE"
    else
        echo "❌ Failed to stop process"
        exit 1
    fi
else
    echo "⚠️  Process $PID is not running"
    echo "   Cleaning up PID file..."
    rm "$PID_FILE"
fi

echo ""
echo "✅ Cleanup complete"

# Made with Bob
