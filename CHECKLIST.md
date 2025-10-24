# Deployment Checklist

Use this checklist to ensure your AI Video Subtitler is properly set up and ready for use.

## ✅ Pre-Installation Checklist

### System Requirements
- [ ] Python 3.8 or higher installed
  ```bash
  python3 --version
  ```
- [ ] FFmpeg installed
  ```bash
  ffmpeg -version
  ```
- [ ] Redis installed
  ```bash
  redis-cli --version
  ```
- [ ] Git installed (for cloning)
  ```bash
  git --version
  ```

### Google Cloud Setup
- [ ] Google Cloud account created
- [ ] Project created in Google Cloud Console
- [ ] Billing enabled on the project
- [ ] Speech-to-Text API enabled
- [ ] Translation API enabled
- [ ] Service account created with appropriate roles
- [ ] JSON credentials file downloaded

### System Resources
- [ ] At least 10 GB free disk space
- [ ] At least 4 GB RAM available
- [ ] Stable internet connection
- [ ] Appropriate ports available (5000, 6379)

## ✅ Installation Checklist

### Environment Setup
- [ ] Virtual environment created
  ```bash
  python3 -m venv venv
  ```
- [ ] Virtual environment activated
  ```bash
  source venv/bin/activate  # macOS/Linux
  # or
  venv\Scripts\activate     # Windows
  ```
- [ ] Dependencies installed
  ```bash
  pip install -r requirements.txt
  ```

### Configuration
- [ ] `.env` file created from `.env.example`
  ```bash
  cp .env.example .env
  ```
- [ ] `google-credentials.json` placed in project root
- [ ] `.env` updated with correct paths
- [ ] Secret key generated and set
- [ ] Redis URL configured correctly

### Directory Structure
- [ ] `temp_files/` directory created or will be auto-created
- [ ] `output_files/` directory created or will be auto-created
- [ ] `logs/` directory created
- [ ] `static/` directory exists with CSS and JS
- [ ] `templates/` directory exists with HTML

### Scripts
- [ ] `setup.sh` made executable
  ```bash
  chmod +x setup.sh
  ```
- [ ] `start.sh` made executable
  ```bash
  chmod +x start.sh
  ```

## ✅ Testing Checklist

### Installation Test
- [ ] Run installation test script
  ```bash
  python test_installation.py
  ```
- [ ] All checks passed

### Service Startup
- [ ] Redis server started
  ```bash
  redis-server
  # or
  brew services start redis
  ```
- [ ] Celery worker starts without errors
  ```bash
  celery -A tasks.celery worker --loglevel=info
  ```
- [ ] Celery beat starts without errors
  ```bash
  celery -A tasks.celery beat --loglevel=info
  ```
- [ ] Flask application starts without errors
  ```bash
  python app.py
  ```

### Connectivity Tests
- [ ] Redis connection works
  ```bash
  redis-cli ping  # Should return PONG
  ```
- [ ] Flask responds to health check
  ```bash
  curl http://localhost:5000/api/health
  ```
- [ ] Web interface loads in browser
  ```
  Open: http://localhost:5000
  ```

### Functional Tests
- [ ] Submit a test video URL (use a short video)
- [ ] Progress indicators update correctly
- [ ] All 5 stages complete successfully
- [ ] Video preview loads and plays
- [ ] Download button works
- [ ] Delete button works
- [ ] Error handling works (try invalid URL)

## ✅ Production Deployment Checklist

### Security
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Secure Google credentials file permissions
  ```bash
  chmod 600 google-credentials.json
  ```
- [ ] Add firewall rules (if applicable)
- [ ] Configure HTTPS/SSL
- [ ] Set up proper user permissions
- [ ] Review and restrict API access

### Performance
- [ ] Configure appropriate number of Gunicorn workers
- [ ] Set up Celery worker concurrency
- [ ] Configure Redis memory limits
- [ ] Set appropriate file retention period
- [ ] Monitor disk space

### Monitoring
- [ ] Set up log rotation
- [ ] Configure application logs
- [ ] Set up health check monitoring
- [ ] Configure alerts for errors
- [ ] Monitor API usage and costs

