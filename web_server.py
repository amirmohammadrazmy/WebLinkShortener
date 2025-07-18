#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web-based 2ad.ir URL Shortener
Flask web interface for online deployment
"""

import os
import sys
import json
import time
import csv
import logging
from datetime import datetime
from io import StringIO
from flask import Flask, render_template, request, jsonify, send_file
import threading
from queue import Queue
import tempfile

# Import our existing modules
from url_shortener import URLShortener
from config import Config
from utils import setup_logging

app = Flask(__name__)
app.secret_key = 'url_shortener_secret_key_2ad_ir'

# Global variables for processing
processing_queue = Queue()
processing_status = {}
results_storage = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_urls():
    """Upload URLs for processing"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        urls_text = data.get('urls', '')
        batch_size = int(data.get('batch_size', 5))
        delay = float(data.get('delay', 3.0))
        
        if not username or not password:
            return jsonify({'error': 'نام کاربری و رمز عبور الزامی است'}), 400
        
        # Process URLs
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            return jsonify({'error': 'لطفاً حداقل یک URL وارد کنید'}), 400
        
        if len(urls) > 1000:
            return jsonify({'error': 'حداکثر 1000 URL در هر بار پردازش'}), 400
        
        # Create processing job
        job_id = f"job_{int(time.time())}"
        
        # Save URLs to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        for url in urls:
            temp_file.write(url + '\n')
        temp_file.close()
        
        # Create job configuration
        job_config = {
            'job_id': job_id,
            'username': username,
            'password': password,
            'input_file': temp_file.name,
            'batch_size': batch_size,
            'delay': delay,
            'total_urls': len(urls),
            'processed_urls': 0,
            'successful_urls': 0,
            'failed_urls': 0,
            'status': 'queued',
            'created_at': datetime.now().isoformat(),
            'results': []
        }
        
        # Add to queue and status tracking
        processing_queue.put(job_config)
        processing_status[job_id] = job_config
        
        # Start processing if not already running
        if not getattr(app, 'processing_thread_running', False):
            thread = threading.Thread(target=process_urls_worker)
            thread.daemon = True
            thread.start()
            app.processing_thread_running = True
        
        return jsonify({
            'job_id': job_id,
            'message': f'کار با {len(urls)} URL به صف اضافه شد',
            'status': 'queued'
        })
        
    except Exception as e:
        return jsonify({'error': f'خطا در پردازش: {str(e)}'}), 500

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get processing status"""
    if job_id not in processing_status:
        return jsonify({'error': 'کار یافت نشد'}), 404
    
    status = processing_status[job_id].copy()
    
    # Calculate progress
    if status['total_urls'] > 0:
        status['progress'] = (status['processed_urls'] / status['total_urls']) * 100
    else:
        status['progress'] = 0
    
    return jsonify(status)

@app.route('/download/<job_id>')
def download_results(job_id):
    """Download results as CSV"""
    if job_id not in processing_status:
        return jsonify({'error': 'کار یافت نشد'}), 404
    
    job = processing_status[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'کار هنوز تکمیل نشده'}), 400
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Original URL', 'Shortened URL', 'Status', 'Processed Time'])
    
    for result in job['results']:
        writer.writerow([
            result['original_url'],
            result['shortened_url'],
            result['status'],
            result['processed_time']
        ])
    
    # Create temporary file for download
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_file.write(output.getvalue())
    temp_file.close()
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f'shortened_urls_{job_id}.csv',
        mimetype='text/csv'
    )

def process_urls_worker():
    """Background worker to process URLs"""
    while True:
        try:
            # Get job from queue
            job = processing_queue.get(timeout=60)
            
            if job is None:
                break
            
            job_id = job['job_id']
            processing_status[job_id]['status'] = 'processing'
            processing_status[job_id]['started_at'] = datetime.now().isoformat()
            
            # Setup logging for this job
            logger = setup_logging(logging.INFO)
            
            try:
                # Create config
                config = Config(
                    username=job['username'],
                    password=job['password'],
                    input_files=[job['input_file']],
                    output_dir=tempfile.gettempdir(),
                    batch_size=job['batch_size'],
                    delay=job['delay'],
                    headless=True,
                    resume=False
                )
                
                # Initialize URL shortener
                shortener = URLShortener(config, logger)
                
                # Override methods to track progress
                original_shorten_url = shortener.shorten_url
                
                def track_progress_shorten_url(url):
                    result = original_shorten_url(url)
                    
                    # Update progress
                    processing_status[job_id]['processed_urls'] += 1
                    
                    if result:
                        processing_status[job_id]['successful_urls'] += 1
                        status = 'success'
                        shortened_url = result
                    else:
                        processing_status[job_id]['failed_urls'] += 1
                        status = 'failed'
                        shortened_url = 'خطا در کوتاه‌سازی'
                    
                    # Add to results
                    processing_status[job_id]['results'].append({
                        'original_url': url,
                        'shortened_url': shortened_url,
                        'status': status,
                        'processed_time': datetime.now().isoformat()
                    })
                    
                    return result
                
                shortener.shorten_url = track_progress_shorten_url
                
                # Run the shortener
                success = shortener.run()
                
                # Update final status
                if success:
                    processing_status[job_id]['status'] = 'completed'
                else:
                    processing_status[job_id]['status'] = 'failed'
                
            except Exception as e:
                logger.error(f"Processing error for job {job_id}: {str(e)}")
                processing_status[job_id]['status'] = 'failed'
                processing_status[job_id]['error'] = str(e)
            
            finally:
                processing_status[job_id]['completed_at'] = datetime.now().isoformat()
                
                # Clean up temporary file
                if os.path.exists(job['input_file']):
                    os.unlink(job['input_file'])
            
            processing_queue.task_done()
            
        except Exception as e:
            print(f"Worker error: {e}")
            break

if __name__ == '__main__':
    # Create templates directory and template
    os.makedirs('templates', exist_ok=True)
    
    # Create HTML template
    html_template = '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کوتاه‌کننده لینک 2ad.ir</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, button { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; cursor: pointer; }
        button:hover { background: #0056b3; }
        .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .status.queued { background: #fff3cd; border: 1px solid #ffeaa7; }
        .status.processing { background: #d1ecf1; border: 1px solid #bee5eb; }
        .status.completed { background: #d4edda; border: 1px solid #c3e6cb; }
        .status.failed { background: #f8d7da; border: 1px solid #f5c6cb; }
        .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: #007bff; transition: width 0.3s; }
        .results { margin-top: 20px; }
        .results a { display: inline-block; margin-top: 10px; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 کوتاه‌کننده لینک 2ad.ir</h1>
        
        <form id="urlForm">
            <div class="form-group">
                <label>نام کاربری 2ad.ir:</label>
                <input type="text" id="username" required placeholder="your@email.com">
            </div>
            
            <div class="form-group">
                <label>رمز عبور:</label>
                <input type="password" id="password" required>
            </div>
            
            <div class="form-group">
                <label>لینک‌ها (هر کدام در یک خط):</label>
                <textarea id="urls" rows="10" required placeholder="https://example.com/link1&#10;https://example.com/link2"></textarea>
            </div>
            
            <div class="form-group">
                <label>تعداد هر دسته:</label>
                <input type="number" id="batch_size" value="5" min="1" max="20">
            </div>
            
            <div class="form-group">
                <label>تاخیر بین درخواست‌ها (ثانیه):</label>
                <input type="number" step="0.1" id="delay" value="3.0" min="1" max="10">
            </div>
            
            <button type="submit">شروع پردازش</button>
        </form>
        
        <div id="status" class="status" style="display: none;"></div>
    </div>

    <script>
        let currentJobId = null;
        let statusInterval = null;

        document.getElementById('urlForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                urls: document.getElementById('urls').value,
                batch_size: document.getElementById('batch_size').value,
                delay: document.getElementById('delay').value
            };
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    currentJobId = result.job_id;
                    document.getElementById('status').style.display = 'block';
                    startStatusCheck();
                } else {
                    alert('خطا: ' + result.error);
                }
            } catch (error) {
                alert('خطا در ارسال: ' + error.message);
            }
        });

        function startStatusCheck() {
            if (statusInterval) clearInterval(statusInterval);
            
            statusInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/status/${currentJobId}`);
                    const status = await response.json();
                    
                    updateStatus(status);
                    
                    if (status.status === 'completed' || status.status === 'failed') {
                        clearInterval(statusInterval);
                    }
                } catch (error) {
                    console.error('Error checking status:', error);
                }
            }, 2000);
        }

        function updateStatus(status) {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status ${status.status}`;
            
            let html = `<h3>وضعیت: ${getStatusText(status.status)}</h3>`;
            
            if (status.progress !== undefined) {
                html += `
                    <div class="progress">
                        <div class="progress-bar" style="width: ${status.progress}%"></div>
                    </div>
                    <p>پیشرفت: ${Math.round(status.progress)}% (${status.processed_urls}/${status.total_urls})</p>
                `;
            }
            
            if (status.status === 'completed') {
                html += `
                    <div class="results">
                        <p>✅ موفق: ${status.successful_urls}</p>
                        <p>❌ ناموفق: ${status.failed_urls}</p>
                        <a href="/download/${currentJobId}">📥 دانلود نتایج CSV</a>
                    </div>
                `;
            }
            
            if (status.error) {
                html += `<p style="color: red;">خطا: ${status.error}</p>`;
            }
            
            statusDiv.innerHTML = html;
        }

        function getStatusText(status) {
            const statusTexts = {
                'queued': 'در صف انتظار',
                'processing': 'در حال پردازش',
                'completed': 'تکمیل شده',
                'failed': 'ناموفق'
            };
            return statusTexts[status] || status;
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Start the web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)