# 🚀 Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:

- ✅ Python 3.8+
- ✅ FFmpeg
- ✅ Redis
- ✅ Google Cloud account with Speech-to-Text & Translation APIs enabled

## Fast Setup (3 minutes)

### 1. Run Automated Setup

```bash
./setup.sh
```

This will:
- Check all prerequisites
- Create virtual environment
- Install dependencies
- Setup configuration files

### 2. Configure Google Cloud

1. Download your Google Cloud service account JSON key
2. Save it as `google-credentials.json` in the project root
3. Edit `.env` if needed to update the path

### 3. Start the Application

```bash
./start.sh
```

This single command starts:
- ✅ Redis (if not running)
- ✅ Celery Worker
- ✅ Celery Beat
- ✅ Flask App

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## Manual Setup (if automated setup fails)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env
# Edit .env with your settings

# 4. Create directories
mkdir -p temp_files output_files logs

# 5. Start services (in separate terminals)
# Terminal 1:
redis-server

# Terminal 2:
celery -A tasks.celery worker --loglevel=info

# Terminal 3:
celery -A tasks.celery beat --loglevel=info

# Terminal 4:
python app.py
```

## Testing the Service

1. Open http://localhost:5000
2. Enter a YouTube video URL (e.g., a short video for testing)
3. Click "شروع پردازش" (Start Processing)
4. Watch the progress through 5 stages
5. Preview and download the subtitled video

## Recommended Test Videos

For initial testing, use short videos (1-2 minutes):
- YouTube short videos
- Public Twitter/X videos
- Any platform supported by yt-dlp

## Stopping the Service

If you used `./start.sh`:
- Press `Ctrl+C` in the terminal

If you started manually:
- Stop each terminal with `Ctrl+C`

## Troubleshooting

### "Redis connection refused"
```bash
redis-server --daemonize yes
```

### "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### "Google API authentication failed"
Check that:
1. `google-credentials.json` exists in project root
2. Path in `.env` is correct
3. APIs are enabled in Google Cloud Console
4. Billing is enabled on your Google Cloud project

### Port 5000 already in use
```bash
lsof -ti:5000 | xargs kill -9
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Configure automatic cleanup settings in `.env`
- Set up production deployment (see README.md)

## Support

For issues:
1. Check logs in the `logs/` directory
2. Verify all prerequisites are installed
3. Ensure Google Cloud APIs are properly configured
4. Open an issue on the repository

---

**Ready to translate videos? Let's go! 🎬**
