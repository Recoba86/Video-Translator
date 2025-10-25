#!/bin/bash
# Watch Celery logs in real-time for debugging

echo "🔍 Monitoring Celery Worker Logs..."
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

tail -f logs/celery.log | grep --line-buffered -E "Transcrib|ERROR|Exception|Traceback|Task.*process_video|succeeded|failed|Audio file|File exists|complete" -i
