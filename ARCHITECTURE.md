# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                              │
│                    (HTML/CSS/JavaScript)                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTP/AJAX
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Web Server                             │
│                         (app.py)                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                            │  │
│  │  • POST /api/process      - Start processing              │  │
│  │  • GET  /api/status/:id   - Check status                  │  │
│  │  • GET  /api/download/:f  - Download file                 │  │
│  │  • GET  /api/preview/:f   - Preview video                 │  │
│  │  • DELETE /api/delete/:f  - Delete file                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬───────────────────────────────────────────┬────────┘
             │                                           │
             │ Task Queue                                │ File System
             ▼                                           ▼
┌──────────────────────────┐                 ┌─────────────────────┐
│      Redis Server        │                 │   File Storage      │
│   (Message Broker)       │                 │  • temp_files/      │
│                          │                 │  • output_files/    │
└──────────┬───────────────┘                 └─────────────────────┘
           │
           │ Task Distribution
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Celery Worker (tasks.py)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Background Task: process_video_task()                    │  │
│  │  • Receives video URL                                     │  │
│  │  • Updates status in real-time                            │  │
│  │  • Calls VideoProcessor methods                           │  │
│  │  • Handles cleanup on completion/error                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              VideoProcessor (video_processor.py)                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Processing Pipeline:                                     │  │
│  │  1. download_video()        - yt-dlp                      │  │
│  │  2. extract_audio()         - FFmpeg                      │  │
│  │  3. transcribe_audio()      - Google Speech-to-Text       │  │
│  │  4. translate_segments()    - Google Translation          │  │
│  │  5. generate_ass()          - Create subtitle file        │  │
│  │  6. burn_subtitles()        - FFmpeg                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬─────────────────────┬──────────────────────────────┘
             │                     │
             │                     │
             ▼                     ▼
┌──────────────────────┐  ┌────────────────────────────────────┐
│   Google Cloud API   │  │    System Commands                  │
│  • Speech-to-Text    │  │    • FFmpeg (video/audio)          │
│  • Translation       │  │    • yt-dlp (download)             │
└──────────────────────┘  └────────────────────────────────────┘
```

## Component Interaction Flow

```
User Action: Submit Video URL
    ↓
Flask receives POST /api/process
    ↓
Generate unique task_id
    ↓
Queue Celery task with (url, task_id)
    ↓
Return task_id to user immediately
    ↓
[Frontend starts polling /api/status/:task_id]
    ↓
Celery Worker picks up task
    ↓
┌─────────────────────────────────────────────┐
│ Processing Pipeline (with status updates)   │
├─────────────────────────────────────────────┤
│ Stage 1: Download Video                     │
│   - yt-dlp downloads to temp_files/         │
│   - Update: "مرحله ۱/۵: در حال دانلود"     │
├─────────────────────────────────────────────┤
│ Stage 2: Extract & Transcribe Audio         │
│   - FFmpeg extracts audio to .wav           │
│   - Google API transcribes with timestamps  │
│   - Auto-detect source language             │
│   - Update: "مرحله ۲/۵: در حال رونویسی"    │
├─────────────────────────────────────────────┤
│ Stage 3: Translate to Persian               │
│   - Google API translates each segment      │
│   - Preserve timestamps                     │
│   - Update: "مرحله ۳/۵: در حال ترجمه"      │
├─────────────────────────────────────────────┤
│ Stage 4: Generate Subtitle File             │
│   - Create ASS file with Persian styling    │
│   - Include all timed segments              │
│   - Update: "مرحله ۴/۵: در حال ساخت زیرنویس"│
├─────────────────────────────────────────────┤
│ Stage 5: Burn Subtitles                     │
│   - FFmpeg merges video + subtitles         │
│   - Output to output_files/                 │
│   - Update: "مرحله ۵/۵: در حال چسباندن"    │
└─────────────────────────────────────────────┘
    ↓
Clean up temp files
    ↓
Update status: "completed"
    ↓
Frontend receives completion status
    ↓
Display video player with preview
    ↓
