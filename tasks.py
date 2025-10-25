import os
import shutil
import json
from datetime import datetime, timedelta
from celery import Celery
from config import Config
from video_processor_gemini import GeminiVideoProcessor
import redis
import multiprocessing

# Force spawn method for multiprocessing (Mac compatibility for PyTorch/Whisper)
multiprocessing.set_start_method('spawn', force=True)

# Initialize Celery
celery = Celery('tasks')
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND
celery.conf.task_serializer = 'json'
celery.conf.result_serializer = 'json'
celery.conf.accept_content = ['json']
celery.conf.timezone = 'UTC'
celery.conf.enable_utc = True

# Initialize Redis for persistent task status storage
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Task status storage (in production, use Redis or database)
# Keeping this for backward compatibility but will use Redis primarily
task_status_storage = {}

# Track Celery task IDs for cancellation
celery_task_ids = {}


def update_task_status(task_id: str, status: str, message: str, progress: int = 0, **kwargs):
    """Update task status in storage - now persisted in Redis"""
    current_time = datetime.utcnow()
    
    status_data = {
        'status': status,
        'message': message,
        'progress': progress,
        'updated_at': current_time.isoformat()
    }
    
    # Track timing for each stage
    timing_key = f'task_timing:{task_id}'
    
    # Get existing timing data
    existing_timing = redis_client.get(timing_key)
    if existing_timing:
        timing_data = json.loads(existing_timing)
    else:
        timing_data = {'start_time': current_time.isoformat(), 'stages': {}}
    
    # List of stages in order
    stage_order = ['downloading', 'transcribing', 'translating', 'generating_subtitles', 'burning_subtitles']
    
    # Update stage timing
    if status in stage_order:
        # Complete previous stage if it exists and doesn't have duration
        current_index = stage_order.index(status)
        if current_index > 0:
            prev_stage = stage_order[current_index - 1]
            if prev_stage in timing_data['stages'] and 'duration' not in timing_data['stages'][prev_stage]:
                stage_start = datetime.fromisoformat(timing_data['stages'][prev_stage]['start'])
                duration = (current_time - stage_start).total_seconds()
                timing_data['stages'][prev_stage]['duration'] = duration
        
        # Start current stage if not already started
        if status not in timing_data['stages']:
            timing_data['stages'][status] = {'start': current_time.isoformat()}
    
    # If completed, calculate total time and complete last stage
    if status == 'completed':
        # Complete the last stage (burning_subtitles)
        if 'burning_subtitles' in timing_data['stages'] and 'duration' not in timing_data['stages']['burning_subtitles']:
            stage_start = datetime.fromisoformat(timing_data['stages']['burning_subtitles']['start'])
            duration = (current_time - stage_start).total_seconds()
            timing_data['stages']['burning_subtitles']['duration'] = duration
        
        # Calculate total duration
        start_time = datetime.fromisoformat(timing_data['start_time'])
        total_duration = (current_time - start_time).total_seconds()
        timing_data['total_duration'] = total_duration
    
    # Store timing data
    redis_client.setex(timing_key, 86400, json.dumps(timing_data))
    
    # Always include timing data in status (not just on completion)
    status_data['timing'] = timing_data
    
    # Add any additional fields (like output_file, detected_language, etc.)
    status_data.update(kwargs)
    
    # Store in Redis with 24-hour expiration
    try:
        redis_client.setex(
            f'task_status:{task_id}',
            86400,  # 24 hours in seconds
            json.dumps(status_data)
        )
    except Exception as e:
        print(f"Redis error, falling back to memory: {e}")
        # Fallback to memory storage
        task_status_storage[task_id] = status_data


