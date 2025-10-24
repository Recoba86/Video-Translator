# Configuration Examples

## Development Environment

For local development and testing:

```env
# .env
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key
FLASK_ENV=development
UPLOAD_FOLDER=temp_files
OUTPUT_FOLDER=output_files
MAX_CONTENT_LENGTH=524288000
FILE_RETENTION_HOURS=24
HOST=0.0.0.0
PORT=5000
```

## Production Environment

For production deployment:

```env
# .env
GOOGLE_APPLICATION_CREDENTIALS=/var/www/video-subtitler/google-credentials.json
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=YOUR-SUPER-SECRET-RANDOM-KEY-CHANGE-THIS
FLASK_ENV=production
UPLOAD_FOLDER=/var/www/video-subtitler/temp_files
OUTPUT_FOLDER=/var/www/video-subtitler/output_files
MAX_CONTENT_LENGTH=524288000
FILE_RETENTION_HOURS=12
HOST=127.0.0.1
PORT=5000
```

## Using External Redis

If using Redis on another server or cloud service:

```env
REDIS_URL=redis://username:password@redis-host:6379/0
# Or with SSL:
REDIS_URL=rediss://username:password@redis-host:6380/0
```

## Different File Locations

If you want to store files on a different drive or mounted volume:

```env
UPLOAD_FOLDER=/mnt/storage/video-subtitler/temp
OUTPUT_FOLDER=/mnt/storage/video-subtitler/output
```

## Shorter File Retention

For environments with limited storage:

```env
FILE_RETENTION_HOURS=6  # Delete after 6 hours
```

## Alternative Google Cloud Credentials

If using environment variable instead of file:

```python
# In config.py, you could modify to use:
GOOGLE_APPLICATION_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
# Then in video_processor.py, load from JSON string
```

## Docker Environment

When using Docker, mount volumes and use container paths:

```env
GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json
REDIS_URL=redis://redis:6379/0
SECRET_KEY=docker-secret-key
FLASK_ENV=production
UPLOAD_FOLDER=/app/temp_files
OUTPUT_FOLDER=/app/output_files
MAX_CONTENT_LENGTH=524288000
FILE_RETENTION_HOURS=24
HOST=0.0.0.0
PORT=5000
```

## Cloud Storage (Future Enhancement)

For using cloud storage like S3 or Google Cloud Storage:

```env
# This would require code modifications
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=video-subtitler-output
```

## Custom Port

If port 5000 is already in use:

```env
PORT=8080
```

## Multiple Languages Support (Future Enhancement)

To support multiple target languages:

```env
DEFAULT_TARGET_LANGUAGE=fa  # Persian/Farsi
SUPPORTED_LANGUAGES=fa,ar,en,es,fr
```

## Processing Limits

To limit concurrent processing:

```python
# In tasks.py, configure Celery:
celery.conf.worker_max_tasks_per_child = 10
celery.conf.task_time_limit = 3600  # 1 hour
celery.conf.task_soft_time_limit = 3000  # 50 minutes
```

## Logging Configuration

For enhanced logging:

```python
# In config.py, add:
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

## Rate Limiting (Future Enhancement)

To prevent abuse:

```python
# Install: pip install Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/process', methods=['POST'])
@limiter.limit("10 per hour")
def process_video():
    # ... existing code
```

## Performance Tuning

### Celery Workers

```bash
# More workers for better concurrency
celery -A tasks.celery worker --concurrency=8 --loglevel=info

# Use prefork pool (default)
celery -A tasks.celery worker --pool=prefork

# Use threads for I/O-bound tasks
celery -A tasks.celery worker --pool=threads
```

### Gunicorn

```bash
# Calculate workers: (2 x CPU cores) + 1
gunicorn -w 9 -b 0.0.0.0:5000 app:app

# With timeout for long requests
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 600 app:app

# With async workers
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 app:app
```

## Security Headers

Add to Flask app:

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Monitoring Integration

For application monitoring:

```env
# Sentry for error tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# New Relic
NEW_RELIC_LICENSE_KEY=your-license-key
```

---

Choose the configuration that best fits your deployment scenario!
