# Frequently Asked Questions (FAQ)

## General Questions

### What is this application?
This is an AI-powered web service that automatically adds Persian/Farsi subtitles to videos. It downloads videos, transcribes the audio, translates the text to Persian, and burns the subtitles directly into the video.

### What video platforms are supported?
The service supports YouTube, Twitter (X), and many other platforms via yt-dlp. Most public video URLs should work.

### Is this free to use?
The software is free and open-source. However, you need a Google Cloud account, which requires billing. Google offers free tiers for both APIs used:
- Speech-to-Text: 60 minutes/month free
- Translation: 500,000 characters/month free

### How long does processing take?
Processing time depends on video length and complexity:
- 1-minute video: ~2-4 minutes
- 5-minute video: ~6-12 minutes
- 10-minute video: ~12-20 minutes

### What languages can be transcribed?
Google Speech-to-Text supports 125+ languages. The source language is automatically detected.

### Can I translate to languages other than Persian?
Currently, the system is configured for Persian only. However, the code can be modified to support other languages (see CONFIGURATION.md).

## Installation Issues

### Q: "Python not found" or wrong version?
**A:** Install Python 3.8 or higher:
```bash
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Check version
python3 --version
```

### Q: "FFmpeg not found"?
**A:** Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

### Q: "Redis connection refused"?
**A:** Start Redis server:
```bash
# Start Redis
redis-server

# Or as background service (macOS)
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis-server

# Verify
redis-cli ping  # Should return PONG
```

### Q: Virtual environment activation fails?
**A:** Ensure you're using the correct command:
```bash
# macOS/Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### Q: pip install fails with permission errors?
**A:** Make sure you're in the virtual environment, or use --user flag:
```bash
# Activate virtual environment first
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

## Google Cloud Issues

### Q: "Google API authentication failed"?
**A:** Check these steps:
1. Verify `google-credentials.json` exists
2. Check path in `.env` is correct
3. Ensure the JSON file is valid (not corrupted)
4. Verify service account has correct permissions

```bash
# Test credentials
export GOOGLE_APPLICATION_CREDENTIALS="./google-credentials.json"
python -c "from google.cloud import speech; client = speech.SpeechClient()"
```

### Q: "API not enabled" error?
**A:** Enable required APIs in Google Cloud Console:
```bash
gcloud services enable speech.googleapis.com
gcloud services enable translate.googleapis.com
```

Or visit:
- https://console.cloud.google.com/apis/library/speech.googleapis.com
- https://console.cloud.google.com/apis/library/translate.googleapis.com

### Q: "Billing not enabled" error?
**A:** Enable billing on your Google Cloud project:
1. Go to https://console.cloud.google.com/billing
2. Link a billing account to your project
3. Note: You won't be charged if you stay within free tier limits

### Q: How much will Google Cloud cost?
**A:** Pricing (as of 2025):
- **Speech-to-Text**: $0.006 per 15 seconds after free tier
- **Translation**: $20 per million characters after free tier
- **Free tier**: 60 minutes STT + 500k characters translation/month

Example: A 10-minute video might cost $0.04-0.10 if beyond free tier.

### Q: Service account permissions?
**A:** Your service account needs these roles:
- Cloud Speech Client
- Cloud Translation API User

## Runtime Issues

### Q: Video download fails?
**A:** Possible causes:
1. **Invalid URL**: Ensure the URL is public and accessible
2. **yt-dlp outdated**: Update with `pip install --upgrade yt-dlp`
3. **Platform restrictions**: Some videos may be region-locked or private
4. **Network issues**: Check your internet connection

### Q: Processing gets stuck?
**A:** Check these:
1. **Celery worker running**: Check if worker is active
2. **Redis running**: Verify with `redis-cli ping`
3. **Google API quotas**: Check if you've exceeded limits
4. **Disk space**: Ensure sufficient storage
5. **Check logs**: `tail -f logs/celery_worker.log`

### Q: "Port 5000 already in use"?
**A:** Find and kill the process:
```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
lsof -ti:5000 | xargs kill -9

# Or change port in .env
PORT=8080
```

### Q: Video preview doesn't load?
**A:** Check:
1. **File exists**: Verify file in `output_files/`
2. **Browser compatibility**: Try another browser
3. **File size**: Large files may take time to load
4. **MIME type**: Ensure video/mp4 is supported

### Q: Subtitle timing is off?
**A:** This can happen if:
1. **Video has intro music**: Google API starts timing from first speech
2. **Audio quality is poor**: Try with better quality video
3. **Multiple languages**: Source detection may be confused

### Q: Translation quality is poor?
**A:** Factors affecting translation:
1. **Context**: Google Translate works better with longer segments
2. **Technical terms**: May not translate well
3. **Slang/idioms**: May be translated literally
4. **Audio quality**: Poor transcription = poor translation

## Performance Issues

### Q: Processing is very slow?
**A:** Optimize:
1. **Internet speed**: Google API calls require good connection
2. **System resources**: Ensure adequate RAM and CPU
3. **Concurrent tasks**: Too many may slow down processing
4. **Video quality**: Lower resolution processes faster

### Q: Disk space filling up?
**A:** Solutions:
1. **Reduce retention**: Lower `FILE_RETENTION_HOURS` in `.env`
2. **Manual cleanup**: Delete old files from `output_files/`
3. **Check cleanup**: Ensure Celery Beat is running for auto-cleanup
4. **Monitor usage**: Set up alerts for disk space

