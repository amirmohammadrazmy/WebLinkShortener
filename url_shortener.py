#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL Shortener class for 2ad.ir automation
Handles web automation using Selenium WebDriver
"""

import os
import json
import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class URLShortener:
    """Main class for URL shortening automation on 2ad.ir"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self.wait = None
        self.processed_links = set()
        self.checkpoint_file = os.path.join(config.output_dir, 'checkpoint.json')
        self.results_file = os.path.join(config.output_dir, f'shortened_urls_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        # Selectors for 2ad.ir website (based on user specification)
        self.selectors = {
            'username_field': 'username',
            'password_field': 'password',
            'login_button': 'invisibleCaptchaSignin',
            'new_link_modal': 'modal-open-new-link',
            'url_input': 'url',
            'shorten_button': "//span[text()='کوتاه کن']",
            'result_field': 'link-result-url',
            'dashboard_url': 'https://2ad.ir/member/dashboard'
        }
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            # Add essential Chrome options
            if self.config.headless:
                chrome_options.add_argument('--headless=new')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
            
            # For local Windows environment, don't set binary_location
            # Chrome will be found automatically
            
            # Try different approaches for ChromeDriver
            driver_initialized = False
            
            # Method 1: Use webdriver-manager with auto-detection
            if not driver_initialized:
                try:
                    self.logger.info("Attempting to use webdriver-manager with auto-detection")
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver_initialized = True
                    self.logger.info("WebDriver initialized with auto-detection")
                except Exception as e:
                    self.logger.warning(f"Auto-detection failed: {e}")
            
            # Method 2: Try system ChromeDriver
            if not driver_initialized:
                try:
                    self.logger.info("Attempting to use system ChromeDriver")
                    service = Service()  # Uses system PATH
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver_initialized = True
                    self.logger.info("WebDriver initialized with system ChromeDriver")
                except Exception as e:
                    self.logger.warning(f"System ChromeDriver failed: {e}")
            
            # Method 3: Force latest version download
            if not driver_initialized:
                try:
                    self.logger.info("Forcing latest ChromeDriver download")
                    service = Service(ChromeDriverManager(cache_valid_range=1).install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver_initialized = True
                    self.logger.info("WebDriver initialized with forced download")
                except Exception as e:
                    self.logger.error(f"All ChromeDriver methods failed: {e}")
                    raise
            
            if not driver_initialized:
                raise WebDriverException("Failed to initialize ChromeDriver with any method")
            
            self.driver.set_page_load_timeout(180)  # 3 minutes timeout for page loads
            
            self.wait = WebDriverWait(self.driver, 60)
            
            self.logger.info("WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def login(self):
        """Login to 2ad.ir website"""
        try:
            self.logger.info("Navigating to 2ad.ir signin page")
            
            # Try multiple attempts to load the page
            for attempt in range(3):
                try:
                    self.driver.get("https://2ad.ir/auth/signin")
                    # Wait for page to load
                    time.sleep(5)
                    break
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed to load signin page: {str(e)}")
                    if attempt == 2:
                        raise e
                    time.sleep(10)
            
            # Find and fill username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, self.selectors['username_field']))
            )
            username_field.clear()
            username_field.send_keys(self.config.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, self.selectors['password_field'])
            password_field.clear()
            password_field.send_keys(self.config.password)
            
            # Click login button
            login_button = self.driver.find_element(By.ID, self.selectors['login_button'])
            login_button.click()
            
            # Wait for login to complete and redirect to dashboard
            time.sleep(8)
            
            # Navigate to dashboard
            self.logger.info("Navigating to dashboard")
            for attempt in range(3):
                try:
                    self.driver.get(self.selectors['dashboard_url'])
                    time.sleep(5)
                    break
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed to load dashboard: {str(e)}")
                    if attempt == 2:
                        raise e
                    time.sleep(10)
            
            # Check if we're on dashboard page
            if self.selectors['dashboard_url'] in self.driver.current_url:
                self.logger.info("Login successful - reached dashboard")
                return True
            else:
                self.logger.error("Login failed - not redirected to dashboard")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    def read_links_from_files(self):
        """Read links from input files"""
        all_links = []
        
        for file_path in self.config.input_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Filter out comments and empty lines
                    links = [line.strip() for line in f.readlines() 
                            if line.strip() and not line.strip().startswith('#')]
                    all_links.extend(links)
                    self.logger.info(f"Read {len(links)} links from {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to read file {file_path}: {str(e)}")
                return None
        
        # Remove duplicates while preserving order
        unique_links = []
        seen = set()
        for link in all_links:
            if link not in seen:
                unique_links.append(link)
                seen.add(link)
        
        self.logger.info(f"Total unique links to process: {len(unique_links)}")
        return unique_links[:1000]  # Limit to 1000 links as specified
    
    def load_checkpoint(self):
        """Load checkpoint data if resume is enabled"""
        if not self.config.resume or not os.path.exists(self.checkpoint_file):
            return set()
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                processed = set(data.get('processed_links', []))
                self.logger.info(f"Loaded checkpoint: {len(processed)} processed links")
                return processed
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {str(e)}")
            return set()
    
    def save_checkpoint(self, processed_links):
        """Save checkpoint data"""
        try:
            checkpoint_data = {
                'processed_links': list(processed_links),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def shorten_url(self, url):
        """Shorten a single URL"""
        try:
            # Click on new link modal button
            modal_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, self.selectors['new_link_modal']))
            )
            modal_button.click()
            time.sleep(2)
            
            # Find URL input field and enter URL
            url_input = self.wait.until(
                EC.presence_of_element_located((By.ID, self.selectors['url_input']))
            )
            url_input.clear()
            url_input.send_keys(url)
            
            # Click shorten button using XPath
            shorten_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['shorten_button']))
            )
            shorten_button.click()
            
            # Wait for result
            time.sleep(3)
            
            # Get shortened URL
            result_field = self.wait.until(
                EC.presence_of_element_located((By.ID, self.selectors['result_field']))
            )
            
            shortened_url = result_field.get_attribute('value')
            if not shortened_url:
                shortened_url = result_field.text
            
            if shortened_url and shortened_url != url:
                self.logger.debug(f"Successfully shortened: {url} -> {shortened_url}")
                
                # Open the shortened URL in a new tab to register the link
                self.driver.execute_script(f"window.open('{shortened_url}', '_blank');")
                time.sleep(2)
                
                # Close the new tab and return to main window
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                return shortened_url
            else:
                self.logger.warning(f"Failed to shorten URL: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error shortening URL {url}: {str(e)}")
            return None
    
    def save_result(self, original_url, shortened_url, success=True):
        """Save result to CSV file"""
        try:
            file_exists = os.path.exists(self.results_file)
            
            with open(self.results_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'original_url', 'shortened_url', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'timestamp': datetime.now().isoformat(),
                    'original_url': original_url,
                    'shortened_url': shortened_url or 'FAILED',
                    'status': 'SUCCESS' if success else 'FAILED'
                })
                
        except Exception as e:
            self.logger.error(f"Failed to save result: {str(e)}")
    
    def process_links_in_batches(self, links):
        """Process links in batches"""
        processed_links = self.load_checkpoint()
        remaining_links = [link for link in links if link not in processed_links]
        
        self.logger.info(f"Processing {len(remaining_links)} remaining links")
        
        total_processed = len(processed_links)
        successful = 0
        failed = 0
        
        for i in range(0, len(remaining_links), self.config.batch_size):
            batch = remaining_links[i:i + self.config.batch_size]
            batch_num = (i // self.config.batch_size) + 1
            
            self.logger.info(f"Processing batch {batch_num} ({len(batch)} links)")
            
            for link in batch:
                try:
                    shortened = self.shorten_url(link)
                    
                    if shortened:
                        successful += 1
                        self.save_result(link, shortened, True)
                    else:
                        failed += 1
                        self.save_result(link, None, False)
                    
                    processed_links.add(link)
                    total_processed += 1
                    
                    # Add delay between requests
                    time.sleep(self.config.delay)
                    
                except Exception as e:
                    self.logger.error(f"Error processing link {link}: {str(e)}")
                    failed += 1
                    processed_links.add(link)
                    self.save_result(link, None, False)
            
            # Save checkpoint after each batch
            self.save_checkpoint(processed_links)
            
            progress = (total_processed / len(links)) * 100
            self.logger.info(f"Progress: {total_processed}/{len(links)} ({progress:.1f}%) - Success: {successful}, Failed: {failed}")
        
        return successful, failed
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {str(e)}")
    
    def run(self):
        """Main execution method"""
        try:
            # Setup WebDriver
            if not self.setup_driver():
                return False
            
            # Login to website
            if not self.login():
                return False
            
            # Read links from files
            links = self.read_links_from_files()
            if not links:
                self.logger.error("No links to process")
                return False
            
            # Process links in batches
            successful, failed = self.process_links_in_batches(links)
            
            # Final summary
            total = successful + failed
            self.logger.info(f"Processing completed: {successful} successful, {failed} failed out of {total} total")
            self.logger.info(f"Results saved to: {self.results_file}")
            
            return successful > 0
            
        except Exception as e:
            self.logger.error(f"Unexpected error in main execution: {str(e)}")
            return False
        finally:
            self.cleanup()
