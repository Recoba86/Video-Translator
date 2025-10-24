# 🔄 Alternative: Using Gemini API

If you prefer to use **Google Gemini** instead of the current Speech-to-Text + Translation APIs, here's what you need and how to modify the code.

---

## Why Consider Gemini?

### Pros ✅
- Single API for multiple tasks
- Can handle transcription + translation in one call
- Potentially lower cost for some use cases
- More flexible prompting
- Better context understanding

### Cons ❌
- Less accurate for audio transcription than Speech-to-Text
- No native audio processing (need to transcribe audio first with another tool)
- Might be slower for long videos
- Less reliable timing/timestamps

---

## What You Need for Gemini

### 1. Get Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the API key

### 2. Update `.env`

Add this line:
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Install Gemini SDK

Add to `requirements.txt`:
```txt
google-generativeai==0.3.0
```

Then install:
```bash
pip install google-generativeai
```

---

## Modified Implementation

Here's how to use Gemini for translation (keeping Speech-to-Text for transcription):

### Option A: Gemini for Translation Only (Recommended)

**File: `video_processor_gemini.py`**

```python
import os
import google.generativeai as genai
from video_processor import VideoProcessor

class GeminiVideoProcessor(VideoProcessor):
    """Video processor using Gemini for translation"""
    
    def __init__(self, google_credentials_path: str = None, gemini_api_key: str = None):
        super().__init__(google_credentials_path)
        
        # Configure Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        else:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def translate_text(self, text: str, target_language: str = 'fa') -> str:
        """Translate text using Gemini"""
        
        prompt = f"""Translate the following text to Persian (Farsi).
Rules:
- Provide only the translation, no explanations
- Maintain the original meaning and tone
- Use natural Persian language
- Keep proper nouns as they are

Text to translate:
{text}

Persian translation:"""
        
        response = self.gemini_model.generate_content(prompt)
        return response.text.strip()
    
    def translate_segments(self, segments: list, target_language: str = 'fa') -> list:
        """Translate all segments using Gemini"""
        translated_segments = []
        
        # Batch translate for efficiency
        for segment in segments:
            translated_text = self.translate_text(segment['text'], target_language)
            translated_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': translated_text
            })
        
        return translated_segments
```

**Update `tasks.py`** to use Gemini processor:

```python
from video_processor_gemini import GeminiVideoProcessor

@celery.task(bind=True)
def process_video_task(self, url: str, task_id: str):
    # ... existing code ...
    
    # Use Gemini processor instead
    processor = GeminiVideoProcessor(
        google_credentials_path=Config.GOOGLE_APPLICATION_CREDENTIALS,
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    
    # Rest of the code remains the same
```

### Option B: Full Gemini Implementation (Audio → Text → Translation)

For this, you'd need an intermediate step with Whisper or another audio-to-text tool:

**Install Whisper:**
```bash
pip install openai-whisper
```

**Modified processor:**
```python
import whisper
import google.generativeai as genai

class FullGeminiProcessor:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.whisper_model = whisper.load_model("base")
    
    def transcribe_audio(self, audio_path: str):
        """Transcribe using Whisper (local)"""
        result = self.whisper_model.transcribe(audio_path)
        
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })
        
        return segments, result.get('language', 'unknown')
    
    def translate_with_context(self, segments: list) -> list:
        """Translate with better context using Gemini"""
        
        # Combine all text for context
        full_text = " ".join([s['text'] for s in segments])
        
        prompt = f"""Translate the following text to Persian (Farsi).
Maintain natural flow and context.

Original text:
{full_text}

Provide the Persian translation:"""
        
        response = self.gemini_model.generate_content(prompt)
        persian_text = response.text.strip()
        
        # Split back into segments (simplified approach)
        # In production, use better alignment
        words = persian_text.split()
        words_per_segment = len(words) // len(segments)
        
        translated_segments = []
        for i, segment in enumerate(segments):
            start_idx = i * words_per_segment
            end_idx = start_idx + words_per_segment if i < len(segments) - 1 else len(words)
            segment_text = " ".join(words[start_idx:end_idx])
            
            translated_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment_text
            })
        
        return translated_segments
```

---

## Cost Comparison

### Current Setup (Google Cloud)
- Speech-to-Text: $0.024/minute (60 min free/month)
- Translation: $20/million chars (500k free/month)
- **10-min video**: ~$0.24 + ~$0.02 = **$0.26**

### With Gemini
- Gemini API: $0.00025 per 1000 chars input + $0.0005 per 1000 chars output
- **10-min video** (~3000 words = ~15k chars): ~$0.01
- **Much cheaper!** But need Whisper or another STT

### With Gemini + Whisper (Local)
- Whisper: **FREE** (runs locally)
- Gemini: ~$0.01 per video
- **Total: ~$0.01** but requires more processing power

---

## Recommendation

### Best Setup for You:

**Hybrid Approach (Recommended):**
1. Keep **Google Speech-to-Text** for transcription (most accurate)
2. Use **Gemini** for translation (cheaper, good quality)

**Why?**
- ✅ Best transcription accuracy
- ✅ Lower translation costs
- ✅ Good timing/timestamps
- ✅ Easy to implement

---

## Implementation Steps

### Step 1: Get Gemini API Key
```bash
# Visit: https://aistudio.google.com/app/apikey
# Copy your API key
```

### Step 2: Update Configuration
```bash
# Add to .env
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

### Step 3: Install Gemini SDK
```bash
pip install google-generativeai==0.3.0
```

### Step 4: Create Modified Processor
Save the `GeminiVideoProcessor` code above as `video_processor_gemini.py`

### Step 5: Update Tasks
Modify `tasks.py` to use the new processor

### Step 6: Test
```bash
python test_installation.py
./start.sh
```

---

## Quick Start with Gemini

Want to switch to Gemini quickly? Run this:

```bash
# Install Gemini SDK
pip install google-generativeai

# Add API key to .env
echo "GEMINI_API_KEY=your-key" >> .env

# Create the modified processor (I'll create it for you)
```

Would you like me to create the full Gemini implementation files for you?

---

## Summary: What You Actually Need

### Current Setup (Google Cloud):
1. ✅ Google Cloud Project
2. ✅ Speech-to-Text API enabled
3. ✅ Translation API enabled  
4. ✅ Service Account JSON key
5. ✅ Billing enabled

### Alternative Setup (Gemini):
1. ✅ Gemini API key from https://aistudio.google.com/app/apikey
2. ✅ (Optional) Keep Google Speech-to-Text for transcription
3. ✅ Much simpler setup!

**My Recommendation**: Start with Google Cloud (current setup) since it's already implemented and proven. Later, you can switch translation to Gemini to save costs.

---

Let me know if you want me to:
1. Create the Gemini implementation files
2. Help you get the Google Cloud setup done
3. Both!
