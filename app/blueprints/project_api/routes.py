import os
from flask import request, redirect, url_for, session, flash, current_app, send_from_directory, jsonify
from app.blueprints.project_api import project_api
from app.services.project_service import ProjectService

# Import a project file
@project_api.route('/import', methods=['POST'])
def import_project():
    if 'file' not in request.files:
        flash("No file uploaded.", "danger")
        return redirect(url_for('main.home'))

    file = request.files['file']

    try:
        filename = ProjectService.save_project_file(file)
        flash("Project uploaded successfully!", "success")
    except (ValueError, FileExistsError) as e:
        flash(str(e), "danger")

    return redirect(url_for('main.home'))

# Get a project
@project_api.route('/get/<filename>')
def get_project(filename):
    try:
        project_data = ProjectService.load_project(filename)
        session['project_data'] = project_data
        return redirect(url_for('main.project_details'))
    except (FileNotFoundError, ValueError) as e:
        flash(str(e), "danger")
        return redirect(url_for('main.home'))

# Delete a project
@project_api.route('/delete/<filename>')
def delete_project(filename):
    try:
        ProjectService.delete_project(filename)
        flash("Project deleted successfully.", "success")
    except FileNotFoundError as e:
        flash(str(e), "danger")

    return redirect(url_for('main.home'))

# Create a new project
@project_api.route('/create', methods=['POST'])
def create_project():
    project_name = request.form.get("project_name")
    project_comment = request.form.get("project_comment", "")

    try:
        filename = ProjectService.create_project(project_name, project_comment)
        flash("Project created successfully!", "success")
    except (ValueError, FileExistsError) as e:
        flash(str(e), "danger")

    return redirect(url_for('main.home'))

# Download a project
@project_api.route('/download/<filename>', methods=['GET'])
def download_project(filename):
    """Serve the project JSON file for download."""
    projects_dir = current_app.config['PROJECT_FILES_DIR']

    try:
        # Validate that the file exists
        if not os.path.exists(os.path.join(projects_dir, filename)):
            raise FileNotFoundError(f"Project '{filename}' not found.")

        return send_from_directory(directory=projects_dir, path=filename, as_attachment=True)
    except FileNotFoundError as e:
        flash(str(e), "danger")
        return redirect(url_for('main.home'))
