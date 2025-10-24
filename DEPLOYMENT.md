# Production Deployment Guide

## Option 1: Using Docker (Recommended)

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp_files output_files logs

# Expose port
EXPOSE 5000

# Default command
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: .
    command: celery -A tasks.celery worker --loglevel=info
    volumes:
      - ./temp_files:/app/temp_files
      - ./output_files:/app/output_files
      - ./google-credentials.json:/app/google-credentials.json
    env_file:
      - .env
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A tasks.celery beat --loglevel=info
    volumes:
      - ./temp_files:/app/temp_files
      - ./output_files:/app/output_files
    env_file:
      - .env
    depends_on:
      - redis

  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./temp_files:/app/temp_files
      - ./output_files:/app/output_files
      - ./google-credentials.json:/app/google-credentials.json
    env_file:
      - .env
    depends_on:
      - redis
      - celery_worker

volumes:
  redis_data:
```

### Deploy with Docker Compose

```bash
docker-compose up -d
```

## Option 2: Systemd Services (Linux)

### Flask Service

Create `/etc/systemd/system/video-subtitler-web.service`:

```ini
[Unit]
Description=Video Subtitler Web Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/video-subtitler
Environment="PATH=/var/www/video-subtitler/venv/bin"
ExecStart=/var/www/video-subtitler/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Celery Worker Service

Create `/etc/systemd/system/video-subtitler-celery.service`:

```ini
[Unit]
Description=Video Subtitler Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/video-subtitler
Environment="PATH=/var/www/video-subtitler/venv/bin"
ExecStart=/var/www/video-subtitler/venv/bin/celery -A tasks.celery worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Celery Beat Service

Create `/etc/systemd/system/video-subtitler-beat.service`:

```ini
[Unit]
Description=Video Subtitler Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/video-subtitler
Environment="PATH=/var/www/video-subtitler/venv/bin"
ExecStart=/var/www/video-subtitler/venv/bin/celery -A tasks.celery beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable video-subtitler-web video-subtitler-celery video-subtitler-beat
sudo systemctl start video-subtitler-web video-subtitler-celery video-subtitler-beat
```

### Check Status

```bash
sudo systemctl status video-subtitler-web
sudo systemctl status video-subtitler-celery
sudo systemctl status video-subtitler-beat
```

## Option 3: Supervisor (Cross-platform)

Install Supervisor:
```bash
pip install supervisor
```

Create `supervisord.conf`:

```ini
[supervisord]
nodaemon=false
logfile=logs/supervisord.log

[program:celery_worker]
command=/path/to/venv/bin/celery -A tasks.celery worker --loglevel=info
directory=/path/to/video-subtitler
stdout_logfile=logs/celery_worker.log
stderr_logfile=logs/celery_worker_err.log
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A tasks.celery beat --loglevel=info
directory=/path/to/video-subtitler
stdout_logfile=logs/celery_beat.log
stderr_logfile=logs/celery_beat_err.log
autostart=true
autorestart=true

[program:flask_app]
command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
directory=/path/to/video-subtitler
stdout_logfile=logs/flask.log
stderr_logfile=logs/flask_err.log
autostart=true
autorestart=true
```

Start Supervisor:
```bash
supervisord -c supervisord.conf
```

Control services:
```bash
supervisorctl status
supervisorctl restart all
```

## Nginx Configuration

Create `/etc/nginx/sites-available/video-subtitler`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long processing
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    location /static {
        alias /var/www/video-subtitler/static;
        expires 30d;
    }

    location /api/preview {
        proxy_pass http://127.0.0.1:5000;
        proxy_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/video-subtitler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables for Production

Update `.env` for production:

```env
FLASK_ENV=production
SECRET_KEY=generate-a-strong-random-key-here
HOST=127.0.0.1
PORT=5000
FILE_RETENTION_HOURS=12
```

## Monitoring

### Log Rotation

Create `/etc/logrotate.d/video-subtitler`:

```
/var/www/video-subtitler/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

### Health Checks

Monitor the health endpoint:
```bash
curl http://localhost:5000/api/health
```

Set up external monitoring (e.g., UptimeRobot, Pingdom) to check this endpoint.

## Security Considerations

1. **Firewall**: Only expose necessary ports (80, 443)
2. **Rate Limiting**: Implement rate limiting in Nginx
3. **File Upload Limits**: Already configured in Flask
4. **Environment Variables**: Never commit `.env` or credentials
5. **User Permissions**: Run services as non-root user
6. **HTTPS**: Always use SSL in production
7. **Google Cloud**: Restrict API keys to specific IPs if possible

## Scaling

### Horizontal Scaling

- Run multiple Celery workers on different machines
- Use a load balancer (HAProxy, AWS ELB) for Flask instances
- Use shared storage (NFS, S3) for temp and output files

### Vertical Scaling

- Increase Gunicorn workers: `-w` parameter
- Increase Celery concurrency: `--concurrency` parameter
- Allocate more resources to Redis

## Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz \
    .env \
    google-credentials.json \
    output_files/ \
    logs/
```

## Troubleshooting Production

```bash
# Check logs
tail -f logs/flask.log
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log

# Check Redis
redis-cli ping
redis-cli INFO

# Check disk space
df -h

# Check processes
ps aux | grep celery
ps aux | grep gunicorn
```

---

**Your service is now production-ready! 🚀**
