#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Version Fix Script
Automatically fixes ChromeDriver version compatibility issues
Specifically handles latest Chrome versions that don't have matching ChromeDriver yet
"""

import os
import sys
import subprocess
import shutil
import requests
import json
from pathlib import Path

def get_chrome_version():
    """Get installed Chrome version"""
    try:
        # Windows
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        # Linux/Mac
        else:
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split()[-1]
            else:
                result = subprocess.run(['chromium-browser', '--version'], capture_output=True, text=True)
                return result.stdout.split()[-1]
    except:
        return None

def clear_webdriver_cache():
    """Clear webdriver-manager cache"""
    try:
        home = Path.home()
        cache_dirs = [
            home / ".wdm",
            home / "AppData" / "Local" / ".wdm",  # Windows
            home / ".cache" / "selenium"
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                print(f"Clearing cache: {cache_dir}")
                shutil.rmtree(cache_dir, ignore_errors=True)
        
        print("✅ WebDriver cache cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False

def get_compatible_chromedriver_version():
    """Get compatible ChromeDriver version for installed Chrome"""
    try:
        # Get available ChromeDriver versions
        url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        versions = [v['version'] for v in data['versions']]
        
        # Get installed Chrome version
        chrome_version = get_chrome_version()
        if not chrome_version:
            return "131.0.6778.87"  # Fallback stable version
        
        # Find compatible version
        chrome_major = chrome_version.split('.')[0]
        
        # Look for exact match first
        for version in reversed(versions):
            if version.startswith(chrome_major):
                return version
        
        # Fallback to last known stable
        return "131.0.6778.87"
        
    except Exception as e:
        print(f"⚠️ Could not determine compatible version: {e}")
        return "131.0.6778.87"

def install_compatible_chromedriver():
    """Install compatible ChromeDriver"""
    try:
        print("🔄 Installing compatible ChromeDriver...")
        
        # Get compatible version
        compatible_version = get_compatible_chromedriver_version()
        print(f"📋 Using ChromeDriver version: {compatible_version}")
        
        # Force reinstall selenium and webdriver-manager
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'selenium', 'webdriver-manager'], check=True)
        
        # Pre-download the compatible version
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            ChromeDriverManager(version=compatible_version).install()
            print("✅ Compatible ChromeDriver pre-downloaded")
        except:
            print("⚠️ Pre-download failed, will try during runtime")
        
        print("✅ ChromeDriver dependencies updated")
        return True
    except Exception as e:
        print(f"❌ Error installing ChromeDriver: {e}")
        return False

def main():
    print("🔧 Chrome Version Fix Tool")
    print("=" * 40)
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"📋 Chrome version detected: {chrome_version}")
    else:
        print("⚠️ Could not detect Chrome version")
    
    # Clear cache
    clear_webdriver_cache()
    
    # Install compatible driver
    install_compatible_chromedriver()
    
    print("\n✅ Fix completed!")
    print("💡 Now try running your script again:")
    print("   python run_local.py")

if __name__ == "__main__":
    main()