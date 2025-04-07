from flask import render_template, redirect, url_for, flash, session, current_app
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
    return render_template('project_details.html', data=project_data)
