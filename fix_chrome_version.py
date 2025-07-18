#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Version Fix Script
Automatically fixes ChromeDriver version compatibility issues
"""

import os
import sys
import subprocess
import shutil
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

def install_compatible_chromedriver():
    """Install compatible ChromeDriver"""
    try:
        print("🔄 Installing compatible ChromeDriver...")
        
        # Force reinstall selenium and webdriver-manager
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'selenium', 'webdriver-manager'], check=True)
        
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