#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for URL shortener application
"""

import os
import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"logs/url_shortener_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Log file: {log_filename}")
    
    return logger

def validate_files(file_paths):
    """Validate that input files exist and are readable"""
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            print(f"Error: Path is not a file: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Try to read and count non-comment lines
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
                if len(lines) == 0:
                    print(f"Warning: No valid URLs found in {file_path}")
                else:
                    print(f"Found {len(lines)} URLs in {file_path}")
        except Exception as e:
            print(f"Error: Cannot read file {file_path}: {e}")
            return False
    
    return True

def is_valid_url(url):
    """Basic URL validation"""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Basic URL pattern check
    return (url.startswith('http://') or 
            url.startswith('https://') or 
            url.startswith('ftp://')) and len(url) > 10

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores and whitespace
    filename = filename.strip('_ ')
    
    return filename

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def create_directories():
    """Create necessary directories for the application"""
    directories = ['input', 'output', 'logs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create directory {directory}: {e}")

def get_file_size(file_path):
    """Get file size in human readable format"""
    try:
        size = os.path.getsize(file_path)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    
    except Exception:
        return "Unknown"

def count_lines_in_file(file_path):
    """Count number of lines in a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0
