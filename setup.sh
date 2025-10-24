#!/bin/bash

# Quick Setup Script for AI Video Subtitler

echo "🎬 AI Video Subtitler - Quick Setup"
echo "=================================="
echo ""

# Check Python version
echo "1️⃣ Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python found"
echo ""

# Check FFmpeg
echo "2️⃣ Checking FFmpeg..."
ffmpeg -version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ FFmpeg is not installed."
    echo "   Install it with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Ubuntu)"
    exit 1
fi
echo "✅ FFmpeg found"
echo ""

# Check Redis
echo "3️⃣ Checking Redis..."
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Redis is not running."
    echo "   Install it with: brew install redis (macOS) or sudo apt install redis-server (Ubuntu)"
    echo "   Start it with: redis-server or brew services start redis"
    read -p "Would you like to start Redis now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        redis-server --daemonize yes
        sleep 2
        echo "✅ Redis started"
    else
        exit 1
    fi
else
    echo "✅ Redis is running"
fi
echo ""

# Create virtual environment
echo "4️⃣ Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate and install dependencies
echo "5️⃣ Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment file
echo "6️⃣ Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: You need to configure your Google Cloud credentials!"
    echo ""
    echo "Next steps:"
    echo "1. Get your Google Cloud service account JSON key"
    echo "2. Save it as 'google-credentials.json' in this directory"
    echo "3. Edit .env and update GOOGLE_APPLICATION_CREDENTIALS path if needed"
    echo "4. Update SECRET_KEY in .env with a random string"
    echo ""
    read -p "Press Enter when you've completed the above steps..."
else
    echo "✅ .env file already exists"
fi
echo ""

# Create directories
echo "7️⃣ Creating directories..."
mkdir -p temp_files output_files logs
echo "✅ Directories created"
echo ""

# Make start script executable
echo "8️⃣ Making scripts executable..."
chmod +x start.sh
echo "✅ Scripts are executable"
echo ""

echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "To start the application, run:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  celery -A tasks.celery worker --loglevel=info &"
echo "  celery -A tasks.celery beat --loglevel=info &"
echo "  python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
