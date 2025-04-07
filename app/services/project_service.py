import os
import json
import re
import jsonschema
from flask import current_app
from app.models.schemas import PROJECT_JSON_SCHEMA

class ProjectService:
    @staticmethod
    def normalize_filename(filename):
        """Normalize a filename by replacing spaces and invalid characters."""
        filename = filename.replace(' ', '_')
        return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "_", filename)

    @staticmethod
    def get_project_path(filename):
        """Get the full path for a project file."""
        clean_filename = ProjectService.normalize_filename(filename)
        return os.path.join(current_app.config['PROJECT_FILES_DIR'], clean_filename)

    @staticmethod
    def get_all_projects():
        """Get a list of all project filenames."""
        project_dir = current_app.config['PROJECT_FILES_DIR']
        return [f for f in os.listdir(project_dir) if f.endswith('.json')]

    @staticmethod
    def create_project(project_name, project_comment=""):
        """Create a new project file."""
        if not project_name:
            raise ValueError("Project name is required.")

        project_data = {
            "project_name": project_name,
            "project_comment": project_comment,
            "c_file_path": "main.c"
        }

        # Create filename from project name
        clean_filename = ProjectService.normalize_filename(project_name) + ".json"
        project_path = ProjectService.get_project_path(clean_filename)

        # Check if project already exists
        if os.path.exists(project_path):
            raise FileExistsError(f"The project '{clean_filename}' already exists.")

        # Write the project file
        with open(project_path, 'wt', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

        return clean_filename

    @staticmethod
    def load_project(filename):
        """Load a project from file and validate its schema."""
        project_path = ProjectService.get_project_path(filename)

        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project '{filename}' not found.")

        with open(project_path, 'rt', encoding='utf-8') as file:
            try:
                project_data = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON file.")

        # Validate schema
        try:
            jsonschema.validate(instance=project_data, schema=PROJECT_JSON_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"JSON schema validation failed: {e.message}")

        return project_data

    @staticmethod
    def delete_project(filename):
        """Delete a project file."""
        project_path = ProjectService.get_project_path(filename)

        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project '{filename}' not found.")

        os.remove(project_path)
        return True

    @staticmethod
    def save_project_file(file):
        """Save an uploaded project file."""
        if not file or file.filename == '':
            raise ValueError("No file selected.")

        if not file.filename.endswith('.json'):
            raise ValueError("Only JSON files are allowed.")

        try:
            project_data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file.")

        try:
            jsonschema.validate(instance=project_data, schema=PROJECT_JSON_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"JSON schema validation failed: {e.message}")

        # Save the file
        project_path = ProjectService.get_project_path(file.filename)

        # Check if file already exists
        if os.path.exists(project_path):
            raise FileExistsError(f"The project '{file.filename}' already exists.")

        with open(project_path, 'wt', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

        return file.filename
