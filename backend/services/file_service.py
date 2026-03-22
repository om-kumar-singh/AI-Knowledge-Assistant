"""Save uploaded files to local disk with validation."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from core.config import get_settings

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".txt"})
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
CHUNK_SIZE = 1024 * 1024


def _backend_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_uploads_directory() -> Path:
    """Absolute path to the uploads directory (under the backend package root)."""
    return _backend_root() / get_settings().uploads_dir


def ensure_upload_directory() -> Path:
    """Create `uploads/` (or configured dir) if it does not exist."""
    path = get_uploads_directory()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sanitize_basename(name: str) -> str:
    """Use only the final path segment and strip null bytes."""
    base = Path(name or "file").name.replace("\x00", "").strip()
    return base or "file"


def _safe_storage_stem(original_basename: str, max_len: int = 200) -> str:
    stem = Path(original_basename).stem
    stem = stem[:max_len] if len(stem) > max_len else stem
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in stem) or "file"


async def save_upload_file(file: UploadFile) -> tuple[str, str]:
    """
    Validate and persist an upload under the configured uploads directory.

    Returns:
        (relative_path, display_filename): `relative_path` is POSIX-style, relative to backend root
        (e.g. ``uploads/<uuid>_<name>.pdf``). `display_filename` is the sanitized original basename for DB storage.
    """
    original = _sanitize_basename(file.filename or "")
    suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and TXT files are allowed.")

    stem = _safe_storage_stem(original)
    ext = suffix
    unique_name = f"{uuid.uuid4()}_{stem}{ext}"

    uploads_dir = ensure_upload_directory()
    dest_abs = uploads_dir / unique_name
    relative = dest_abs.relative_to(_backend_root()).as_posix()

    total = 0
    try:
        with dest_abs.open("wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_BYTES:
                    raise ValueError("File exceeds the maximum size of 10 MB.")
                out.write(chunk)
    except ValueError:
        dest_abs.unlink(missing_ok=True)
        raise
    except Exception:
        dest_abs.unlink(missing_ok=True)
        raise

    display_filename = original[:512] if len(original) <= 512 else original[:509] + "..."
    return relative, display_filename
