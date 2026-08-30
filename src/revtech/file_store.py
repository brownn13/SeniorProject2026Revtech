"""Authenticated, encrypted storage for user-uploaded CSV files."""

import os
import shutil
import struct
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


UPLOAD_ROOT = Path(__file__).resolve().parent / "user_uploads"
_PAYLOAD_MAGIC = b"RVTECH01"
_HEADER = struct.Struct(">8sH")


class UploadAccessError(PermissionError):
    """Raised when a user attempts to access another user's upload."""


class CorruptUploadError(ValueError):
    """Raised when an encrypted upload cannot be authenticated or decoded."""


@dataclass(frozen=True)
class StoredUpload:
    upload_id: str
    original_name: str
    uploaded_at: datetime
    size: int | None
    readable: bool = True


@dataclass(frozen=True)
class LoadedUpload:
    upload_id: str
    original_name: str
    csv_bytes: bytes


def _cipher(encryption_key):
    key = (
        encryption_key.encode("ascii")
        if isinstance(encryption_key, str)
        else encryption_key
    )
    return Fernet(key)


def _authorize(requester, owner_id):
    requester_id = int(requester["id"])
    if requester_id != int(owner_id) and requester["role"] != "admin":
        raise UploadAccessError("You do not have access to this user's uploads.")


def _user_directory(owner_id, upload_root):
    owner_id = int(owner_id)
    if owner_id <= 0:
        raise ValueError("User IDs must be positive integers.")
    return Path(upload_root or UPLOAD_ROOT) / str(owner_id)


def _upload_path(owner_id, upload_id, upload_root):
    try:
        normalized_id = str(uuid.UUID(str(upload_id)))
    except ValueError as error:
        raise ValueError("Invalid upload ID.") from error
    if normalized_id != str(upload_id):
        raise ValueError("Invalid upload ID.")
    return _user_directory(owner_id, upload_root) / f"{normalized_id}.enc"


def _encode_payload(original_name, csv_bytes):
    safe_name = Path(original_name).name.strip()
    if not safe_name or "\x00" in safe_name:
        raise ValueError("The upload must have a valid filename.")

    filename_bytes = safe_name.encode("utf-8")
    if len(filename_bytes) > 4096:
        raise ValueError("The upload filename is too long.")
    return _HEADER.pack(_PAYLOAD_MAGIC, len(filename_bytes)) + filename_bytes + csv_bytes


def _decode_payload(encrypted_bytes, encryption_key):
    try:
        payload = _cipher(encryption_key).decrypt(encrypted_bytes)
        magic, filename_length = _HEADER.unpack(payload[: _HEADER.size])
        filename_end = _HEADER.size + filename_length
        filename = payload[_HEADER.size : filename_end].decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, struct.error, ValueError) as error:
        raise CorruptUploadError("The encrypted upload is unreadable.") from error

    if magic != _PAYLOAD_MAGIC or filename_end > len(payload) or not filename:
        raise CorruptUploadError("The encrypted upload has an invalid format.")
    return filename, payload[filename_end:]


def save_upload(
    requester,
    owner_id,
    original_name,
    csv_bytes,
    encryption_key,
    upload_root=None,
):
    """Encrypt and atomically save a CSV for an authorized owner."""
    _authorize(requester, owner_id)
    upload_id = str(uuid.uuid4())
    destination = _upload_path(owner_id, upload_id, upload_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination.with_suffix(f".{uuid.uuid4().hex}.tmp")
    encrypted_bytes = _cipher(encryption_key).encrypt(
        _encode_payload(original_name, csv_bytes)
    )

    try:
        temporary_path.write_bytes(encrypted_bytes)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)

    return StoredUpload(
        upload_id=upload_id,
        original_name=Path(original_name).name.strip(),
        uploaded_at=datetime.fromtimestamp(destination.stat().st_mtime, tz=UTC),
        size=len(csv_bytes),
    )


def list_uploads(requester, owner_id, encryption_key, upload_root=None):
    """List an owner's uploads without exposing CSV contents to the caller."""
    _authorize(requester, owner_id)
    user_directory = _user_directory(owner_id, upload_root)
    if not user_directory.exists():
        return []

    uploads = []
    for path in user_directory.glob("*.enc"):
        try:
            original_name, csv_bytes = _decode_payload(
                path.read_bytes(), encryption_key
            )
            readable = True
            size = len(csv_bytes)
        except (CorruptUploadError, OSError):
            original_name = "Unreadable encrypted file"
            readable = False
            size = None

        uploads.append(
            StoredUpload(
                upload_id=path.stem,
                original_name=original_name,
                uploaded_at=datetime.fromtimestamp(path.stat().st_mtime, tz=UTC),
                size=size,
                readable=readable,
            )
        )
    return sorted(uploads, key=lambda upload: upload.uploaded_at, reverse=True)


def load_upload(
    requester, owner_id, upload_id, encryption_key, upload_root=None
):
    """Authorize, authenticate, and decrypt one stored upload."""
    _authorize(requester, owner_id)
    path = _upload_path(owner_id, upload_id, upload_root)
    original_name, csv_bytes = _decode_payload(path.read_bytes(), encryption_key)
    return LoadedUpload(upload_id, original_name, csv_bytes)


def delete_upload(requester, owner_id, upload_id, upload_root=None):
    """Delete one upload after checking owner or administrator access."""
    _authorize(requester, owner_id)
    _upload_path(owner_id, upload_id, upload_root).unlink()


def delete_user_uploads(user_id, upload_root=None):
    """Remove all encrypted uploads after a user account is deleted."""
    user_directory = _user_directory(user_id, upload_root)
    if user_directory.exists():
        shutil.rmtree(user_directory)
