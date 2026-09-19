"""
file_operations.py
-------------------
Core create / read / update / delete logic for the File Manager app.

All operations are sandboxed to WORKSPACE_DIR so that filenames coming
from user input (via the Streamlit UI) can never escape the intended
folder (e.g. via "../../etc/passwd").

Every function returns a (success: bool, message_or_content: str) tuple
instead of printing, so the same module can be reused by a CLI, a
Streamlit UI, tests, etc.
"""

import os
from pathlib import Path

# All files created/read/updated/deleted by this app live inside this folder.
WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"


def ensure_workspace() -> None:
    """Create the workspace folder if it doesn't already exist."""
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_path(filename: str) -> Path:
    """
    Resolve `filename` relative to WORKSPACE_DIR and guarantee the
    resolved path still lives inside WORKSPACE_DIR (blocks path
    traversal like '../secret.txt').
    """
    ensure_workspace()
    candidate = (WORKSPACE_DIR / filename).resolve()
    if WORKSPACE_DIR.resolve() not in candidate.parents and candidate != WORKSPACE_DIR.resolve():
        raise ValueError("Invalid filename: path escapes the workspace folder.")
    return candidate


def list_files() -> list[str]:
    """Return a sorted list of file names currently in the workspace."""
    ensure_workspace()
    return sorted(p.name for p in WORKSPACE_DIR.iterdir() if p.is_file())


def create_file(filename: str, content: str) -> tuple[bool, str]:
    """Create a new file. Fails if the file already exists."""
    try:
        path = _safe_path(filename)
        if path.exists():
            return False, f"File '{filename}' already exists."
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"File '{filename}' created successfully."
    except Exception as error:
        return False, f"Unable to create file: {error}"


def read_file(filename: str) -> tuple[bool, str]:
    """Read and return the contents of a file."""
    try:
        path = _safe_path(filename)
        if not path.exists():
            return False, f"File '{filename}' does not exist."
        with open(path, "r", encoding="utf-8") as f:
            return True, f.read()
    except Exception as error:
        return False, f"Unable to read file: {error}"


def overwrite_file(filename: str, content: str) -> tuple[bool, str]:
    """Overwrite an existing file's contents."""
    try:
        path = _safe_path(filename)
        if not path.exists():
            return False, f"File '{filename}' does not exist."
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"File '{filename}' overwritten successfully."
    except Exception as error:
        return False, f"Unable to update file: {error}"


def append_file(filename: str, content: str) -> tuple[bool, str]:
    """Append content to an existing file."""
    try:
        path = _safe_path(filename)
        if not path.exists():
            return False, f"File '{filename}' does not exist."
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return True, f"Content appended to '{filename}' successfully."
    except Exception as error:
        return False, f"Unable to update file: {error}"


def rename_file(filename: str, new_filename: str) -> tuple[bool, str]:
    """Rename/move a file within the workspace."""
    try:
        old_path = _safe_path(filename)
        new_path = _safe_path(new_filename)
        if not old_path.exists():
            return False, f"File '{filename}' does not exist."
        if new_path.exists():
            return False, f"File '{new_filename}' already exists."
        os.rename(old_path, new_path)
        return True, f"File renamed to '{new_filename}' successfully."
    except Exception as error:
        return False, f"Unable to rename file: {error}"


def delete_file(filename: str) -> tuple[bool, str]:
    """Delete a file from the workspace."""
    try:
        path = _safe_path(filename)
        if not path.exists():
            return False, f"File '{filename}' does not exist."
        os.remove(path)
        return True, f"File '{filename}' deleted successfully."
    except Exception as error:
        return False, f"Unable to delete file: {error}"
