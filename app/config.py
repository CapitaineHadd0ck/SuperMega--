import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Debug mode
DEBUG = True

# Secret key for session management
SECRET_KEY = 'dev-to-change'

# File upload settings
ALLOWED_EXTENSIONS = {'json'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size

# Saved projects settings
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
