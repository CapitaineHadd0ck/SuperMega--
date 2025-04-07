import os
from flask import Flask

def create_app(config_class='app.config'):
    """
    Application factory function that creates and configures the Flask app

    Args:
        config_class: Path to the config module (default: 'app.config')

    Returns:
        The configured Flask application instance
    """
    # Create the Flask application instance
    app = Flask(__name__)

    # Load configuration from the specified config module
    app.config.from_object(config_class)

    # Set a secret key for session management
    app.secret_key = app.config.get('SECRET_KEY')

    # Create folders if they don't exist
    os.makedirs(app.config['PROJECT_FILES_DIR'], exist_ok=True)

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register blueprints
    from app.blueprints.main import main
    app.register_blueprint(main)

    from app.blueprints.project_api import project_api
    app.register_blueprint(project_api)

    return app
