from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class NewProjectForm(FlaskForm):
    """Form for creating a new project."""
    project_name = StringField('Project Name', validators=[DataRequired()])
    project_comment = TextAreaField('Project Comment')
    submit = SubmitField('Create Project')

class UploadProjectForm(FlaskForm):
    """Form for uploading a project file."""
    file = FileField('Project File', validators=[
        FileRequired(),
        FileAllowed(['json'], 'JSON files only!')
    ])
    submit = SubmitField('Upload Project')
