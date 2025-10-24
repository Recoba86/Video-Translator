import os
import subprocess
import tempfile
from typing import Dict, List, Tuple
import google.generativeai as genai
import whisper
import yt_dlp


class GeminiVideoProcessor:
    """Handles video download, transcription (Whisper), translation (Gemini), and subtitle burn-in"""
    
    def __init__(self, gemini_api_key: str = None):
        """Initialize with Gemini API key"""
        # Configure Gemini
        api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load Whisper model (base model - good balance of speed and accuracy)
        print("Loading Whisper model...")
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
        
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path
    
    def transcribe_audio(self, audio_path: str) -> Tuple[List[Dict], str]:
        """Transcribe audio using Whisper (local, FREE!)"""
        print("Transcribing audio with Whisper...")
        
        # Transcribe with Whisper
        result = self.whisper_model.transcribe(
            audio_path,
            language=None,  # Auto-detect language
            task='transcribe',
            verbose=False
        )
        
        # Extract segments with timestamps
        transcription_segments = []
        for segment in result.get('segments', []):
            transcription_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        detected_language = result.get('language', 'unknown')
        
        print(f"Transcription complete! Detected language: {detected_language}")
        return transcription_segments, detected_language
    
    def translate_text(self, text: str, target_language: str = 'Persian') -> str:
        """Translate text using Gemini"""
        prompt = f"""Translate the following text to {target_language} (Farsi).

IMPORTANT RULES:
- Provide ONLY the translation, no explanations or additional text
- Maintain the original meaning and tone
- Use natural {target_language} language
- Keep proper nouns in their original form
- Preserve punctuation and formatting

Text to translate:
{text}

{target_language} translation:"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            translation = response.text.strip()
            
            # Clean up any markdown formatting
            translation = translation.replace('**', '').replace('*', '')
            
            return translation
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Fallback to original text
    
    def translate_segments(self, segments: List[Dict], target_language: str = 'Persian') -> List[Dict]:
        """Translate all transcription segments using Gemini"""
        translated_segments = []
        
        print(f"Translating {len(segments)} segments to {target_language}...")
        
        # Batch segments for more efficient translation
        batch_size = 5
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i+batch_size]
            
            # Combine batch for context-aware translation
            batch_text = "\n---\n".join([seg['text'] for seg in batch])
            
            # Translate the batch
            translated_batch = self.translate_text(batch_text, target_language)
            
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
                f.write(f"{segment['text']}\n\n")
        
        return output_path
    
    def generate_ass(self, segments: List[Dict], output_path: str) -> str:
        """Generate ASS subtitle file with Persian-friendly styling"""
        # ASS header with Persian font settings
        ass_header = """[Script Info]
Title: Auto-generated Persian Subtitles (Gemini AI)
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Vazir,52,&H00FFFFFF,&H000088EF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,10,10,40,178

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            
            for segment in segments:
                start = self.format_timestamp_ass(segment['start'])
                end = self.format_timestamp_ass(segment['end'])
                text = segment['text'].replace('\n', '\\N')
                
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
        
        subprocess.run(cmd, check=True, capture_output=True)
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
