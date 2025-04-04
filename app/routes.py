import os
import json
import jsonschema
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

# Create a Blueprint named 'main'
main_bp = Blueprint('main', __name__)

# Helper function to set flash messages in session
def set_message(message, category="danger"):
    session['message'] = message
    session['message_type'] = category

# Route for the home page
@main_bp.route('/')
def index():
    projects = [f for f in os.listdir(current_app.config['PROJECTS_DIR']) if f.endswith('.json')]
    return render_template('index.html',
                           projects=projects,
                           message=session.pop('message', None),
                           message_type=session.pop('message_type', None))

# Route for the projects page
@main_bp.route('/project')
def project():
# Check if project data exists in session
    if 'project_data' not in session:
        session['message'] = "No project loaded. Please upload a JSON file."
        session['message_type'] = "warning"
        return redirect(url_for('main.index'))  # Redirect to home page

    project_data = session['project_data']
    return render_template('project.html', data=project_data)
