import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template, redirect
from flask_cors import CORS
from config import Config
from tasks import process_video_task, get_task_status, task_status_storage, cancel_task
from celery.result import AsyncResult

app = Flask(__name__)
app.config.from_object(Config)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching
CORS(app)

# Track active connections for each task
active_connections = {}


# Add no-cache headers to all responses
@app.after_request
def add_no_cache_headers(response):
    """Add headers to prevent caching"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')


@app.route('/simple')
@app.route('/simple/process', methods=['GET', 'POST'])
def simple_interface():
    """Simple HTML-only interface with auto-refresh"""
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        
        if not video_url:
            return render_template('simple.html', 
                                 status='failed', 
                                 message='لطفاً آدرس ویدئو را وارد کنید')
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start processing
        process_video_task.delay(video_url, task_id)
        
        # Redirect to status page
        return redirect(f'/simple/status/{task_id}')
    
    return render_template('simple.html')


@app.route('/simple/status/<task_id>')
def simple_status(task_id):
    """Show status with auto-refresh"""
    status = get_task_status(task_id)
    
    return render_template('simple.html',
                         task_id=task_id,
                         status=status.get('status'),
                         message=status.get('message'),
                         progress=status.get('progress', 0),
                         output_file=status.get('output_file'))


@app.route('/api/process', methods=['POST'])
def process_video():
    """Start video processing"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'لطفاً آدرس ویدئو را وارد کنید (Please provide a video URL)'
            }), 400
        
        # Validate URL (basic check)
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'آدرس ویدئو نامعتبر است (Invalid video URL)'
            }), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Start background task
        process_video_task.delay(url, task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'پردازش شروع شد (Processing started)'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطای سیستمی: {str(e)}'
        }), 500


@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    """Check processing status"""
    try:
        # Track that this connection is still alive
        active_connections[task_id] = True
        
        status = get_task_status(task_id)
        return jsonify(status)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطا در دریافت وضعیت: {str(e)}'
        }), 500


@app.route('/api/cancel/<task_id>', methods=['POST'])
def cancel_video_task(task_id):
    """Cancel a running task"""
    try:
        # Mark connection as inactive
        active_connections.pop(task_id, None)
        
        # Cancel the task
        result = cancel_task(task_id)
        
        return jsonify({
            'success': True,
            'message': 'Task cancelled successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در لغو تسک: {str(e)}'
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download processed video"""
    try:
        file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'فایل یافت نشد (File not found)'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در دانلود فایل: {str(e)}'
        }), 500


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """Stream video for preview"""
    try:
        file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'فایل یافت نشد (File not found)'
            }), 404
        
        return send_file(
            file_path,
            mimetype='video/mp4'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در نمایش فایل: {str(e)}'
        }), 500


@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete processed video from server"""
    try:
        file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'فایل یافت نشد (File not found)'
            }), 404
        
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': 'فایل با موفقیت حذف شد (File deleted successfully)'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در حذف فایل: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Video Subtitler'
    })


if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=(Config.FLASK_ENV == 'development')
    )
