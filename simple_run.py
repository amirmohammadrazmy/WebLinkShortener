#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple runner with Chrome version compatibility fix
Solves the latest Chrome version ChromeDriver mismatch issue
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """Setup Chrome driver with multiple fallback methods"""
    print("🔧 Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # List of stable ChromeDriver versions to try
    stable_versions = [
        "131.0.6778.87",
        "130.0.6723.116", 
        "129.0.6668.89",
        "128.0.6613.137"
    ]
    
    for version in stable_versions:
        try:
            print(f"📥 Trying ChromeDriver version {version}...")
            service = Service(ChromeDriverManager(version=version).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"✅ Success with version {version}")
            return driver
        except Exception as e:
            print(f"❌ Version {version} failed: {str(e)[:100]}")
            continue
    
    # Last resort: try without specifying version (but with timeout)
    try:
        print("🔄 Trying latest version with timeout...")
        import signal
        
        def timeout_handler(signum, frame):
            raise Exception("Timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Latest version worked")
            return driver
        finally:
            signal.alarm(0)
            
    except Exception as e:
        print(f"❌ Latest version failed: {e}")
    
    raise Exception("❌ All ChromeDriver methods failed")

def main():
    """Simple test to verify Chrome setup works"""
    print("🚀 Chrome Compatibility Test")
    print("=" * 40)
    
    try:
        # Test Chrome setup
        driver = setup_chrome_driver()
        
        # Quick test
        print("🌐 Testing website access...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        title = driver.title
        print(f"✅ Website loaded: {title}")
        
        driver.quit()
        print("✅ Chrome setup working perfectly!")
        print("\n💡 Now you can run: python run_local.py")
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n💡 Try running: python fix_chrome_version.py")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to close...")