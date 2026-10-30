"""Shared test setup.

The tests never touch MySQL. A small fake database replaces get_db(), records
every SQL statement the app runs, and returns rows that each test queues up.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "website"))
import app as bce  # noqa: E402


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.lastrowid = 7
        self._rows = []

    def execute(self, sql, params=None):
        self.db.executed.append((" ".join(sql.split()), params))
        # Pick the first queued result whose keyword appears in the statement
        for i, (needle, rows) in enumerate(self.db.queue):
            if needle in " ".join(sql.split()):
                self._rows = list(rows)
                del self.db.queue[i]
                return
        self._rows = []

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        rows, self._rows = self._rows, []
        return rows

    def close(self):
        pass


class FakeDB:
    def __init__(self):
        self.executed = []
        self.queue = []
        self.committed = False

    def queue_rows(self, needle, rows):
        """The next statement containing `needle` returns `rows`."""
        self.queue.append((needle, rows))

    def cursor(self, dictionary=False):
        return FakeCursor(self)

    def commit(self):
        self.committed = True

    def close(self):
        pass

    def ran(self, fragment):
        """All executed statements that contain `fragment`."""
        return [(s, p) for s, p in self.executed if fragment in s]


@pytest.fixture
def fake_db(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(bce, "get_db", lambda: db)
    return db


@pytest.fixture
def client():
    bce.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with bce.app.test_client() as c:
        yield c


@pytest.fixture
def csrf_client():
    """Client with CSRF protection switched ON, as in production."""
    bce.app.config.update(TESTING=True, WTF_CSRF_ENABLED=True)
    with bce.app.test_client() as c:
        yield c
    bce.app.config.update(WTF_CSRF_ENABLED=False)


def login(client, user_id=1, student=False, admin=False):
    with client.session_transaction() as s:
        s["user_id"] = user_id
        s["user_name"] = "Test User"
        s["is_student"] = student
        s["is_admin"] = admin