### Process Management
- [ ] Configure systemd services (Linux)
- [ ] Or configure Supervisor
- [ ] Or set up Docker containers
- [ ] Ensure services auto-restart on failure
- [ ] Verify services start on boot

### Reverse Proxy (if using)
- [ ] Nginx/Apache configured
- [ ] SSL certificates installed
- [ ] Proxy settings tested
- [ ] Upload size limits set
- [ ] Timeout values configured

### Backup
- [ ] Backup strategy defined
- [ ] `.env` file backed up securely
- [ ] Google credentials backed up securely
- [ ] Documentation backed up

## ✅ Maintenance Checklist

### Daily
- [ ] Check disk space
  ```bash
  df -h
  ```
- [ ] Review error logs
  ```bash
  tail -f logs/flask.log
  tail -f logs/celery_worker.log
  ```
- [ ] Verify automatic cleanup is working

### Weekly
- [ ] Review Google Cloud API usage
- [ ] Check for yt-dlp updates
  ```bash
  pip install --upgrade yt-dlp
  ```
- [ ] Monitor system resources

### Monthly
- [ ] Update Python dependencies
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- [ ] Review and optimize file retention settings
- [ ] Check for security updates
- [ ] Review logs for patterns or issues
- [ ] Test disaster recovery procedures

## ✅ Documentation Checklist

- [ ] README.md reviewed
- [ ] QUICKSTART.md reviewed
- [ ] DEPLOYMENT.md reviewed (for production)
- [ ] CONFIGURATION.md reviewed for your setup
- [ ] ARCHITECTURE.md understood
- [ ] Team members trained (if applicable)
- [ ] Support documentation created (if needed)

## ✅ User Acceptance Checklist

### Functionality
- [ ] Video downloads work from multiple sources
- [ ] Transcription accuracy is acceptable
- [ ] Translation quality meets requirements
- [ ] Subtitle timing is accurate
- [ ] Video quality is preserved
- [ ] Processing time is acceptable

### User Experience
- [ ] Interface is intuitive
- [ ] Progress updates are clear
- [ ] Error messages are helpful
- [ ] Video preview works smoothly
- [ ] Download process is simple
- [ ] Mobile experience is acceptable (if required)

### Reliability
- [ ] Service recovers from errors
- [ ] Cleanup works as expected
- [ ] Multiple concurrent requests handled
- [ ] Long videos process successfully
- [ ] System remains stable under load

## ✅ Rollback Plan

- [ ] Backup of working configuration available
- [ ] Rollback procedure documented
- [ ] Database backup (if using one)
- [ ] Know how to stop all services quickly
- [ ] Contact information for support ready

## ✅ Go-Live Checklist

- [ ] All above checklists completed
- [ ] Stakeholders notified
- [ ] Support team briefed
- [ ] Documentation accessible
- [ ] Monitoring active
- [ ] Backup verified
- [ ] SSL certificate valid
- [ ] Domain configured (if applicable)
- [ ] Final testing completed
- [ ] Performance baseline established

---

## Quick Reference Commands

### Start Services (Automated)
```bash
./start.sh
```

### Start Services (Manual)
```bash
# Terminal 1
redis-server

# Terminal 2
celery -A tasks.celery worker --loglevel=info

# Terminal 3
celery -A tasks.celery beat --loglevel=info

# Terminal 4
python app.py
```

### Check Status
```bash
# Redis
redis-cli ping

# Flask
curl http://localhost:5000/api/health

# Processes
ps aux | grep -E 'celery|flask|redis'
```

### Stop Services
```bash
# If using start.sh
Ctrl+C in the terminal

# Manual
pkill -f celery
pkill -f flask
redis-cli shutdown
```

### View Logs
```bash
tail -f logs/flask.log
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log
```

---

## Sign-off

- [ ] Development Lead: _________________ Date: _______
- [ ] QA Team: _________________ Date: _______
- [ ] Security Review: _________________ Date: _______
- [ ] Operations Team: _________________ Date: _______

---

**Congratulations! Your AI Video Subtitler is ready! 🎉**
