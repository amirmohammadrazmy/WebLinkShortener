#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management for URL shortener
"""

import json
import os

class Config:
    """Configuration class for URL shortener application"""
    
    def __init__(self, username=None, password=None, input_files=None, 
                 output_dir='output', batch_size=10, delay=2.0, 
                 headless=False, resume=False):
        self.username = username
        self.password = password
        self.input_files = input_files or []
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.delay = delay
        self.headless = headless
        self.resume = resume
        
        # Load configuration from file if exists
        self.load_from_file()
    
    def load_from_file(self, config_file='config.json'):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Update attributes from file, but don't override command line args
                for key, value in config_data.items():
                    if hasattr(self, key) and getattr(self, key) is None:
                        setattr(self, key, value)
                        
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
    
    def save_to_file(self, config_file='config.json'):
        """Save current configuration to JSON file"""
        try:
            config_data = {
                'batch_size': self.batch_size,
                'delay': self.delay,
                'headless': self.headless,
                'output_dir': self.output_dir,
                'input_files': self.input_files
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save config file {config_file}: {e}")
    
    def validate(self):
        """Validate configuration parameters"""
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
        
        if not self.input_files:
            raise ValueError("At least one input file is required")
        
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        if self.delay < 0:
            raise ValueError("Delay cannot be negative")
        
        return True
