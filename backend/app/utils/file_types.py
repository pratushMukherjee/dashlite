SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".rs",
    ".json", ".csv", ".xml", ".yaml", ".yml",
    ".png", ".jpg", ".jpeg",
}


def is_supported(file_path: str) -> bool:
    from pathlib import Path
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS


def get_file_type(file_path: str) -> str:
    from pathlib import Path
    return Path(file_path).suffix.lower().lstrip(".")
