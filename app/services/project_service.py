import os
import json
import re
import shutil
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
    def get_projects_base_dir():
        """Get the projects base directory."""
        return current_app.config['PROJECTS_BASE_DIR']

    @staticmethod
    def get_project_dir(project_name):
        """Get the full path for a project directory."""
        normalized_name = ProjectService.normalize_filename(project_name)
        return os.path.join(ProjectService.get_projects_base_dir(), normalized_name)

    @staticmethod
    def get_project_json_path(project_dir):
        """Get the path to the project.json file within a project directory."""
        return os.path.join(project_dir, "project.json")

    @staticmethod
    def get_all_projects():
        """Get a list of all project directories."""
        projects_base_dir = ProjectService.get_projects_base_dir()
        projects = []

        # Only include directories that contain a project.json file
        for item in os.listdir(projects_base_dir):
            full_path = os.path.join(projects_base_dir, item)
            if os.path.isdir(full_path):
                project_json_path = os.path.join(full_path, "project.json")
                if os.path.isfile(project_json_path):
                    projects.append(item)

        return projects

    @staticmethod
    def create_project(project_name, project_comment=""):
        """Create a new project folder with project.json file."""
        if not project_name:
            raise ValueError("Project name is required.")

        # Create a normalized project folder name
        normalized_name = ProjectService.normalize_filename(project_name)
        project_dir = ProjectService.get_project_dir(normalized_name)

        # Check if project already exists
        if os.path.exists(project_dir):
            raise FileExistsError(f"Project '{normalized_name}' already exists.")

        # Create project directory
        os.makedirs(project_dir, exist_ok=True)

        # Create project data
        project_data = {
            "project_name": project_name,
            "project_comment": project_comment,
            "c_file_path": "main.c"
        }

        # Write project.json file
        project_json_path = ProjectService.get_project_json_path(project_dir)
        with open(project_json_path, 'wt', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

        # Create empty main.c file
        main_c_path = os.path.join(project_dir, "main.c")
        with open(main_c_path, 'wt', encoding='utf-8') as f:
            f.write("// Main C file for project\n")

        return normalized_name

    @staticmethod
    def load_project(project_name):
        """Load a project from its project.json file."""
        project_dir = ProjectService.get_project_dir(project_name)

        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        project_json_path = ProjectService.get_project_json_path(project_dir)

        if not os.path.exists(project_json_path):
            raise FileNotFoundError(f"Project file 'project.json' not found in project '{project_name}'.")

        with open(project_json_path, 'rt', encoding='utf-8') as file:
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
    def delete_project(project_name):
        """Delete a project directory and all its contents."""
        project_dir = ProjectService.get_project_dir(project_name)

        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project '{project_name}' not found.")

        shutil.rmtree(project_dir)
        return True

    @staticmethod
    def is_file_acceptable(filename):
        """Check if a file should be accepted based on its extension."""
        return filename.endswith('.c') or filename.lower() == 'project.json'

    @staticmethod
    def save_project_folder(folder_name, files):
        """Save an uploaded project folder with its contents.

        Args:
            folder_name: Name of the project folder
            files: List of file objects from the upload

        Returns:
            The normalized folder name
        """
        if not folder_name or not files:
            raise ValueError("No folder or files selected.")

        # Normalize the folder name
        normalized_folder_name = ProjectService.normalize_filename(folder_name)

        # Create the project folder path
        project_dir = ProjectService.get_project_dir(normalized_folder_name)

        # Check if folder already exists
        if os.path.exists(project_dir):
            raise FileExistsError(f"Project '{normalized_folder_name}' already exists.")

        # Create the folder
        os.makedirs(project_dir, exist_ok=True)

        # Process and save each file
        project_json_found = False
        saved_files = []

        for file in files:
            # Skip directories and empty files
            if not file.filename or file.filename.endswith('/'):
                continue

            # Get just the filename without any path
            filename = os.path.basename(file.filename)

            # Only save files that match our criteria
            if ProjectService.is_file_acceptable(filename):
                # Normalize the filename
                normalized_filename = ProjectService.normalize_filename(filename)
                file_path = os.path.join(project_dir, normalized_filename)

                # Save the file
                file.save(file_path)
                saved_files.append(normalized_filename)

                # Check if this is project.json
                if normalized_filename.lower() == 'project.json':
                    project_json_found = True

        # Verify we have project.json
        if not project_json_found:
            # Remove the created folder
            shutil.rmtree(project_dir, ignore_errors=True)
            raise ValueError("No project.json found in the uploaded folder.")

        # If no files were saved (all were filtered out)
        if not saved_files:
            # Remove the created folder
            shutil.rmtree(project_dir, ignore_errors=True)
            raise ValueError("No valid files (.c or project.json) found in the uploaded folder.")

        return normalized_folder_name
