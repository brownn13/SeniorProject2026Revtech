import pytest
from cryptography.fernet import Fernet

from revtech.file_store import (
    CorruptUploadError,
    UploadAccessError,
    delete_upload,
    delete_user_uploads,
    list_uploads,
    load_upload,
    save_upload,
)


@pytest.fixture
def encryption_key():
    return Fernet.generate_key()


@pytest.fixture
def user():
    return {"id": 1, "username": "driver", "role": "user"}


def test_upload_is_encrypted_and_round_trips(tmp_path, encryption_key, user):
    csv_bytes = b"Time,RPM\n0,900\n1,1200\n"

    saved = save_upload(
        user,
        user["id"],
        "private/track-session.csv",
        csv_bytes,
        encryption_key,
        tmp_path,
    )

    encrypted_path = tmp_path / "1" / f"{saved.upload_id}.enc"
    encrypted_bytes = encrypted_path.read_bytes()
    assert csv_bytes not in encrypted_bytes
    assert b"track-session.csv" not in encrypted_bytes
    assert encrypted_path.name == f"{saved.upload_id}.enc"

    uploads = list_uploads(user, user["id"], encryption_key, tmp_path)
    assert len(uploads) == 1
    assert uploads[0].original_name == "track-session.csv"
    assert uploads[0].size == len(csv_bytes)

    loaded = load_upload(
        user, user["id"], saved.upload_id, encryption_key, tmp_path
    )
    assert loaded.original_name == "track-session.csv"
    assert loaded.csv_bytes == csv_bytes


def test_owner_isolation_and_admin_access(tmp_path, encryption_key, user):
    other_user = {"id": 2, "username": "other", "role": "user"}
    admin = {"id": 3, "username": "admin", "role": "admin"}
    saved = save_upload(
        user, user["id"], "log.csv", b"RPM\n1000\n", encryption_key, tmp_path
    )

    with pytest.raises(UploadAccessError):
        list_uploads(other_user, user["id"], encryption_key, tmp_path)
    with pytest.raises(UploadAccessError):
        load_upload(
            other_user, user["id"], saved.upload_id, encryption_key, tmp_path
        )
    with pytest.raises(UploadAccessError):
        delete_upload(other_user, user["id"], saved.upload_id, tmp_path)

    loaded = load_upload(
        admin, user["id"], saved.upload_id, encryption_key, tmp_path
    )
    assert loaded.original_name == "log.csv"
    delete_upload(admin, user["id"], saved.upload_id, tmp_path)
    assert list_uploads(user, user["id"], encryption_key, tmp_path) == []


def test_corrupt_upload_can_be_identified_and_deleted(
    tmp_path, encryption_key, user
):
    saved = save_upload(
        user, user["id"], "log.csv", b"RPM\n1000\n", encryption_key, tmp_path
    )
    encrypted_path = tmp_path / "1" / f"{saved.upload_id}.enc"
    encrypted_path.write_bytes(b"not-valid-ciphertext")

    uploads = list_uploads(user, user["id"], encryption_key, tmp_path)
    assert len(uploads) == 1
    assert uploads[0].readable is False
    assert uploads[0].original_name == "Unreadable encrypted file"

    with pytest.raises(CorruptUploadError):
        load_upload(user, user["id"], saved.upload_id, encryption_key, tmp_path)

    delete_upload(user, user["id"], saved.upload_id, tmp_path)
    assert not encrypted_path.exists()


def test_delete_user_uploads_removes_only_that_user(
    tmp_path, encryption_key, user
):
    admin = {"id": 3, "username": "admin", "role": "admin"}
    save_upload(user, 1, "one.csv", b"x\n1\n", encryption_key, tmp_path)
    save_upload(admin, 2, "two.csv", b"x\n2\n", encryption_key, tmp_path)

    delete_user_uploads(1, tmp_path)

    assert not (tmp_path / "1").exists()
    assert (tmp_path / "2").exists()
