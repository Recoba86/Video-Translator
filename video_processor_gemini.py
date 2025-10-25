import os
import subprocess
import tempfile
from typing import Dict, List, Tuple
import google.generativeai as genai
# import whisper  # REMOVED - will import only when needed to avoid PyTorch issues
import yt_dlp
from bidi_fixer import fix_srt_file, fix_bidi_text


class GeminiVideoProcessor:
    """Handles video download, transcription (Whisper), translation (Gemini), and subtitle burn-in"""
    
    def __init__(self, gemini_api_key: str = None, load_whisper: bool = True):
        """Initialize with Gemini API key"""
        # Configure Gemini
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Whisper model - only load if requested (for multiprocessing safety)
        self.whisper_model = None
        if load_whisper:
            self._load_whisper()
    
    def _load_whisper(self):
        """Load Whisper model (separated for lazy loading in forked processes)"""
        if self.whisper_model is None:
            print("Loading Whisper model...")
            import whisper  # Import only when needed
            self.whisper_model = whisper.load_model("base")
            print("Whisper model loaded!")
    
    def download_video(self, url: str, output_path: str) -> str:
        """Download video using yt-dlp"""
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_path
    
    def extract_audio(self, video_path: str, audio_path: str) -> str:
        """Extract audio from video using FFmpeg"""
        print("="*80)
        print("EXTRACT_AUDIO CALLED")
        print(f"Video path: {video_path}")
        print(f"Audio path: {audio_path}")
        print(f"Video exists: {os.path.exists(video_path)}")
        print("="*80)
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM format
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            audio_path
        ]
        
        print("About to run FFmpeg subprocess...")
        # Don't capture output - let it go to stdout/stderr, and use DEVNULL for stdin
        result = subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg completed!")
        return audio_path
    
    def transcribe_audio(self, audio_path: str) -> Tuple[List[Dict], str]:
        """Transcribe audio using Whisper (local, FREE!) - runs in subprocess to avoid fork issues"""
        print("="*80)
        print("TRANSCRIBE_AUDIO CALLED")
        print("="*80)
        print("Transcribing audio with Whisper (subprocess mode)...")
        print(f"Audio file: {audio_path}")
        print(f"File exists: {os.path.exists(audio_path)}")
        print(f"File size: {os.path.getsize(audio_path) if os.path.exists(audio_path) else 'N/A'} bytes")
        
        try:
            # Run Whisper in a subprocess to avoid PyTorch/fork issues
            import subprocess
            import json
            import sys
            
            print("About to get Python executable...")
            # Use current Python executable
            python_exe = sys.executable
            print(f"Python exe: {python_exe}")
            
            # Run whisper_subprocess.py
            script_path = os.path.join(os.path.dirname(__file__), 'whisper_subprocess.py')
            print(f"Script path: {script_path}")
            print(f"Script exists: {os.path.exists(script_path)}")
            
            print(f"About to run: {python_exe} {script_path} {audio_path} base")
            print("Starting subprocess.run()...")
            
            result = subprocess.run(
                [python_exe, script_path, audio_path, 'base'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # Ignore Whisper's progress bars
                text=True,
                timeout=300  # 5 minutes max
            )
            
            print("Subprocess.run() completed!")
            print(f"Subprocess return code: {result.returncode}")
            print(f"Subprocess stdout length: {len(result.stdout) if result.stdout else 0} chars")
            print(f"Subprocess stdout preview: {result.stdout[:200] if result.stdout else 'Empty'}")
            
            if result.returncode != 0:
                raise Exception(f"Whisper subprocess failed: {result.stderr}")
            
            # Parse JSON output
            output_data = json.loads(result.stdout)
            
            if not output_data.get('success'):
                raise Exception(f"Whisper error: {output_data.get('error')}")
            
            transcription_segments = output_data['segments']
            detected_language = output_data['detected_language']
            
            print(f"Transcription complete! Detected language: {detected_language}")
            print(f"Segments: {len(transcription_segments)}")
            
            return transcription_segments, detected_language
            
        except subprocess.TimeoutExpired:
            print("ERROR: Whisper transcription timed out after 5 minutes")
            raise Exception("Transcription timed out")
        except Exception as e:
            print(f"ERROR in transcribe_audio: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def translate_text(self, text: str, target_language: str = 'Persian') -> str:
        """Translate text using Gemini"""
        prompt = f"""You are a professional Persian translator for video subtitles. Translate the following English text to natural, conversational Persian (Farsi).

CRITICAL TRANSLATION RULES:
1. Use INFORMAL, CONVERSATIONAL Persian - like how people actually speak
2. Use common daily phrases, not formal/literary language
3. For greetings and common phrases, use the most natural equivalent:
   - "How about..." → "چطوره..." or "چه میگی به..."
   - "at two" → "ساعت دو" (NOT "در دو")
   - "What do you think?" → "نظرت چیه؟"
   - "Let's go" → "بریم"
   - "I don't know" → "نمیدونم"
4. Use short, natural sentences that match spoken Persian
5. Avoid overly literal translations
6. Keep numbers in Persian-Arabic numerals (۱۲۳) 
7. Maintain the casual/formal tone of the original

IMPORTANT - HANDLING ENGLISH WORDS:
8. For English acronyms, names, or technical terms that must stay in English:
   - Separate them with spaces: "من T-Y-O-L و P-SOL هستم"
   - NOT joined: "من T-Y-O-Lو P-SOLهستم"
   - Add ‏ (RLM - Right-to-Left Mark) before/after English text if needed
9. If translation includes English words, structure it clearly:
   - Example: "من یک معلم TESOL هستم" (with proper spacing)
   
10. NO explanations or notes - ONLY return the Persian translation

Original text:
"{text}"

Natural Persian translation:"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            translation = response.text.strip()
            
            # Clean up any markdown formatting
            translation = translation.replace('**', '').replace('*', '')
            
            return translation
        except Exception as e:
            print(f"Translation error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return text  # Fallback to original text
    
    def translate_segments(self, segments: List[Dict], target_language: str = 'Persian') -> List[Dict]:
        """Translate all transcription segments using Gemini"""
        translated_segments = []
        
        total_segments = len(segments)
        print(f"Translating {total_segments} segments to {target_language}...")
        
        # Batch segments for more efficient translation
        batch_size = 20
        total_batches = (total_segments + batch_size - 1) // batch_size
        
        for batch_num, i in enumerate(range(0, len(segments), batch_size), 1):
            batch = segments[i:i+batch_size]
            
            print(f"Processing batch {batch_num}/{total_batches} (segments {i+1}-{min(i+batch_size, total_segments)})...")
            
            # Combine batch for context-aware translation
            batch_text = "\n---\n".join([seg['text'] for seg in batch])
            
            # Translate the batch
            print(f"Sending batch {batch_num} to Gemini API...")
            translated_batch = self.translate_text(batch_text, target_language)
            print(f"Batch {batch_num} translation received!")
            
            # Split back into segments
            translated_texts = translated_batch.split("\n---\n")
            
            # Ensure we have the right number of translations
            if len(translated_texts) != len(batch):
                # Fallback: translate individually
                translated_texts = [self.translate_text(seg['text'], target_language) for seg in batch]
            
            # Add to results
            for seg, trans_text in zip(batch, translated_texts):
                translated_segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': trans_text.strip()
                })
        
        print("Translation complete!")
        return translated_segments
    
    def format_timestamp_srt(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def format_timestamp_ass(self, seconds: float) -> str:
        """Format seconds to ASS timestamp format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def generate_srt(self, segments: List[Dict], output_path: str) -> str:
        """Generate SRT subtitle file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{self.format_timestamp_srt(segment['start'])} --> {self.format_timestamp_srt(segment['end'])}\n")
                # Apply bidi fix to text before writing
                fixed_text = fix_bidi_text(segment['text'])
                f.write(f"{fixed_text}\n\n")
        
        return output_path
    
    def generate_ass(self, segments: List[Dict], output_path: str) -> str:
        """Generate ASS subtitle file with Persian-friendly styling"""
        # ASS header with Persian font settings
        # BackColour: &H66000000 = 40% transparent black background (66 hex = 102 decimal)
        # BorderStyle=4 for background box (valid values: 1, 3, 4)
        # Outline=4 for thicker outline
        # Using Vazirmatn font for better Persian text rendering
        # Font size: 70 (35% increase from 52)
        ass_header = """[Script Info]
Title: Auto-generated Persian Subtitles (Gemini AI)
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Vazirmatn,70,&H00FFFFFF,&H000088EF,&H00000000,&H66000000,-1,0,0,0,100,100,0,0,4,4,0,2,10,10,10,178

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            
            for segment in segments:
                start = self.format_timestamp_ass(segment['start'])
                end = self.format_timestamp_ass(segment['end'])
                # Apply bidi fix before replacing newlines
                fixed_text = fix_bidi_text(segment['text'])
                text = fixed_text.replace('\n', '\\N')
                
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
        
        return output_path
    
    def burn_subtitles(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        """Burn subtitles into video using FFmpeg"""
        # Determine subtitle format
        subtitle_ext = os.path.splitext(subtitle_path)[1].lower()
        
        if subtitle_ext == '.ass':
            # For ASS subtitles
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"ass={subtitle_path}",
                '-c:a', 'copy',
                '-y',
                output_path
            ]
        else:
            # For SRT subtitles
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles={subtitle_path}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'",
                '-c:a', 'copy',
                '-y',
                output_path
            ]
        
        subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    
    def process_video(self, url: str, temp_dir: str, output_dir: str, 
                     status_callback=None) -> Dict:
        """Complete video processing pipeline using Whisper + Gemini"""
        try:
            video_id = os.path.basename(temp_dir)
            
            # Paths
            video_path = os.path.join(temp_dir, f"{video_id}.mp4")
            audio_path = os.path.join(temp_dir, f"{video_id}.wav")
            subtitle_path = os.path.join(temp_dir, f"{video_id}.ass")
            output_path = os.path.join(output_dir, f"{video_id}_subtitled.mp4")
            
            # Step 1: Download video
            if status_callback:
                status_callback('downloading', 'مرحله ۱/۵: در حال دانلود ویدئو...')
            self.download_video(url, video_path)
            
            # Step 2: Extract audio and transcribe (Whisper)
            if status_callback:
                status_callback('transcribing', 'مرحله ۲/۵: در حال رونویسی صوتی...')
            self.extract_audio(video_path, audio_path)
            segments, detected_language = self.transcribe_audio(audio_path)
            
            # Step 3: Translate to Persian (Gemini)
            if status_callback:
                status_callback('translating', 'مرحله ۳/۵: در حال ترجمه به فارسی...')
            translated_segments = self.translate_segments(segments, 'Persian')
            
            # Step 4: Generate subtitle file
            if status_callback:
                status_callback('generating_subtitles', 'مرحله ۴/۵: در حال ساخت فایل زیرنویس...')
            self.generate_ass(translated_segments, subtitle_path)
            
            # Step 5: Burn subtitles
            if status_callback:
                status_callback('burning_subtitles', 'مرحله ۵/۵: در حال چسباندن زیرنویس...')
            self.burn_subtitles(video_path, subtitle_path, output_path)
            
            return {
                'success': True,
                'output_file': output_path,
                'detected_language': detected_language,
                'segments_count': len(segments)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
