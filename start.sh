#!/bin/bash

# AI Video Subtitler - Startup Script
# This script helps start all required services

echo "🎬 Starting AI Video Subtitler Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python3 -m venv venv' first."
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration before continuing."
    exit 1
fi

# Create required directories
mkdir -p temp_files output_files

# Function to cleanup on exit
cleanup() {
    echo "\n🛑 Stopping services..."
    kill $CELERY_WORKER_PID $CELERY_BEAT_PID $FLASK_PID 2>/dev/null
    echo "✅ All services stopped."
    exit 0
}

trap cleanup INT TERM

# Start Celery Worker
echo "🔧 Starting Celery Worker..."
celery -A tasks.celery worker --loglevel=info > logs/celery_worker.log 2>&1 &
CELERY_WORKER_PID=$!

# Start Celery Beat
echo "⏰ Starting Celery Beat..."
celery -A tasks.celery beat --loglevel=info > logs/celery_beat.log 2>&1 &
CELERY_BEAT_PID=$!

# Wait a moment for Celery to initialize
sleep 3

# Start Flask Application
echo "🚀 Starting Flask Application..."
python app.py &
FLASK_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📍 Application URL: http://localhost:5000"
echo ""
echo "📊 Process IDs:"
echo "   - Celery Worker: $CELERY_WORKER_PID"
echo "   - Celery Beat: $CELERY_BEAT_PID"
echo "   - Flask App: $FLASK_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Flask to finish (which it won't unless killed)
wait $FLASK_PID
