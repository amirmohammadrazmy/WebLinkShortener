#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local version of 2ad.ir URL Shortener for better performance with Iranian IP
Fixed ChromeDriver version compatibility
"""

import argparse
import os
import sys
import logging
import subprocess
from datetime import datetime
from url_shortener import URLShortener
from config import Config
from utils import setup_logging, validate_files

def check_chrome_compatibility():
    """Check and fix Chrome/ChromeDriver compatibility"""
    try:
        print("🔍 Checking Chrome compatibility...")
        
        # Try to import selenium
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test basic driver setup
        print("✅ Selenium imported successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Chrome compatibility issue detected: {e}")
        print("🔧 Running automatic fix...")
        
        try:
            # Run fix script
            subprocess.run([sys.executable, 'fix_chrome_version.py'], check=True)
            return True
        except:
            print("❌ Auto-fix failed. Please run: python fix_chrome_version.py")
            return False

def main():
    """Main function optimized for local execution"""
    print("🚀 2ad.ir URL Shortener - Enhanced Local Version")
    print("=" * 55)
    
    # Check Chrome compatibility first
    if not check_chrome_compatibility():
        print("\n❌ Chrome compatibility check failed")
        print("💡 Please run: python fix_chrome_version.py")
        return 1
    
    # Get credentials from user
    username = input("نام کاربری 2ad.ir: ")
    password = input("رمز عبور: ")
    
    # Configure parser with local-optimized defaults
    parser = argparse.ArgumentParser(description='2ad.ir URL Shortener - Local Version')
    parser.add_argument('--username', default=username, help='Username for 2ad.ir')
    parser.add_argument('--password', default=password, help='Password for 2ad.ir')
    parser.add_argument('--file1', default='input/download_links_480p.txt', help='First links file')
    parser.add_argument('--file2', default='input/output_links.txt', help='Second links file')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--batch-size', type=int, default=5, help='Batch size (recommended: 5)')
    parser.add_argument('--delay', type=float, default=3.0, help='Delay between requests (recommended: 3.0)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    print(f"📂 پردازش فایل‌ها: {args.file1}, {args.file2}")
    print(f"⚙️ تنظیمات: batch_size={args.batch_size}, delay={args.delay}s")
    
    try:
        # Validate files
        if not validate_files([args.file1, args.file2]):
            print("❌ خطا در اعتبارسنجی فایل‌ها")
            return 1
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize config
        config = Config(
            username=args.username,
            password=args.password,
            input_files=[args.file1, args.file2],
            output_dir=args.output_dir,
            batch_size=args.batch_size,
            delay=args.delay,
            headless=args.headless,
            resume=args.resume
        )
        
        print("🔄 در حال راه‌اندازی WebDriver...")
        
        # Run URL shortener
        shortener = URLShortener(config, logger)
        success = shortener.run()
        
        if success:
            print("✅ پردازش با موفقیت تکمیل شد!")
            print(f"📊 نتایج در فایل: {shortener.results_file}")
            return 0
        else:
            print("❌ پردازش ناموفق بود")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ پردازش توسط کاربر متوقف شد")
        return 130
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())