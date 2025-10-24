# 🔧 Troubleshooting Common Issues

## Issue 1: "Task not found" Error

**Symptom**: UI shows "Task not found" with 0% progress

**Cause**: Celery worker not running

**Solution**:
```bash
# Terminal 1: Start Celery
source venv/bin/activate
celery -A tasks worker --loglevel=info
```

---

## Issue 2: YouTube Download Fails (HTTP 403/400)

**Symptom**: Celery logs show "HTTP Error 403: Forbidden" or "HTTP Error 400: Bad Request"

**Causes**:
1. **yt-dlp is outdated** - YouTube frequently changes their API
2. **YouTube Shorts** - Sometimes have stricter restrictions
3. **Rate limiting** - Too many requests from your IP

**Solutions**:

### Solution 1: Update yt-dlp (Recommended)
```bash
source venv/bin/activate
pip install --upgrade yt-dlp
```

### Solution 2: Try Regular YouTube Videos
Instead of YouTube Shorts (`/shorts/`), try regular videos:
- ❌ https://www.youtube.com/shorts/4dA2u_PhCp4
- ✅ https://www.youtube.com/watch?v=dQw4w9WgXcQ

### Solution 3: Use Alternative Sources
Try videos from other platforms:
- Vimeo
- Direct MP4 links
- Other video hosting services

### Solution 4: Add Cookies (Advanced)
If YouTube persists blocking:

1. Get your YouTube cookies:
   - Install browser extension: "Get cookies.txt"
   - Visit YouTube
   - Export cookies to `cookies.txt`

2. Update `video_processor_gemini.py`:
   ```python
   'cookies': 'cookies.txt'  # Add to yt-dlp options
   ```

---

## Issue 3: Port 5000 Already in Use

**Symptom**: "Access to localhost was denied" or "Address already in use"

**Cause**: macOS Control Center or AirPlay uses port 5000

**Solution**: Use port 8000 instead (already configured in `.env`)

---

## Issue 4: Redis Connection Failed

**Symptom**: "Error connecting to Redis" or "Connection refused"

**Solution**:
```bash
# Check Redis status
brew services list | grep redis

# Start Redis
brew services start redis

# Test connection
redis-cli ping
# Should return: PONG
```

---

## Issue 5: Flask-CORS Import Error

**Symptom**: "ModuleNotFoundError: No module named 'flask_cors'"

**Solution**:
```bash
source venv/bin/activate
pip install flask-cors
```

---

## Issue 6: Whisper Installation Fails (Mac ARM)

**Symptom**: Error installing openai-whisper on Apple Silicon

**Solution**:
```bash
source venv/bin/activate

# Install PyTorch first
pip install torch torchvision torchaudio

# Then install Whisper
pip install openai-whisper
```

---

## Issue 7: "Task Started" but No Progress

**Symptom**: Task shows as started but stuck at 0%

**Possible Causes**:
1. Celery worker crashed
2. Video download is slow
3. Large video file

**Solutions**:

### Check Celery Logs
Look at the Celery terminal for errors

### Check Disk Space
```bash
df -h
```

### Try Shorter Video
Test with a 1-2 minute video first

---

## Issue 8: Gemini API Key Invalid

**Symptom**: "API key not valid" or "Authentication failed"

**Solution**:

1. Verify API key:
   ```bash
   cat .env | grep GEMINI_API_KEY
   ```

2. Get new key from: https://aistudio.google.com/app/apikey

3. Update `.env`:
   ```bash
   nano .env
   # Update GEMINI_API_KEY=your_new_key_here
   ```

4. Restart Flask:
   ```bash
   # Ctrl+C in Flask terminal, then:
   source venv/bin/activate && python app.py
   ```

---

## Issue 9: Subtitle Not Showing in Video

**Symptom**: Video downloads but no subtitles visible

**Causes**:
1. Subtitles burned incorrectly
2. FFmpeg error
3. Video codec issue

**Solutions**:

### Check FFmpeg
```bash
ffmpeg -version
```

### Check Output Files
```bash
ls -lh output/
```

### Try Different Video Format
Some formats work better than others

---

## Issue 10: Slow Processing

**Symptom**: Takes very long to process short videos

**Expected Times** (on Mac ARM M1/M2):
- **1 min video**: ~30-45 seconds
- **5 min video**: ~2-3 minutes
- **10 min video**: ~5-6 minutes

**Optimization Tips**:

1. **First run is slower** - Whisper downloads model (139MB)
2. **Close other apps** - Free up RAM
3. **Check Activity Monitor** - Ensure not using Rosetta
4. **Use wired connection** - Faster download

---

## Quick Diagnostic Commands

```bash
# Check all services
brew services list

# Check Python packages
source venv/bin/activate && pip list

# Check ports in use
lsof -i :5000
lsof -i :6379
lsof -i :8000

# Check Redis
redis-cli ping

# Check yt-dlp version
source venv/bin/activate && yt-dlp --version

# Test YouTube download
source venv/bin/activate && yt-dlp --print filename "VIDEO_URL"

# Check disk space
df -h

# Check Celery queue
redis-cli
> KEYS celery*
> exit
```

---

## Getting Help

If issues persist:

1. **Check Celery logs** - Look for specific error messages
2. **Check Flask logs** - See `logs/flask.log`
3. **Try simple test**: Short video, regular YouTube URL
4. **Restart everything**:
   ```bash
   # Stop all (Ctrl+C in each terminal)
   brew services restart redis
   source venv/bin/activate && celery -A tasks worker --loglevel=info
   source venv/bin/activate && python app.py
   ```

---

## Common Error Messages Explained

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| `HTTP Error 403: Forbidden` | YouTube blocking download | Update yt-dlp, try different video |
| `HTTP Error 400: Bad Request` | Invalid request to YouTube | Update yt-dlp |
| `Connection refused` | Service not running | Start Redis/Celery |
| `Task not found` | Celery not connected | Start Celery worker |
| `ModuleNotFoundError` | Package not installed | `pip install package_name` |
| `Port already in use` | Another service using port | Change port or kill process |
| `API key not valid` | Wrong/expired Gemini key | Get new key from AI Studio |
| `Out of memory` | Video too large | Try smaller video |

---

## Test Video URLs (Known to Work)

These URLs are tested and should work:

```
# Short test videos (< 1 minute)
https://www.youtube.com/watch?v=jNQXAC9IVRw  # "Me at the zoo" - First YouTube video
https://www.youtube.com/watch?v=aqz-KE-bpKQ  # Short educational video

# Medium videos (2-5 minutes)
https://www.youtube.com/watch?v=9bZkp7q19f0  # PSY - GANGNAM STYLE

# Note: Avoid YouTube Shorts for testing - they have more restrictions
```

---

## Success Checklist

Before reporting an issue, verify:

- [ ] Redis is running (`redis-cli ping` returns PONG)
- [ ] Celery worker is running (see terminal output)
- [ ] Flask is running (http://localhost:8000 loads)
- [ ] Virtual environment is activated
- [ ] All packages installed (`pip list`)
- [ ] .env file has GEMINI_API_KEY
- [ ] yt-dlp is up to date (`yt-dlp --version`)
- [ ] Tried with regular YouTube video (not Shorts)
- [ ] Checked Celery logs for errors
- [ ] Have enough disk space (at least 1GB free)

---

**Still having issues?** Check the Celery terminal output - it shows the actual error!
