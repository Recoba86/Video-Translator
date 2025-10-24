import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from config import Config
from tasks import process_video_task, get_task_status, task_status_storage

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')


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
        status = get_task_status(task_id)
        return jsonify(status)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطا در دریافت وضعیت: {str(e)}'
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
