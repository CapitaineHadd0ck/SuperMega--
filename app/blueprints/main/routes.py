import os
from flask import render_template, redirect, url_for, flash, session, current_app, jsonify
from app.blueprints.main import main
from app.services.project_service import ProjectService

# Route for the projects listing page
@main.route('/')
def home():
    projects_list = ProjectService.get_all_projects()
    return render_template('home.html',
                           projects=projects_list,
                           message=session.pop('message', None),
                           message_type=session.pop('message_type', None))

# Route for the project details page
@main.route('/project')
def project_details():
    # Check if project data exists in session
    if 'project_data' not in session:
        flash("No project loaded. Please select a project first.", "warning")
        return redirect(url_for('main.home'))  # Redirect to home page

    project_data = session['project_data']
    project_name = session.get('current_project')

    # Get the project directory path
    project_dir = ProjectService.get_project_dir(project_name)

    # Get all files in the project directory and their contents
    project_files = []
    file_contents = {}

    if os.path.exists(project_dir):
        for file in os.listdir(project_dir):
            file_path = os.path.join(project_dir, file)
            if os.path.isfile(file_path):
                project_files.append(file)
                try:
                    with open(file_path, 'rt', encoding='utf-8') as f:
                        file_contents[file] = f.read()
                except Exception as e:
                    file_contents[file] = f"Error reading file: {str(e)}"

    # Set default file to the main C file
    default_file = project_data.get('c_file_path', '')
    if default_file not in file_contents and project_files:
        default_file = project_files[0]

    return render_template('project_details.html',
                           data=project_data,
                           project_files=project_files,
                           file_contents=file_contents,
                           default_file=default_file)
