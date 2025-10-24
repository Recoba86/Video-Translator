# 🎬 AI Video Subtitler - Project Overview

## 📚 Complete Project Documentation

This project provides an advanced web service for automatically adding Persian/Farsi subtitles to videos using AI.

### Quick Links

- **[README.md](README.md)** - Full documentation and setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration examples

---

## 📁 Project Structure

```
Video-Translator/
├── 📄 Core Application
│   ├── app.py                    # Flask web server & API endpoints
│   ├── tasks.py                  # Celery background tasks
│   ├── video_processor.py        # Video processing pipeline
│   └── config.py                 # Configuration management
│
├── 🎨 Frontend
│   ├── templates/
│   │   └── index.html           # Main UI (Persian/English)
│   └── static/
│       ├── style.css            # Responsive styling
│       └── script.js            # Frontend logic
│
├── 🔧 Configuration
│   ├── .env.example             # Environment template
│   ├── requirements.txt         # Python dependencies
│   └── .gitignore              # Git ignore rules
│
├── 🚀 Scripts
│   ├── setup.sh                 # Automated setup
│   ├── start.sh                 # Start all services
│   └── test_installation.py    # Installation verification
│
├── 📚 Documentation
│   ├── README.md                # Main documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── DEPLOYMENT.md           # Production deployment
│   └── CONFIGURATION.md        # Configuration examples
│
└── 📦 Data Directories (auto-created)
    ├── temp_files/              # Temporary processing files
    ├── output_files/            # Final subtitled videos
    └── logs/                    # Application logs
```

---

## 🎯 Features Overview

### Core Features
- ✅ Video download from multiple platforms (YouTube, Twitter, etc.)
- ✅ Automatic audio extraction
- ✅ Speech-to-text transcription with language detection
- ✅ Translation to Persian/Farsi
- ✅ Subtitle generation (SRT/ASS formats)
- ✅ Subtitle burn-in to video
- ✅ Real-time progress tracking (5 stages)
- ✅ Video preview and download
- ✅ Automatic file cleanup (24-hour retention)

### User Interface
- ✅ Persian-first design with English support
- ✅ Responsive layout (mobile-friendly)
- ✅ Real-time progress indicators
- ✅ Video player for preview
- ✅ Download and delete buttons
- ✅ Error handling with user-friendly messages

### Technical Features
- ✅ Background job processing (Celery)
- ✅ Redis-based task queue
- ✅ RESTful API endpoints
- ✅ File upload validation
- ✅ Automatic cleanup scheduler
- ✅ Health check endpoint
- ✅ CORS support

---

## 🔄 Processing Pipeline

```
1️⃣ Video URL Input
    ↓
2️⃣ Download Video (yt-dlp)
    ↓
3️⃣ Extract Audio (FFmpeg)
    ↓
4️⃣ Transcribe Audio (Google Speech-to-Text)
    ↓
5️⃣ Translate to Persian (Google Translation)
    ↓
6️⃣ Generate Subtitle File (ASS format)
    ↓
7️⃣ Burn Subtitles (FFmpeg)
    ↓
8️⃣ Preview & Download
    ↓
9️⃣ Auto-cleanup (after 24h)
```

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Core language
- **Flask 3.0** - Web framework
- **Celery 5.3** - Async task queue
- **Redis 5.0** - Message broker

### AI Services
- **Google Cloud Speech-to-Text** - Transcription
- **Google Cloud Translation** - Persian translation

### Media Processing
- **FFmpeg** - Video/audio manipulation
- **yt-dlp** - Video downloading
- **pydub** - Audio processing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with Vazir font
- **Vanilla JavaScript** - Client-side logic

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main UI |
| POST | `/api/process` | Start video processing |
| GET | `/api/status/:task_id` | Check processing status |
| GET | `/api/download/:filename` | Download video |
| GET | `/api/preview/:filename` | Preview video |
| DELETE | `/api/delete/:filename` | Delete video |
| GET | `/api/health` | Health check |

---

## 🚀 Quick Start Commands

```bash
# Setup (one-time)
./setup.sh

# Start application
./start.sh

# Or manually
source venv/bin/activate
python app.py

# Test installation
python test_installation.py

# Stop services
Ctrl+C (if using start.sh)
```

---

## 📊 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB free
- **Network**: Stable internet for API calls

### Recommended
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB (for video processing)
- **Network**: High-speed internet

---

## 🔒 Security Features

- ✅ Environment variable configuration
- ✅ Credential file protection (.gitignore)
- ✅ File size limits (500MB)
- ✅ Automatic file deletion
- ✅ CORS configuration
- ✅ Input validation
- ✅ Error handling without exposing internals

---

## 🌍 Internationalization

### Supported Languages

**Interface**: Persian (RTL) with English fallbacks

**Translation Target**: Persian/Farsi (fa)

**Source Languages**: Auto-detected (any language supported by Google Speech-to-Text)

---

## 📈 Performance Considerations

### Processing Time Estimates
- **1-minute video**: ~2-4 minutes
- **5-minute video**: ~6-12 minutes
- **10-minute video**: ~12-20 minutes

*Times vary based on video quality, audio complexity, and API response times*

### Optimization Tips
1. Use shorter videos for testing
2. Ensure stable internet connection
3. Monitor disk space regularly
4. Configure appropriate retention period
5. Scale Celery workers for concurrent processing

---

## 🧪 Testing

### Quick Test
```bash
python test_installation.py
```

### Manual Test
1. Start the application
2. Use a short YouTube video (1-2 minutes)
3. Monitor console output
4. Check output_files/ directory
5. Preview result in browser

### Example Test URLs
- YouTube: Short educational videos
- Twitter: Public video posts
- Other: Any platform supported by yt-dlp

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Redis connection refused"
**Solution**: Start Redis with `redis-server`

**Issue**: "FFmpeg not found"
**Solution**: Install FFmpeg (see README.md)

**Issue**: "Google API authentication failed"
**Solution**: Check credentials file path in .env

**Issue**: "Port 5000 already in use"
**Solution**: Kill process or change port in .env

**Issue**: "Video download failed"
**Solution**: Verify URL is public and accessible

---

## 🔄 Maintenance

### Daily
- Monitor disk usage
- Check error logs

### Weekly
- Review cleanup effectiveness
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Monthly
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review Google Cloud API usage and costs
- Clear old logs

---

## 📞 Getting Help

1. **Read Documentation**: Start with README.md
2. **Check Logs**: Review logs/ directory
3. **Run Tests**: Use test_installation.py
4. **Search Issues**: Check repository issues
5. **Ask Questions**: Open a new issue

---

## 🎯 Future Enhancements

### Planned Features
- [ ] Multiple target languages
- [ ] Subtitle styling customization
- [ ] Batch processing
- [ ] User authentication
- [ ] Processing history
- [ ] S3/Cloud Storage integration
- [ ] Webhook notifications
- [ ] API rate limiting
- [ ] Advanced error recovery

### Suggestions Welcome!
Open an issue to suggest new features.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Credits

**Built with**:
- Google Cloud AI Services
- FFmpeg project
- yt-dlp team
- Flask and Celery communities
- Vazir Persian font

**Made with ❤️ using AI**

---

## 📌 Version

**Current Version**: 1.0.0
**Last Updated**: October 2025

---

**Ready to translate videos? Start with [QUICKSTART.md](QUICKSTART.md)! 🚀**
