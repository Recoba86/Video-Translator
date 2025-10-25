"""
Standalone Whisper transcriber that runs in a separate process
This avoids PyTorch/fork issues with Celery
"""
import whisper
import sys
import json
import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore")

def transcribe_file(audio_path, model_name="base"):
    """Transcribe audio file and return JSON result"""
    try:
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirect stdout and stderr to devnull during Whisper operations
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        sys.stderr = devnull
        
        # Load model silently
        model = whisper.load_model(model_name)
        
        # Transcribe with verbose=False to avoid progress bars
        result = model.transcribe(
            audio_path,
            language=None,
            task='transcribe',
            verbose=False,
            fp16=False  # Explicitly disable FP16 to avoid warnings
        )
        
        # Restore stdout
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        devnull.close()
        
        # Extract segments
        segments = []
        for segment in result.get('segments', []):
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        output = {
            'success': True,
            'segments': segments,
            'detected_language': result.get('language', 'unknown')
        }
        
        # Print JSON to stdout
        print(json.dumps(output), flush=True)
        return 0
        
    except Exception as e:
        # Restore stdout if error occurs
        try:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        except:
            pass
            
        error_output = {
            'success': False,
            'error': str(e)
        }
        # Print error JSON to stdout
        print(json.dumps(error_output), flush=True)
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'Usage: python whisper_subprocess.py <audio_file> [model_name]'}))
        sys.exit(1)
    
    audio_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    sys.exit(transcribe_file(audio_path, model_name))
