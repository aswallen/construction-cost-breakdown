"""
Configuration file for Construction Cost Breakdown Automation
Customize these settings for your company's needs
"""

import os

# Company branding
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Construction Company')
COMPANY_LOGO_URL = os.getenv('COMPANY_LOGO_URL', '')  # Optional logo URL

# Application settings
APP_TITLE = "Construction Cost Breakdown Automation"
APP_ICON = "🏗️"
MAX_FILE_SIZE_MB = 50  # Maximum file size for uploads
MAX_FILES_PER_BATCH = 10  # Maximum files to process at once

# Template settings
DEFAULT_TEMPLATE_NAME = "_Construction_Breakdown_Template_BLANK.xlsx"
TEMPLATE_DIRECTORY = "templates"

# File storage settings
UPLOAD_DIRECTORY = "uploads"
OUTPUT_DIRECTORY = "outputs"
TEMP_DIRECTORY = "temp"

# AI settings
DEFAULT_AI_MODEL = "gemini-1.5-flash"
AI_TIMEOUT_SECONDS = 120

# Google Gemini API Key Configuration
# Option 1: Set the environment variable GEMINI_API_KEY
# Option 2: Replace "your_api_key_here" with your actual API key below
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA7X-wFf4b1auH7PqC-iTP5OxlebA-pKTw')

# User interface settings
THEME_PRIMARY_COLOR = "#1f77b4"
SHOW_SIDEBAR_BY_DEFAULT = True
LAYOUT_WIDE = True

# Security settings
ALLOWED_FILE_EXTENSIONS = ['pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'bmp', 'tiff']
SANITIZE_FILENAMES = True

# Support contact information
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'aswallen@uwcu.org')

# Feature flags
ENABLE_DEMO_MODE = True
ENABLE_BATCH_PROCESSING = True
ENABLE_ZIP_DOWNLOAD = True
ENABLE_TEMPLATE_UPLOAD = True

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'

# Database settings (for future user management)
DATABASE_URL = os.getenv('DATABASE_URL', '')
ENABLE_USER_TRACKING = False

# Performance settings
CONCURRENT_PROCESSING_LIMIT = 3
CACHE_RESULTS_MINUTES = 60
