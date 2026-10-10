"""File storage for image attachments.

Images attached in the chat are saved under ``chat_attachments/{expert_id}/``.
Messages only reference them (see ``lib.shared.attachments``), which keeps the
chat history small and token counting accurate. The images are turned into
base64 data URLs only when a request is sent to the LLM.
"""

import base64
import mimetypes
import shutil
import uuid
from pathlib import Path
from typing import Optional

from lib.shared.file_ops import (
    ensure_directory_exists,
    get_project_root,
    safe_path_join,
)

CHAT_ATTACHMENTS_DIR = Path("chat_attachments")


def get_attachments_dir() -> Path:
    """Get the absolute path of the attachments directory in the project root."""
    return (get_project_root() / CHAT_ATTACHMENTS_DIR).resolve()


def save_image(expert_id: str, name: str, data: bytes) -> str:
    """Save an image attachment for an expert.

    Args:
        expert_id: Unique expert identifier
        name: Original file name (only its extension is used on disk)
        data: Image bytes

    Returns:
        str: Reference relative to CHAT_ATTACHMENTS_DIR, e.g.
        ``"1004_spell_checker/3f2a....png"``
    """
    expert_dir = safe_path_join(get_attachments_dir(), expert_id)
    ensure_directory_exists(expert_dir)
    filename = f"{uuid.uuid4().hex}{Path(name).suffix.lower()}"
    (expert_dir / filename).write_bytes(data)
    return f"{expert_id}/{filename}"


def get_image_path(ref: str) -> Optional[Path]:
    """Resolve an image reference to its file path.

    Args:
        ref: Reference as returned by ``save_image()``

    Returns:
        Path | None: The file path, or None if the reference is invalid or
        the file no longer exists
    """
    try:
        path = safe_path_join(get_attachments_dir(), ref)
    except ValueError:
        return None
    return path if path.is_file() else None


def get_image_data_url(ref: str) -> Optional[str]:
    """Return an image as a base64 data URL for the LLM API.

    Args:
        ref: Reference as returned by ``save_image()``

    Returns:
        str | None: ``data:<mime>;base64,...``, or None if the file is missing
    """
    path = get_image_path(ref)
    if path is None:
        return None
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def delete_expert_attachments(expert_id: str) -> None:
    """Delete all image attachments of an expert.

    Args:
        expert_id: Unique expert identifier
    """
    base_dir = get_attachments_dir()
    try:
        expert_dir = safe_path_join(base_dir, expert_id)
    except ValueError:
        return
    # An empty ID would resolve to the base dir and delete every expert's images
    if expert_dir != base_dir and expert_dir.is_dir():
        shutil.rmtree(expert_dir)
