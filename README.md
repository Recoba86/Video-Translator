# 🎬 AI Video Subtitler Web Service

An advanced web service that automatically generates Persian/Farsi subtitles for videos using AI. The service downloads videos, transcribes audio, translates to Persian, and burns subtitles directly into the video.

## ✨ Features

- 🎥 **Video Download**: Support for YouTube, Twitter (X), and other platforms via yt-dlp
- 🎤 **Speech-to-Text**: Automatic transcription using Google Cloud Speech-to-Text API
- 🔄 **Translation**: Persian/Farsi translation via Google Cloud Translation API
- 📝 **Subtitle Generation**: Creates timed subtitle files (SRT/ASS format)
- 🎬 **Subtitle Burn-in**: Hardcodes subtitles directly into the video
- 📊 **Real-time Progress**: Live status updates during processing
- 🗑️ **Auto-cleanup**: Automatic file deletion after 24 hours
- 🌐 **Bilingual UI**: Persian interface with English fallbacks

## 🛠️ Tech Stack

- **Backend**: Python + Flask
- **Background Jobs**: Celery + Redis
- **AI Services**: Google Cloud Speech-to-Text & Translation APIs
- **Video Processing**: FFmpeg + yt-dlp
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript

## 📋 Prerequisites

Before installation, ensure you have:

1. **Python 3.8+** installed
2. **FFmpeg** installed ([Download](https://ffmpeg.org/download.html))
3. **Redis Server** installed and running
4. **Google Cloud Account** with APIs enabled (see setup below)

### Installing FFmpeg

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Installing Redis

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**Windows:**
Download from [redis.io](https://redis.io/download) or use WSL.

## 🔑 Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2. Enable Required APIs

Enable these APIs in your project:

- **Cloud Speech-to-Text API**
- **Cloud Translation API**

You can enable them via the console or using gcloud CLI:

```bash
gcloud services enable speech.googleapis.com
gcloud services enable translate.googleapis.com
```

### 3. Create Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name: `video-subtitler` (or any name)
4. Grant these roles:
   - Cloud Speech Client
   - Cloud Translation API User
5. Click **Create Key** → Choose **JSON**
6. Download the JSON key file

### 4. Set Up Billing

⚠️ **Important**: These APIs require billing to be enabled on your Google Cloud project. Both services offer free tier usage:

- **Speech-to-Text**: 60 minutes/month free
- **Translation**: 500,000 characters/month free

Learn more about [pricing](https://cloud.google.com/speech-to-text/pricing) and [free tier](https://cloud.google.com/free).

## 🚀 Installation

### 1. Clone the Repository

```bash
cd /Users/amin/Documents/Witamin-Game/Video-Translator/Video-Translator
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Flask Configuration
SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development

# File Storage
UPLOAD_FOLDER=temp_files
OUTPUT_FOLDER=output_files
MAX_CONTENT_LENGTH=524288000

# Automatic Deletion (in hours)
FILE_RETENTION_HOURS=24

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### 5. Add Google Credentials

Place your downloaded Google Cloud service account JSON file in the project root and name it `google-credentials.json`, or update the path in `.env`.

## 🏃 Running the Application

### Terminal 1: Start Redis (if not running as service)

```bash
redis-server
```

### Terminal 2: Start Celery Worker

```bash
celery -A tasks.celery worker --loglevel=info
```

### Terminal 3: Start Celery Beat (for automatic cleanup)

```bash
celery -A tasks.celery beat --loglevel=info
```

### Terminal 4: Start Flask Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 🎯 Usage

1. **Open Browser**: Navigate to `http://localhost:5000`
2. **Enter Video URL**: Paste a YouTube or Twitter video URL
3. **Start Processing**: Click "شروع پردازش" (Start Processing)
4. **Monitor Progress**: Watch real-time status updates through 5 stages:
   - Stage 1: Downloading video
   - Stage 2: Transcribing audio
   - Stage 3: Translating to Persian
   - Stage 4: Generating subtitle file
   - Stage 5: Burning subtitles into video
5. **Preview & Download**: Once complete, preview the video and download or delete it

## 📁 Project Structure

```
Video-Translator/
├── app.py                 # Flask application & API endpoints
├── tasks.py              # Celery background tasks
├── video_processor.py    # Core video processing logic
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── templates/
│   └── index.html       # Main UI template
├── static/
│   ├── style.css        # UI styles
│   └── script.js        # Frontend JavaScript
├── temp_files/          # Temporary processing files (auto-created)
└── output_files/        # Final output videos (auto-created)
```

## 🔒 Security & Maintenance

### Automatic Cleanup

- Files older than 24 hours are automatically deleted
- Cleanup runs every hour via Celery Beat
- Temporary files are removed after processing

### Manual Cleanup

Users can delete files immediately using the "حذف فایل از سرور" button.

### Privacy

- All processing is done locally on your server
- Files are stored temporarily and auto-deleted
- No data is permanently stored

## 🐛 Troubleshooting

### FFmpeg not found

```bash
# Verify FFmpeg installation
ffmpeg -version
```

If not found, install it (see Prerequisites section).

### Redis connection error

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

Start Redis if not running:
```bash
redis-server
```

### Google API errors

**Authentication error**: Verify your credentials path in `.env`:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="./google-credentials.json"
```

**Quota exceeded**: Check your [Google Cloud quotas](https://console.cloud.google.com/iam-admin/quotas).

**Billing not enabled**: Enable billing in your Google Cloud project.

### Video download fails

- Ensure the URL is valid and publicly accessible
- Some platforms may require authentication or have restrictions
- Check yt-dlp updates: `pip install --upgrade yt-dlp`

### Port already in use

```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

## 🚢 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables

Set `FLASK_ENV=production` in `.env` for production.

### Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Process Management

Use **systemd** or **supervisor** to manage Flask and Celery processes.

## 📊 API Endpoints

### POST /api/process
Start video processing.
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

### GET /api/status/:task_id
Check processing status.

### GET /api/download/:filename
Download processed video.

### GET /api/preview/:filename
Stream video for preview.

### DELETE /api/delete/:filename
Delete video from server.

### GET /api/health
Health check endpoint.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Cloud for AI services
- FFmpeg for video processing
- yt-dlp for video downloading
- Vazir font for Persian text support

## 📞 Support

For issues or questions, please open an issue on the repository.

---

**Made with ❤️ using AI**
