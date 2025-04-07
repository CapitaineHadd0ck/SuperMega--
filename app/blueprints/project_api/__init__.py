from flask import Blueprint

project_api = Blueprint('project_api', __name__, url_prefix='/api/projects')

from app.blueprints.project_api import routes
