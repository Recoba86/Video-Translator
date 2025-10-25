#!/bin/bash
source venv/bin/activate
echo "Starting Celery worker..."
celery -A tasks worker --loglevel=info
