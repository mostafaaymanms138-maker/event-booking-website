import re

import app as bce
from conftest import login


def test_post_without_token_is_rejected(csrf_client, fake_db):
    login(csrf_client)
    resp = csrf_client.post("/waitlist/3")
    assert resp.status_code == 400
    assert not fake_db.ran("INSERT INTO waiting_list")


def test_login_post_without_token_is_rejected(csrf_client, fake_db):
    resp = csrf_client.post("/login", data={"email": "a@b.com", "password": "x"})
    assert resp.status_code == 400


def test_form_with_valid_token_is_accepted(csrf_client, fake_db):
    page = csrf_client.get("/login")
    token = re.search(rb'name="csrf_token" value="([^"]+)"', page.data).group(1).decode()
    resp = csrf_client.post("/login", data={"email": "a@b.com", "password": "x",
                                            "csrf_token": token})
    assert resp.status_code == 200            # normal "invalid login" page, not a 400


def test_every_post_form_in_the_templates_has_a_token():
    import glob
    import os
    root = os.path.join(os.path.dirname(bce.__file__), "templates")
    missing = []
    for path in glob.glob(os.path.join(root, "**", "*.html"), recursive=True):
        text = open(path, encoding="utf-8").read()
        for form in re.finditer(r"<form\b[^>]*method=\"POST\"[^>]*>(.*?)</form>", text, re.S | re.I):
            if "csrf_token" not in form.group(1):
                missing.append(os.path.relpath(path, root))
    assert not missing, f"POST forms without a CSRF token: {missing}"