@celery.task(bind=True)
def process_video_task(self, url: str, task_id: str):
    """Background task for video processing"""
    try:
        # Store Celery task ID for potential cancellation
        celery_task_ids[task_id] = self.request.id
        
        # Create temporary directory for this task
        temp_dir = os.path.join(Config.UPLOAD_FOLDER, task_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Initialize Gemini processor (load_whisper=False to avoid fork issues)
        # Whisper will be loaded lazily when needed in transcribe_audio()
        processor = GeminiVideoProcessor(gemini_api_key=os.getenv('GEMINI_API_KEY'), load_whisper=False)
        
        # Status callback
        def status_callback(status: str, message: str):
            progress_map = {
                'downloading': 20,
                'transcribing': 40,
                'translating': 60,
                'generating_subtitles': 80,
                'burning_subtitles': 90
            }
            update_task_status(task_id, status, message, progress_map.get(status, 0))
        
        # Initial status
        update_task_status(task_id, 'started', 'آماده دریافت درخواست', 0)
        
        # Process video
        result = processor.process_video(
            url=url,
            temp_dir=temp_dir,
            output_dir=Config.OUTPUT_FOLDER,
            status_callback=status_callback
        )
        
        if result['success']:
            update_task_status(
                task_id, 
                'completed', 
                'پردازش با موفقیت انجام شد', 
                100,
                output_file=os.path.basename(result['output_file']),
                detected_language=result.get('detected_language'),
                segments_count=result.get('segments_count')
            )
            
            # Clean up temporary files
            cleanup_temp_files(temp_dir)
            
            return {
                'status': 'completed',
                'output_file': os.path.basename(result['output_file']),
                'detected_language': result.get('detected_language'),
                'segments_count': result.get('segments_count')
            }
        else:
            update_task_status(task_id, 'failed', f'خطا در پردازش: {result["error"]}', 0)
            cleanup_temp_files(temp_dir)
            
            return {
                'status': 'failed',
                'error': result['error']
            }
    
    except Exception as e:
        update_task_status(task_id, 'failed', f'خطای سیستمی: {str(e)}', 0)
        
        # Clean up on error
        if 'temp_dir' in locals():
            cleanup_temp_files(temp_dir)
        
        return {
            'status': 'failed',
            'error': str(e)
        }


def cleanup_temp_files(temp_dir: str):
    """Remove temporary files"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temporary files: {e}")


@celery.task
def cleanup_old_files():
    """Periodic task to delete old output files"""
    try:
        retention_hours = Config.FILE_RETENTION_HOURS
        cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
        
        # Clean output folder
        for filename in os.listdir(Config.OUTPUT_FOLDER):
            file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
            
            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_modified < cutoff_time:
                    os.remove(file_path)
                    print(f"Deleted old file: {filename}")
        
        # Clean temp folder
        for task_dir in os.listdir(Config.UPLOAD_FOLDER):
            task_path = os.path.join(Config.UPLOAD_FOLDER, task_dir)
            
            if os.path.isdir(task_path):
                dir_modified = datetime.fromtimestamp(os.path.getmtime(task_path))
                
                if dir_modified < cutoff_time:
                    shutil.rmtree(task_path)
                    print(f"Deleted old task directory: {task_dir}")
    
    except Exception as e:
        print(f"Error in cleanup task: {e}")


# Configure periodic cleanup (every hour)
celery.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'tasks.cleanup_old_files',
        'schedule': 3600.0,  # Every hour
    },
}


def get_task_status(task_id: str) -> dict:
    """Retrieve task status from storage - now from Redis"""
    try:
        # Try to get from Redis first
        status_json = redis_client.get(f'task_status:{task_id}')
        if status_json:
            return json.loads(status_json)
    except Exception as e:
        print(f"Redis error, falling back to memory: {e}")
    
    # Fallback to memory storage
    return task_status_storage.get(task_id, {
        'status': 'not_found',
        'message': 'Task not found',
        'progress': 0
    })


def cancel_task(task_id: str) -> bool:
    """Cancel a running task"""
    try:
        # Get the Celery task ID
        celery_task_id = celery_task_ids.get(task_id)
        
        if celery_task_id:
            # Revoke the task
            celery.control.revoke(celery_task_id, terminate=True, signal='SIGKILL')
            
            # Update status
            update_task_status(task_id, 'cancelled', 'Task cancelled by user', 0)
            
            # Clean up temp files
            temp_dir = os.path.join(Config.UPLOAD_FOLDER, task_id)
            cleanup_temp_files(temp_dir)
            
            # Remove from tracking
            celery_task_ids.pop(task_id, None)
            
            return True
        else:
            # Task not found or already completed
            return False
    
    except Exception as e:
        print(f"Error cancelling task {task_id}: {e}")
        return False
