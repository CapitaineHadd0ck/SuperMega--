PROJECT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {"type": "string"},
        "project_comment": {"type": "string"},
        "c_file_path": {
            "type": "string",
            "format": "relative-path"
        },
    },
    "required": ["project_name", "c_file_path"]
}
