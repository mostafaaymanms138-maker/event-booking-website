from datetime import date

from werkzeug.security import check_password_hash

from conftest import login


def test_register_stores_hash_not_plain_text(client, fake_db):
    fake_db.queue_rows("SELECT id FROM users", [])        # email not taken
    resp = client.post("/register", data={
        "full_name": "Sam Student", "email": "Sam@Example.com",
        "password": "correct-horse", "confirm_password": "correct-horse",
        "is_student": "on",
    })
    assert resp.status_code == 302
    insert = fake_db.ran("INSERT INTO users")[0]
    name, email, stored, is_student = insert[1]
    assert email == "sam@example.com"                      # lower-cased
    assert stored != "correct-horse"                       # never plain text
    assert check_password_hash(stored, "correct-horse")    # but verifiable
    assert is_student == 1


def test_register_rejects_short_password(client, fake_db):
    resp = client.post("/register", data={
        "full_name": "A", "email": "a@b.com",
        "password": "short", "confirm_password": "short"})
    assert b"at least 8 characters" in resp.data
    assert not fake_db.ran("INSERT INTO users")


def test_register_rejects_mismatched_passwords(client, fake_db):
    resp = client.post("/register", data={
        "full_name": "A", "email": "a@b.com",
        "password": "longenough1", "confirm_password": "different1"})
    assert b"do not match" in resp.data
    assert not fake_db.ran("INSERT INTO users")


def test_login_succeeds_with_correct_password(client, fake_db):
    from werkzeug.security import generate_password_hash
    fake_db.queue_rows("SELECT * FROM users", [{
        "id": 5, "full_name": "Sam", "is_student": 0, "is_admin": 0,
        "password_hash": generate_password_hash("right-password")}])
    resp = client.post("/login", data={"email": "sam@example.com",
                                       "password": "right-password"})
    assert resp.status_code == 302
    with client.session_transaction() as s:
        assert s["user_id"] == 5


def test_login_fails_with_wrong_password(client, fake_db):
    from werkzeug.security import generate_password_hash
    fake_db.queue_rows("SELECT * FROM users", [{
        "id": 5, "full_name": "Sam", "is_student": 0, "is_admin": 0,
        "password_hash": generate_password_hash("right-password")}])
    resp = client.post("/login", data={"email": "sam@example.com",
                                       "password": "wrong-password"})
    assert b"Invalid email or password" in resp.data
    with client.session_transaction() as s:
        assert "user_id" not in s


def test_change_password_stores_new_hash(client, fake_db):
    from werkzeug.security import generate_password_hash
    login(client)
    fake_db.queue_rows("SELECT password_hash", [{"password_hash": generate_password_hash("old-password")}])
    fake_db.queue_rows("SELECT * FROM users", [{"id": 1, "full_name": "T", "email": "t@t.com", "created_at": date.today(), "is_student": 0}])
    client.post("/account", data={"action": "change_password",
                                  "current_password": "old-password",
                                  "new_password": "new-password-1",
                                  "confirm_password": "new-password-1"})
    update = fake_db.ran("UPDATE users SET password_hash")[0]
    assert check_password_hash(update[1][0], "new-password-1")
