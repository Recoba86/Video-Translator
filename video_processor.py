import os
import subprocess
import tempfile
from typing import Dict, List, Tuple
from google.cloud import speech_v1
from google.cloud import translate_v2 as translate
import yt_dlp


class VideoProcessor:
    """Handles video download, transcription, translation, and subtitle burn-in"""
    
    def __init__(self, google_credentials_path: str = None):
        """Initialize with Google Cloud credentials"""
        if google_credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path
        
        self.speech_client = speech_v1.SpeechClient()
        self.translate_client = translate.Client()
    
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
            '-acodec', 'pcm_s16le',  # PCM format for Google Speech API
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            audio_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path
    
    def transcribe_audio(self, audio_path: str) -> Tuple[List[Dict], str]:
        """Transcribe audio using Google Cloud Speech-to-Text with word-level timestamps"""
        with open(audio_path, 'rb') as audio_file:
            content = audio_file.read()
        
        audio = speech_v1.RecognitionAudio(content=content)
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='auto',  # Auto-detect language
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
            model='latest_long',
        )
        
        # For long audio files, use long_running_recognize
        operation = self.speech_client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=600)
        
        # Extract transcription with timestamps
        transcription_segments = []
        detected_language = None
        
        for result in response.results:
            alternative = result.alternatives[0]
            
            if not detected_language and result.language_code:
                detected_language = result.language_code
            
            if alternative.words:
                segment_start = alternative.words[0].start_time.total_seconds()
                segment_end = alternative.words[-1].end_time.total_seconds()
                
                transcription_segments.append({
                    'start': segment_start,
                    'end': segment_end,
                    'text': alternative.transcript.strip()
                })
        
        return transcription_segments, detected_language or 'en-US'
    
    def translate_text(self, text: str, target_language: str = 'fa') -> str:
        """Translate text to Persian using Google Cloud Translation API"""
        result = self.translate_client.translate(
            text,
            target_language=target_language
        )
        
        return result['translatedText']
    
    def translate_segments(self, segments: List[Dict], target_language: str = 'fa') -> List[Dict]:
        """Translate all transcription segments"""
        translated_segments = []
        
        for segment in segments:
            translated_text = self.translate_text(segment['text'], target_language)
            translated_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': translated_text
            })
        
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
Title: Auto-generated Persian Subtitles
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
        """Complete video processing pipeline"""
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
            
            # Step 2: Extract audio and transcribe
            if status_callback:
                status_callback('transcribing', 'مرحله ۲/۵: در حال رونویسی صوتی...')
            self.extract_audio(video_path, audio_path)
            segments, detected_language = self.transcribe_audio(audio_path)
            
            # Step 3: Translate to Persian
            if status_callback:
                status_callback('translating', 'مرحله ۳/۵: در حال ترجمه به فارسی...')
            translated_segments = self.translate_segments(segments, 'fa')
            
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
