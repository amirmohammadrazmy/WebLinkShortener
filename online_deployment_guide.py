#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Online Deployment Guide for 2ad.ir URL Shortener
Alternative cloud platforms that work with Iranian websites
"""

import json

def create_deployment_configs():
    """Create deployment configurations for different platforms"""
    
    # 1. Railway.app deployment
    railway_config = {
        "name": "Railway Deployment",
        "description": "Railway.app with Iranian-friendly IPs",
        "files": {
            "Procfile": "web: python web_server.py",
            "requirements.txt": """
selenium==4.34.2
webdriver-manager==4.0.2
flask==3.0.0
requests==2.32.4
""",
            "railway.json": {
                "build": {
                    "builder": "nixpacks"
                },
                "deploy": {
                    "startCommand": "python web_server.py"
                }
            }
        },
        "environment_vars": [
            "PORT=5000",
            "CHROME_BIN=/usr/bin/google-chrome-stable",
            "CHROMEDRIVER_PATH=/usr/bin/chromedriver"
        ]
    }
    
    # 2. Heroku deployment
    heroku_config = {
        "name": "Heroku Deployment", 
        "description": "Heroku with buildpacks for Chrome",
        "files": {
            "Procfile": "web: python web_server.py",
            "requirements.txt": """
selenium==4.34.2
webdriver-manager==4.0.2
flask==3.0.0
gunicorn==21.2.0
""",
            "runtime.txt": "python-3.11.6"
        },
        "buildpacks": [
            "https://github.com/heroku/heroku-buildpack-google-chrome",
            "https://github.com/heroku/heroku-buildpack-chromedriver",
            "heroku/python"
        ]
    }
    
    # 3. Render.com deployment
    render_config = {
        "name": "Render.com Deployment",
        "description": "Render.com with Chrome support",
        "files": {
            "render.yaml": {
                "services": [{
                    "type": "web",
                    "name": "url-shortener",
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python web_server.py",
                    "envVars": [{
                        "key": "PYTHON_VERSION",
                        "value": "3.11.6"
                    }]
                }]
            }
        }
    }
    
    # 4. DigitalOcean App Platform
    digitalocean_config = {
        "name": "DigitalOcean App Platform",
        "description": "DigitalOcean with custom Docker",
        "files": {
            "Dockerfile": """
FROM python:3.11-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \\
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/\$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \\
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "web_server.py"]
""",
            ".do/app.yaml": {
                "name": "url-shortener",
                "services": [{
                    "name": "web",
                    "source_dir": "/",
                    "github": {
                        "repo": "your-username/url-shortener",
                        "branch": "main"
                    },
                    "run_command": "python web_server.py"
                }]
            }
        }
    }
    
    return {
        "railway": railway_config,
        "heroku": heroku_config, 
        "render": render_config,
        "digitalocean": digitalocean_config
    }

def print_deployment_guide():
    """Print deployment guide"""
    configs = create_deployment_configs()
    
    print("🌐 Online Deployment Options for 2ad.ir URL Shortener")
    print("=" * 60)
    
    print("\n🚀 Recommended Platforms:")
    print("1. Railway.app - Fast, easy setup")
    print("2. Render.com - Free tier available") 
    print("3. DigitalOcean - Reliable, good IP ranges")
    print("4. Heroku - Popular, many resources")
    
    print("\n📋 Required Files for All Platforms:")
    print("- web_server.py (Flask web interface)")
    print("- requirements.txt (Python dependencies)")
    print("- Deployment config file")
    
    print("\n💡 Steps:")
    print("1. Create web_server.py")
    print("2. Upload to GitHub repository")
    print("3. Connect to chosen platform")
    print("4. Deploy and test")
    
    print("\n🔧 All platforms will have:")
    print("- Automated Chrome/ChromeDriver setup")
    print("- Web interface for bulk URL processing")
    print("- Better IP compatibility with Iranian sites")

if __name__ == "__main__":
    print_deployment_guide()