import os
from jsonschema import FormatChecker

# Format checker for JSON schema validation
format_checker = FormatChecker()

@format_checker.checks("relative-path")
def is_relative_path(path):
    """Check if a path is relative."""
    return not os.path.isabs(path)  # Returns True if relative
