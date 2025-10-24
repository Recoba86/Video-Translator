# 🍎 Mac ARM (Apple Silicon) Setup Guide

Complete installation guide for Mac with Apple Silicon (M1/M2/M3/M4).

## 📋 Quick Start

### One-Command Installation

```bash
chmod +x install_mac_arm.sh && ./install_mac_arm.sh
```

That's it! The script will automatically:
- ✅ Install Homebrew (if needed)
- ✅ Install Python 3.11 (ARM-optimized)
- ✅ Install FFmpeg (ARM-optimized)
- ✅ Install Redis
- ✅ Create virtual environment
- ✅ Install all Python packages (ARM-compatible versions)
- ✅ Set up directories
- ✅ Create launch scripts
- ✅ Test everything

---

## 🚀 After Installation

### Step 1: Configure API Key

Edit the `.env` file:

```bash
nano .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=AIzaSyDErRp1HpEHJVsc5OLM1I88haAAqdIRu5g
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

### Step 2: Start Services

You have **two options**:

#### Option A: All-in-One (Recommended)

```bash
./start.sh
```

This starts Redis, Celery, and Flask in the background.

#### Option B: Separate Terminals (For Debugging)

Open 3 terminal tabs/windows:

**Terminal 1 - Redis:**
```bash
./start_redis.sh
```

**Terminal 2 - Celery:**
```bash
./start_celery.sh
```

**Terminal 3 - Flask:**
```bash
./start_flask.sh
```

### Step 3: Open Browser

Go to: **http://localhost:5000**

---

## 🔍 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
brew services list

# Restart Redis
brew services restart redis

# Test Redis
redis-cli ping
# Should return: PONG
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Whisper Installation Issues (ARM-specific)

If Whisper installation fails:

```bash
# Activate venv
source venv/bin/activate

# Install PyTorch for ARM first
pip install torch torchvision torchaudio

# Then install Whisper
pip install openai-whisper
```

### FFmpeg Not Found

```bash
# Install FFmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Permission Denied on Scripts

```bash
# Make scripts executable
chmod +x install_mac_arm.sh
chmod +x start.sh
chmod +x start_redis.sh
chmod +x start_celery.sh
chmod +x start_flask.sh
```

---

## 🎯 What Gets Installed

### System Tools (via Homebrew)
- **Homebrew**: Package manager for macOS
- **Python 3.11**: Optimized for Apple Silicon
- **FFmpeg**: Video processing (ARM-optimized build)
- **Redis**: Background job queue

### Python Packages (ARM-compatible)
- **Flask 3.0**: Web framework
- **Celery 5.3.4**: Background task processing
- **Redis 5.0.1**: Python Redis client
- **yt-dlp**: Video downloader
- **Whisper**: Speech-to-text (ARM-optimized)
- **Google Generative AI**: Gemini API
- **PyTorch**: ML framework (ARM-optimized)
- **FFmpeg-Python**: Video manipulation

---

## 📁 Directory Structure

After installation:

```
Video-Translator/
├── venv/              # Virtual environment
├── temp/              # Temporary video files
├── output/            # Processed videos with subtitles
├── logs/              # Application logs
├── .env               # Your API keys (DO NOT COMMIT)
├── install_mac_arm.sh # Installation script
├── start.sh           # Start all services
├── start_redis.sh     # Start Redis only
├── start_celery.sh    # Start Celery only
├── start_flask.sh     # Start Flask only
└── ...
```

---

## 🔧 Apple Silicon Optimizations

This setup is specifically optimized for ARM64:

1. **Native ARM Builds**: Homebrew packages are ARM-native
2. **PyTorch ARM**: Uses Metal acceleration for faster processing
3. **Whisper ARM**: Optimized for Apple Silicon
4. **Python 3.11**: Best performance on M-series chips

### Performance Benefits

- **Whisper transcription**: 2-3x faster on ARM vs x86 emulation
- **Video processing**: Native FFmpeg ARM build
- **Lower power consumption**: No Rosetta translation overhead

---

## 🧪 Testing Installation

Run the test script:

```bash
python test_installation.py
```

This checks:
- ✅ Python environment
- ✅ All required packages
- ✅ Redis connection
- ✅ FFmpeg availability
- ✅ Directory structure
- ✅ API configuration

---

## 🆘 Getting Help

### Check Service Status

```bash
# Check Redis
brew services list | grep redis

# Check if ports are in use
lsof -i :5000  # Flask
lsof -i :6379  # Redis
```

### View Logs

```bash
# Flask logs
tail -f logs/flask.log

# Celery logs
tail -f logs/celery.log
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 5000 already in use | Kill process: `lsof -ti:5000 \| xargs kill -9` |
| Redis won't start | `brew services restart redis` |
| Import errors | Reinstall packages: `pip install -r requirements.txt` |
| Whisper slow | Check Activity Monitor for Rosetta process |

---

## 📊 System Requirements

- **macOS**: Big Sur (11.0) or later
- **Chip**: Apple M1/M2/M3/M4 (ARM64)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Internet**: Required for video download and API calls

---

## 🎬 Usage Example

1. Open **http://localhost:5000**
2. Paste a video URL (YouTube, etc.)
3. Click "پردازش ویدیو" (Process Video)
4. Wait for 5-stage processing:
   - 📥 Downloading video
   - 🎤 Transcribing audio (Whisper)
   - 🌐 Translating to Persian (Gemini)
   - 📝 Generating subtitles
   - 🎬 Burning subtitles into video
5. Download your video with Persian subtitles!

---

## 💰 Cost Information

Using Gemini API (your setup):
- **Transcription**: FREE (local Whisper)
- **Translation**: ~$0.01 per 10-minute video
- **Total**: ~$0.01 per video

Compare to Google Cloud: ~$0.26 per video (96% savings!)

---

## 🔄 Updating

To update the project:

```bash
# Pull latest changes
git pull origin main

# Reinstall packages
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart services
./start.sh
```

---

## 🛑 Stopping Services

```bash
# If using start.sh (background mode)
pkill -f "celery worker"
pkill -f "python app.py"
brew services stop redis

# Or use:
./stop.sh  # If stop script exists
```

---

## ✅ Installation Checklist

After running `install_mac_arm.sh`:

- [ ] Homebrew installed
- [ ] Python 3.11 installed
- [ ] FFmpeg installed
- [ ] Redis installed and running
- [ ] Virtual environment created
- [ ] All Python packages installed
- [ ] `.env` file configured with API key
- [ ] Test script passes
- [ ] Services start without errors
- [ ] Browser opens http://localhost:5000

---

## 🎉 You're Ready!

Your Mac ARM is now set up with the fastest, most efficient Video Translator configuration. Enjoy! 🚀
