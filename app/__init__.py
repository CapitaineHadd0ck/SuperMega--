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

    # Create folders if don't exist
    os.makedirs(app.config['PROJECTS_DIR'], exist_ok=True)

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    from app.api_project import api_bp
    app.register_blueprint(api_bp)

    return app
