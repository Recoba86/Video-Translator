import os
import shutil
from datetime import datetime, timedelta
from celery import Celery
from config import Config
from video_processor_gemini import GeminiVideoProcessor

# Initialize Celery
celery = Celery('tasks')
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND
celery.conf.task_serializer = 'json'
celery.conf.result_serializer = 'json'
celery.conf.accept_content = ['json']
celery.conf.timezone = 'UTC'
celery.conf.enable_utc = True

# Task status storage (in production, use Redis or database)
task_status_storage = {}


def update_task_status(task_id: str, status: str, message: str, progress: int = 0):
    """Update task status in storage"""
    task_status_storage[task_id] = {
        'status': status,
        'message': message,
        'progress': progress,
        'updated_at': datetime.utcnow().isoformat()
    }


@celery.task(bind=True)
def process_video_task(self, url: str, task_id: str):
    """Background task for video processing using Whisper + Gemini"""
    try:
        # Create temporary directory for this task
        temp_dir = os.path.join(Config.UPLOAD_FOLDER, task_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Initialize Gemini processor
        processor = GeminiVideoProcessor(gemini_api_key=os.getenv('GEMINI_API_KEY'))
        
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
            update_task_status(task_id, 'completed', 'پردازش با موفقیت انجام شد', 100)
            
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
        'task': 'tasks_gemini.cleanup_old_files',
        'schedule': 3600.0,  # Every hour
    },
}


def get_task_status(task_id: str) -> dict:
    """Retrieve task status from storage"""
    return task_status_storage.get(task_id, {
        'status': 'not_found',
        'message': 'Task not found',
        'progress': 0
    })