### Q: Memory issues?
**A:** Try:
1. **Reduce workers**: Lower Gunicorn `-w` count
2. **Celery concurrency**: Reduce `--concurrency` value
3. **Video size limits**: Lower `MAX_CONTENT_LENGTH` in `.env`
4. **Restart services**: Clear memory leaks

## Celery Issues

### Q: Celery worker not picking up tasks?
**A:** Check:
```bash
# Verify worker is running
ps aux | grep celery

# Check Redis connection
redis-cli ping

# Restart worker
pkill -f celery
celery -A tasks.celery worker --loglevel=info
```

### Q: "Received unregistered task" error?
**A:** This means Celery can't find the task. Fix:
1. Restart Celery worker
2. Ensure `tasks.py` is in the correct location
3. Check for syntax errors in `tasks.py`

### Q: Tasks failing silently?
**A:** Increase logging:
```bash
celery -A tasks.celery worker --loglevel=debug
```

Check logs in `logs/celery_worker.log`

## Frontend Issues

### Q: Persian text displays incorrectly?
**A:** Ensure:
1. Browser supports RTL text
2. Vazir font loads correctly
3. UTF-8 encoding is set

### Q: Progress bar doesn't update?
**A:** Check:
1. JavaScript console for errors (F12)
2. Network tab shows polling requests
3. CORS is configured correctly
4. Backend status endpoint works: `curl http://localhost:5000/api/status/test`

### Q: Download button doesn't work?
**A:** Verify:
1. File exists in `output_files/`
2. No browser popup blocker
3. Check browser console (F12) for errors

## Production Issues

### Q: Service crashes frequently?
**A:** Common causes:
1. **Memory leaks**: Restart services regularly
2. **Unhandled errors**: Check logs
3. **Resource limits**: Increase system resources
4. **Dependency issues**: Update all packages

### Q: How to monitor the service?
**A:** Use:
1. **Health endpoint**: Monitor `/api/health`
2. **System monitoring**: Prometheus, Grafana
3. **Log aggregation**: ELK stack, Splunk
4. **Uptime monitoring**: UptimeRobot, Pingdom

### Q: How to scale for more users?
**A:** Scaling strategies:
1. **Horizontal**: Run multiple Celery workers
2. **Load balancing**: Use Nginx/HAProxy for Flask
3. **Redis cluster**: For high availability
4. **Cloud storage**: Use S3 for files
5. **CDN**: For serving videos

### Q: SSL/HTTPS setup?
**A:** Use Let's Encrypt with Nginx:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

See DEPLOYMENT.md for full configuration.

## Troubleshooting Commands

### Check all services
```bash
# Redis
redis-cli ping

# Flask
curl http://localhost:5000/api/health

# Celery worker
celery -A tasks.celery inspect active

# Processes
ps aux | grep -E 'celery|flask|redis'
```

### View logs
```bash
# Flask
tail -f logs/flask.log

# Celery
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log

# Follow multiple logs
tail -f logs/*.log
```

### Test installation
```bash
python test_installation.py
```

### Clear Redis cache
```bash
redis-cli FLUSHALL
```

### Reset everything
```bash
# Stop all services
pkill -f celery
pkill -f flask
redis-cli shutdown

# Clear files
rm -rf temp_files/* output_files/* logs/*.log

# Restart
./start.sh
```

## Getting Help

### Where to find more information?
- **README.md**: Complete documentation
- **QUICKSTART.md**: Fast setup guide
- **DEPLOYMENT.md**: Production deployment
- **ARCHITECTURE.md**: System design
- **CONFIGURATION.md**: Config examples

### Logs location?
- Flask: `logs/flask.log`
- Celery Worker: `logs/celery_worker.log`
- Celery Beat: `logs/celery_beat.log`

### How to report bugs?
1. Check existing issues
2. Gather information:
   - Error message
   - Logs
   - Steps to reproduce
   - System information
3. Open an issue on the repository

### How to contribute?
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Advanced Questions

### Q: Can I use Whisper instead of Google Speech-to-Text?
**A:** Yes! Modify `video_processor.py` to use OpenAI's Whisper:
```python
import whisper
model = whisper.load_model("base")
result = model.transcribe(audio_path)
```

### Q: Can I add custom subtitle styling?
**A:** Yes! Edit the ASS header in `generate_ass()` method in `video_processor.py`.

### Q: Can I process multiple videos simultaneously?
**A:** Yes! Run multiple Celery workers:
```bash
celery -A tasks.celery worker --concurrency=4 --loglevel=info
```

### Q: Can I use this offline?
**A:** Partially. You'd need to replace Google APIs with local models (Whisper for STT, local NMT for translation).

### Q: Can I change subtitle language?
**A:** Yes! Modify the `target_language` parameter in `tasks.py` when calling `translate_segments()`.

### Q: Can I export subtitle files separately?
**A:** Yes! Modify the code to also return the .ass/.srt file without burning it into the video.

---

## Still Have Questions?

If your question isn't answered here:
1. Check the documentation in `docs/` folder
2. Search existing issues
3. Open a new issue with details
4. Contact support (if available)

---

**Happy subtitling! 🎬**