User can Download or Delete
```

## Data Flow Diagram

```
┌──────────────┐
│  Video URL   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Raw Video   │  (temp_files/task_id/video.mp4)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Audio File  │  (temp_files/task_id/audio.wav)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  Transcription + Timestamps  │  (In-memory JSON)
│  [                            │
│    {start: 0.0, end: 2.5,    │
│     text: "Hello world"},    │
│    {...}                      │
│  ]                            │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Translated + Timestamps     │  (In-memory JSON)
│  [                            │
│    {start: 0.0, end: 2.5,    │
│     text: "سلام دنیا"},       │
│    {...}                      │
│  ]                            │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────┐
│ Subtitle File│  (temp_files/task_id/video.ass)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Final Video  │  (output_files/task_id_subtitled.mp4)
│ with Persian │
│  Subtitles   │
└──────────────┘
```

## State Management

```
Task Status States:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  not_found ──► started ──► downloading ──► transcribing │
│                                                         │
│       ┌──────────────────────────────┐                 │
│       ▼                              ▼                 │
│  translating ──► generating_subtitles ──► burning_     │
│                                           subtitles    │
│       │                                      │         │
│       │              ┌───────────────────────┘         │
│       ▼              ▼                                 │
│   completed      failed                                │
│                                                         │
└─────────────────────────────────────────────────────────┘

Progress Percentages:
- started:               0%
- downloading:          20%
- transcribing:         40%
- translating:          60%
- generating_subtitles: 80%
- burning_subtitles:    90%
- completed:           100%
```

## Cleanup System

```
┌─────────────────────────────────────────────────────────────┐
│              Celery Beat (Scheduler)                         │
│                                                              │
│  Every 1 hour:                                               │
│    └─► cleanup_old_files()                                  │
│          │                                                   │
│          ├─► Check output_files/ for files > 24h old        │
│          │     └─► Delete old videos                        │
│          │                                                   │
│          └─► Check temp_files/ for directories > 24h old    │
│                └─► Delete old temp directories              │
└─────────────────────────────────────────────────────────────┘

User-Triggered Cleanup:
┌─────────────────────────────────────────────────────────────┐
│  User clicks "Delete" button                                 │
│    ↓                                                         │
│  DELETE /api/delete/:filename                                │
│    ↓                                                         │
│  Immediately remove file from output_files/                  │
│    ↓                                                         │
│  Return success/error to user                                │
└─────────────────────────────────────────────────────────────┘

Post-Processing Cleanup:
┌─────────────────────────────────────────────────────────────┐
│  Task completes (success or failure)                         │
│    ↓                                                         │
│  cleanup_temp_files(temp_dir)                                │
│    ↓                                                         │
│  Remove all files in temp_files/task_id/                     │
│    └─► video.mp4                                            │
│    └─► audio.wav                                            │
│    └─► video.ass                                            │
│    └─► (entire directory)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Security Layers

```
┌──────────────────────────────────────────────────────────┐
│  Layer 1: Input Validation                                │
│  • URL format check                                       │
│  • File size limits (500MB)                               │
│  • Rate limiting (configurable)                           │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 2: Environment Security                            │
│  • Credentials in .env (not in code)                      │
│  • .gitignore for sensitive files                         │
│  • Secret key for Flask sessions                          │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 3: File System Security                            │
│  • Temporary file isolation                               │
│  • Automatic cleanup                                      │
│  • Path validation                                        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  Layer 4: API Security                                    │
│  • CORS configuration                                     │
│  • Error handling without detail leaking                  │
│  • Health check endpoint                                  │
└──────────────────────────────────────────────────────────┘
```

## Scaling Architecture

```
                    Load Balancer
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    Flask App 1    Flask App 2    Flask App 3
         │               │               │
         └───────────────┼───────────────┘
                         │
                    Redis Cluster
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   Celery Worker 1  Celery Worker 2  Celery Worker 3
         │               │               │
         └───────────────┼───────────────┘
                         │
              Shared Storage (NFS/S3)
```

---

This architecture ensures:
- ✅ Separation of concerns
- ✅ Scalability
- ✅ Fault tolerance
- ✅ Easy maintenance
- ✅ Real-time status updates
- ✅ Automatic cleanup
