#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package creator for 2ad.ir URL Shortener
Creates a downloadable package with all necessary files
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_package():
    """Create a complete package for download"""
    
    # Package info
    package_name = f"2ad_url_shortener_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = f"packages/{package_name}"
    
    # Create package directory
    os.makedirs(package_dir, exist_ok=True)
    os.makedirs(f"{package_dir}/input", exist_ok=True)
    os.makedirs(f"{package_dir}/output", exist_ok=True)
    os.makedirs(f"{package_dir}/logs", exist_ok=True)
    
    # Files to include
    files_to_copy = [
        'main.py',
        'url_shortener.py',
        'config.py',
        'utils.py',
        'config.json',
        'run_local.py',
        'README_FARSI.md'
    ]
    
    # Copy main files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
    
    # Copy input files as templates
    if os.path.exists('input/download_links_480p.txt'):
        shutil.copy2('input/download_links_480p.txt', f"{package_dir}/input/")
    if os.path.exists('input/output_links.txt'):
        shutil.copy2('input/output_links.txt', f"{package_dir}/input/")
    
    # Create .gitkeep files
    with open(f"{package_dir}/output/.gitkeep", 'w') as f:
        f.write("# Output files will be saved here\n")
    
    with open(f"{package_dir}/logs/.gitkeep", 'w') as f:
        f.write("# Log files will be saved here\n")
    
    # Create installation script
    install_script = """@echo off
echo Installing 2ad.ir URL Shortener...
echo.
echo Installing Python dependencies...
pip install selenium webdriver-manager
echo.
echo Installation complete!
echo.
echo To run the program:
echo   python run_local.py
echo.
echo OR:
echo   python main.py --username your_email@example.com --password your_password
echo.
pause
"""
    
    with open(f"{package_dir}/install.bat", 'w') as f:
        f.write(install_script)
    
    # Create shell script for Linux/Mac
    shell_script = """#!/bin/bash
echo "Installing 2ad.ir URL Shortener..."
echo
echo "Installing Python dependencies..."
pip install selenium webdriver-manager
echo
echo "Installation complete!"
echo
echo "To run the program:"
echo "  python run_local.py"
echo
echo "OR:"
echo "  python main.py --username your_email@example.com --password your_password"
echo
"""
    
    with open(f"{package_dir}/install.sh", 'w') as f:
        f.write(shell_script)
    
    # Make shell script executable
    os.chmod(f"{package_dir}/install.sh", 0o755)
    
    # Create zip file
    zip_filename = f"{package_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(f"packages/{package_name}")
    
    return zip_filename

if __name__ == "__main__":
    try:
        zip_file = create_package()
        print(f"Package created successfully: {zip_file}")
        print(f"Size: {os.path.getsize(zip_file)} bytes")
    except Exception as e:
        print(f"Error creating package: {e}")