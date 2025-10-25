#!/bin/bash

# Start Services Script for AI Video Subtitler
# This script starts Flask and Celery services

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Kill any existing services
echo "Stopping any existing services..."
pkill -9 -f "python app.py" 2>/dev/null
pkill -9 -f "celery.*tasks" 2>/dev/null
sleep 2

# Start Flask server in background (production mode to avoid debug issues)
echo "Starting Flask server on port 8000..."
FLASK_ENV=production python app.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "Flask started with PID: $FLASK_PID"

# Wait for Flask to start
sleep 3

# Start Celery worker in background (concurrency=1 to avoid memory issues with Whisper)
echo "Starting Celery worker..."
celery -A tasks worker --loglevel=info --concurrency=1 > logs/celery.log 2>&1 &
CELERY_PID=$!
echo "Celery started with PID: $CELERY_PID"

# Wait for Celery to start
sleep 3

# Check if services are running
echo ""
echo "=== Service Status ==="
if ps -p $FLASK_PID > /dev/null; then
    echo "✅ Flask is running (PID: $FLASK_PID)"
    echo "   Access at: http://localhost:8000"
else
    echo "❌ Flask failed to start"
fi

if ps -p $CELERY_PID > /dev/null; then
    echo "✅ Celery is running (PID: $CELERY_PID)"
else
    echo "❌ Celery failed to start"
fi

echo ""
echo "=== Logs ==="
echo "Flask logs: tail -f logs/flask.log"
echo "Celery logs: tail -f logs/celery.log"
echo ""
echo "=== Stop Services ==="
echo "To stop: pkill -f 'python app.py' && pkill -f 'celery.*tasks'"
