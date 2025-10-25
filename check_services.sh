#!/bin/bash
# Quick service status check for Video Translator

echo "🔍 Checking Video Translator Services..."
echo ""

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: NOT running"
fi

# Check Celery
CELERY_COUNT=$(ps aux | grep -E "celery.*worker" | grep -v grep | wc -l | tr -d ' ')
if [ "$CELERY_COUNT" -gt 0 ]; then
    echo "✅ Celery: Running ($CELERY_COUNT processes)"
else
    echo "❌ Celery: NOT running"
fi

# Check Flask
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Flask: Running on port 8000"
    echo ""
    echo "🌐 Access your app at: http://localhost:8000/simple"
else
    echo "❌ Flask: NOT running on port 8000"
fi

echo ""
echo "================================"
