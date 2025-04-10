import os
from flask import request, redirect, url_for, session, flash, current_app, send_from_directory, jsonify
from app.blueprints.project_api import project_api
from app.services.project_service import ProjectService

# Import a project folder
@project_api.route('/import', methods=['POST'])
def import_project():
    # Handle folder upload
    if 'folder' in request.files:
        folder_name = request.form.get('folder_name', 'project')
        files = request.files.getlist('folder')

        if not files or len(files) == 0:
            flash("No files uploaded.", "danger")
            return redirect(url_for('main.home'))

        try:
            normalized_folder_name = ProjectService.save_project_folder(folder_name, files)
            flash(f"Project '{normalized_folder_name}' uploaded successfully!", "success")
        except (ValueError, FileExistsError) as e:
            flash(str(e), "danger")
    else:
        flash("No folder selected.", "danger")

    return redirect(url_for('main.home'))

# Open a project
@project_api.route('/open/<project_name>')
def open_project(project_name):
    try:
        project_data = ProjectService.load_project(project_name)
        session['project_data'] = project_data
        session['current_project'] = project_name
        return redirect(url_for('main.project_details'))
    except (FileNotFoundError, ValueError) as e:
        flash(str(e), "danger")
        return redirect(url_for('main.home'))

# Delete a project
@project_api.route('/delete/<project_name>')
def delete_project(project_name):
    try:
        ProjectService.delete_project(project_name)

        # If we're deleting the currently open project, clear it from session
        if session.get('current_project') == project_name:
            session.pop('project_data', None)
            session.pop('current_project', None)

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
        normalized_name = ProjectService.create_project(project_name, project_comment)
        flash("Project created successfully!", "success")
    except (ValueError, FileExistsError) as e:
        flash(str(e), "danger")

    return redirect(url_for('main.home'))

# Download project files as a zip archive
@project_api.route('/download/<project_name>', methods=['GET'])
def download_project(project_name):
    """Create a zip archive of the project and send it for download."""
    import zipfile
    import tempfile

    project_dir = ProjectService.get_project_dir(project_name)

    try:
        # Validate that the project exists
        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_path = temp_file.name

        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from the project directory to the zip
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate the relative path to maintain folder structure in zip
                    rel_path = os.path.relpath(file_path, os.path.dirname(project_dir))
                    zipf.write(file_path, rel_path)

        # Send the zip file
        return send_from_directory(
            directory=os.path.dirname(temp_path),
            path=os.path.basename(temp_path),
            as_attachment=True,
            download_name=f"{project_name}.zip"
        )
    except FileNotFoundError as e:
        flash(str(e), "danger")
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f"Error creating zip archive: {str(e)}", "danger")
        return redirect(url_for('main.home'))

# NEW ROUTE: Update project fields
@project_api.route('/update/<project_name>', methods=['POST'])
def update_project_field(project_name):
    """Update a single field in the project data."""
    try:
        # Get the JSON data from the request
        data = request.get_json()

        if not data or 'field' not in data or 'value' not in data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400

        field = data['field']
        value = data['value']

        # Only allow updating specific fields
        if field not in ['project_name', 'project_comment']:
            return jsonify({'success': False, 'message': 'Invalid field name'}), 400

        # Update the project
        updated_data = ProjectService.update_project_field(project_name, field, value)

        # Update the session data
        if 'project_data' in session:
            session['project_data'] = updated_data

        # Set flash message for the next page load
        flash(f"Project {field.replace('_', ' ')} updated successfully.", "success")

        return jsonify({'success': True, 'data': updated_data})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
