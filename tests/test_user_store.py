import sqlite3

import pytest
from werkzeug.security import check_password_hash

from revtech.user_store import create_user, find_user, init_db, list_users


def test_init_db_seeds_admin_only_once(tmp_path):
    db_path = tmp_path / "users.db"

    init_db(db_path)
    init_db(db_path)

    users = list_users(db_path=db_path)
    assert [(user["username"], user["role"]) for user in users] == [
        ("admin", "admin")
    ]
    assert check_password_hash(find_user("admin", db_path)["password"], "admin")


def test_create_user_hashes_password_and_rejects_duplicate_username(tmp_path):
    db_path = tmp_path / "users.db"
    init_db(db_path)

    user_id = create_user("driver", "long-enough", db_path=db_path)

    user = find_user("driver", db_path)
    assert user["id"] == user_id
    assert user["role"] == "user"
    assert user["password"] != "long-enough"
    assert check_password_hash(user["password"], "long-enough")

    with pytest.raises(sqlite3.IntegrityError):
        create_user("driver", "another-password", db_path=db_path)
