import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class"""
    # Debug mode
    DEBUG = False

    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-to-change')

    # File upload settings
    ALLOWED_EXTENSIONS = {'json'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size

    # Saved projects settings
    PROJECT_FILES_DIR = os.path.join(BASE_DIR, '../projects')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    PROJECT_FILES_DIR = os.path.join(BASE_DIR, '../test_projects')

class ProductionConfig(Config):
    """Production configuration"""
    # This would be expanded with production-specific settings
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in environment

# Determine which config to use based on environment variable
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Use this as the actual imported configuration
# Usually this would be selected based on an environment variable
config = config_map.get(os.environ.get('FLASK_ENV', 'default'))
