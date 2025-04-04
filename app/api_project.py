import os
import json
import jsonschema
from flask import Blueprint, send_from_directory, request, redirect, url_for, session, flash, current_app
from .schemas import PROJECT_JSON_SCHEMA  # Import schema from a separate file
from jsonschema import ValidationError, FormatChecker
import re

api_bp = Blueprint('api', __name__, url_prefix='/api/project')

# Format checker for JSON schema validation
format_checker = FormatChecker()

@format_checker.checks("relative-path")
def is_relative_path(path):
    """Check if a path is relative."""
    return not os.path.isabs(path)  # Returns True if relative

def sanitize(dirty):
    dirty = dirty.replace(' ', '_')
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "_", dirty)

def sanitize_and_add_project_dir(dirty):
    clean = sanitize(dirty)
    return os.path.join(current_app.config['PROJECTS_DIR'], clean)

# Upload JSON Project File
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file uploaded.", "danger")
        return redirect(url_for('main.index'))

    file = request.files['file']
    if file and file.filename == '':
        flash("No file selected.", "danger")
        return redirect(url_for('main.index'))

    if not file.filename.endswith('.json'):
        flash("Only valid JSON files are allowed.", "danger")
        return redirect(url_for('main.index'))

    try:
        project_data = json.load(file)
    except json.JSONDecodeError:
        flash("Invalid JSON file.", "danger")
        return redirect(url_for('main.index'))

    try:
        jsonschema.validate(instance=project_data, schema=PROJECT_JSON_SCHEMA)
    except jsonschema.ValidationError:
        flash("JSON schema validation failed.", "danger")
        return redirect(url_for('main.index'))

    # sanitize filename
    project_path = sanitize_and_add_project_dir(file.filename)

    # check if filename already exists
    if os.path.exists(project_path):
        flash(f"The project \"{file.filename}\" already exists.", "danger")
        return redirect(url_for('main.index'))

    with open(project_path, 'wt', encoding='utf-8') as f:
        json.dump(project_data, f)

    flash("Project uploaded successfully!", "success")

    return redirect(url_for('main.index'))

# Load an existing project
@api_bp.route('/load/<filename>')
def load_project(filename):
    project_path = os.path.join(current_app.config['PROJECTS_DIR'], filename)

    if not os.path.exists(project_path):
        flash("Project not found.", "danger")
        return redirect(url_for('main.index'))

    with open(project_path, 'rt', encoding='utf-8') as file:

        if not file.name.endswith('.json'):
            flash("Only valid JSON files are allowed.", "danger")
            return redirect(url_for('main.index'))


        try:
            project_data = json.load(file)
        except json.JSONDecodeError:
            flash("Invalid JSON file.", "danger")
            return redirect(url_for('main.index'))

    try:
        jsonschema.validate(instance=project_data, schema=PROJECT_JSON_SCHEMA)
    except jsonschema.ValidationError:
        flash("JSON schema validation failed.", "danger")
        return redirect(url_for('main.index'))

    session['project_data'] = project_data
    # flash("Project loaded successfully!", "success")

    return redirect(url_for('main.project'))

# Delete a project
@api_bp.route('/delete/<filename>')
def delete_project(filename):
    project_path = os.path.join(current_app.config['PROJECTS_DIR'], filename)

    if os.path.exists(project_path):
        os.remove(project_path)
        flash("Project deleted successfully.", "success")
    else:
        flash("Project not found.", "danger")

    return redirect(url_for('main.index'))

# Create a new project
@api_bp.route('/create', methods=['POST'])
def create_project():
    project_name = request.form.get("project_name")
    project_comment = request.form.get("project_comment", "")

    if not project_name:
        flash("Project name is required.", "danger")
        return redirect(url_for('main.index'))

    project_data = {
        "project_name": project_name,
        "project_comment": project_comment,
        "c_file_path": "main.c"
    }

    # sanitize filename
    clean_filename = sanitize(project_name) + ".json"
    project_path = os.path.join(current_app.config['PROJECTS_DIR'], clean_filename)

    if os.path.exists(project_path):
        flash(f"The project \"{clean_filename}\" already exists.", "danger")
        return redirect(url_for('main.index'))

    with open(project_path, 'wt', encoding='utf-8') as f:
        json.dump(project_data, f)

    flash("Project created successfully!", "success")
    return redirect(url_for('main.index'))


@api_bp.route('/download/<filename>', methods=['GET'])
def download_project(filename):
    """Serve the project JSON file for download."""
    projects_dir = current_app.config['PROJECTS_DIR']
    file_path = os.path.join(projects_dir, filename)

    if os.path.exists(file_path):
        return send_from_directory(directory=projects_dir, path=filename, as_attachment=True)
    else:
        return "File not found", 404
