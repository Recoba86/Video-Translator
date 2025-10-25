# AI Video Subtitler - Usage Guide

## 🚀 Starting the Services

```bash
./start_services.sh
```

This will start:
- Flask server on http://localhost:8000
- Celery worker for background processing
- Redis (must be running separately)

## 📱 Using the Web Interface

1. **Open your browser**: http://localhost:8000

2. **Paste a YouTube URL** in the input field

3. **Click "شروع پردازش" (Start Processing)**

4. **IMPORTANT: Keep the tab open!** 
   - Don't refresh the page
   - Don't close the tab
   - Don't switch away for long periods

## ⚠️ Important Behavior Changes

### **Automatic Task Cancellation**

The system now automatically cancels tasks in these situations:

1. **Page Refresh**: If you refresh while processing, the task will be cancelled
2. **Tab Close**: If you close the tab, the task will be cancelled
3. **Browser Warning**: You'll see a warning if you try to leave during processing

### **Why This Matters**

- **Saves Server Resources**: No orphaned tasks running in background
- **Prevents Wasted API Calls**: Gemini API calls are expensive
- **Cleaner System**: No zombie processes or temp files

## 📊 Processing Stages

You'll see 5 stages during processing:

1. **⏬ دانلود ویدئو** (Downloading Video) - 20%
2. **🎤 رونویسی صوتی** (Transcribing Audio) - 40%
3. **🌐 ترجمه به فارسی** (Translating to Persian) - 60%
4. **📝 ساخت فایل زیرنویس** (Generating Subtitles) - 80%
5. **🎬 چسباندن زیرنویس** (Burning Subtitles) - 100%

## ⏱️ Expected Processing Times

- **Short videos (< 1 min)**: 30-60 seconds
- **Medium videos (1-3 min)**: 1-3 minutes
- **Long videos (3-10 min)**: 3-10 minutes

Translation time depends on:
- Number of segments detected by Whisper
- Gemini API response time (~1-2 seconds per segment)

## 🛠️ Troubleshooting

### "Task not found" Error

This happens when:
- You refreshed the page during processing
- The server restarted
- Task was cancelled

**Solution**: Click "تلاش مجدد" (Try Again) and start a new process

### Video Processing Stuck

If processing seems stuck:
1. Check the Celery logs: `tail -f logs/celery.log`
2. Check the Flask logs: `tail -f logs/flask.log`
3. Restart services: `./start_services.sh`

### Port Already in Use

If port 8000 is occupied:
```bash
lsof -ti:8000 | xargs kill -9
./start_services.sh
```

## 📝 Monitoring

### Watch Flask Logs
```bash
tail -f logs/flask.log
```

### Watch Celery Logs
```bash
tail -f logs/celery.log
```

### Check Services Status
```bash
ps aux | grep -E "(python app.py|celery.*worker)"
```

## 🛑 Stopping Services

```bash
pkill -f 'python app.py' && pkill -f 'celery.*tasks'
```

Or press `Ctrl+C` if running in foreground.

## 📁 Output Files

Processed videos are saved in:
```
output/[task-id]_subtitled.mp4
```

Files are automatically deleted after 24 hours (configurable in `.env`).

## 🔑 API Endpoints

- `POST /api/process` - Start processing
- `GET /api/status/<task_id>` - Check status
- `POST /api/cancel/<task_id>` - Cancel task (NEW!)
- `GET /api/download/<filename>` - Download video
- `DELETE /api/delete/<filename>` - Delete video
- `GET /api/health` - Health check

## 🌟 Best Practices

1. **Test with short videos first** (< 1 minute)
2. **Keep the browser tab active** during processing
3. **Check logs** if something goes wrong
4. **Don't process multiple videos simultaneously** (uses significant resources)
5. **Clear old output files** regularly to save disk space

## 🆘 Getting Help

If you encounter issues:
1. Check the logs first
2. Restart the services
3. Try with a different video
4. Check your Gemini API key is valid

## 📌 Notes

- **API Key**: Stored in `.env` file
- **Model**: Uses Gemini 2.5 Flash for translation
- **Transcription**: Uses OpenAI Whisper (base model, local)
- **Video Download**: Uses yt-dlp (updated to latest)
