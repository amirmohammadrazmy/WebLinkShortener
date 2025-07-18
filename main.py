#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2ad.ir URL Shortener Automation Script
Main entry point for the application
"""

import argparse
import os
import sys
import logging
from datetime import datetime
from url_shortener import URLShortener
from config import Config
from utils import setup_logging, validate_files

def main():
    """Main function to run the URL shortener automation"""
    parser = argparse.ArgumentParser(description='2ad.ir URL Shortener Automation')
    parser.add_argument('--username', required=True, help='Username for 2ad.ir')
    parser.add_argument('--password', required=True, help='Password for 2ad.ir')
    parser.add_argument('--file1', default='input/download_links_480p.txt', help='First links file (download_links_480p)')
    parser.add_argument('--file2', default='input/output_links.txt', help='Second links file (output_links)')
    parser.add_argument('--output-dir', default='output', help='Output directory for results')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("Starting 2ad.ir URL Shortener Automation")
    logger.info(f"Processing files: {args.file1}, {args.file2}")
    
    try:
        # Validate input files
        if not validate_files([args.file1, args.file2]):
            logger.error("Input file validation failed")
            return 1
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize configuration
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
        
        # Initialize and run URL shortener
        shortener = URLShortener(config, logger)
        success = shortener.run()
        
        if success:
            logger.info("URL shortening completed successfully")
            return 0
        else:
            logger.error("URL shortening failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
