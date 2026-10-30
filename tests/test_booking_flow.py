from datetime import date, timedelta

from conftest import login


def event_row(tickets=10, days=55, price=20.0):
    return {"id": 3, "name": "Jazz Night", "venue_name": "The Hall",
            "category_name": "Music", "price": price, "tickets_remaining": tickets,
            "date": date.today() + timedelta(days=days), "time": None}


def test_booking_requires_login(client):
    resp = client.get("/booking/3")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_booking_applies_advance_and_student_discounts(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM events e", [event_row(days=55, price=50.0)])
    resp = client.post("/booking/3", data={"quantity": "2", "is_student": "on"})
    assert resp.status_code == 302 and "/payment" in resp.headers["Location"]
    with client.session_transaction() as s:
        pb = s["pending_booking"]
    assert pb["advance_pct"] == 20
    assert pb["total"] == 72.0           # 2 x 50, minus 20%, minus 10%
    assert pb["ref"].startswith("BCE-")


def test_booking_rejects_more_tickets_than_remaining(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM events e", [event_row(tickets=2)])
    resp = client.post("/booking/3", data={"quantity": "5"})
    assert resp.status_code == 302 and "/booking/3" in resp.headers["Location"]
    with client.session_transaction() as s:
        assert "pending_booking" not in s


def test_sold_out_event_redirects_to_event_page(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM events e", [event_row(tickets=0)])
    resp = client.get("/booking/3")
    assert resp.status_code == 302 and "/event/3" in resp.headers["Location"]


def _pending(client, qty=2):
    with client.session_transaction() as s:
        s["pending_booking"] = {
            "event_id": 3, "quantity": qty, "is_student": 0, "advance_pct": 0,
            "base_price": 20.0, "total": 40.0, "ref": "BCE-2026-12345",
            "event_name": "Jazz Night", "venue_name": "The Hall",
            "event_date": "2026-12-01", "event_time": ""}


GOOD_CARD = {"card_number": "4242 4242 4242 4242", "expiry": "12/30", "cvv": "123"}


def test_payment_creates_booking_reduces_tickets_and_leaves_waitlist(client, fake_db):
    login(client)
    _pending(client, qty=2)
    fake_db.queue_rows("SELECT tickets_remaining", [{"tickets_remaining": 10}])
    resp = client.post("/payment", data=GOOD_CARD)
    assert resp.status_code == 302 and "/receipt/" in resp.headers["Location"]
    assert fake_db.ran("INSERT INTO bookings")
    reduce = fake_db.ran("tickets_remaining=tickets_remaining-")[0]
    assert reduce[1] == (2, 3)
    assert fake_db.ran("DELETE FROM waiting_list")[0][1] == (1, 3)
    assert fake_db.committed
    with client.session_transaction() as s:
        assert "pending_booking" not in s


def test_payment_rejects_bad_card_number(client, fake_db):
    login(client)
    _pending(client)
    resp = client.post("/payment", data={**GOOD_CARD, "card_number": "1234"})
    assert b"Invalid card number" in resp.data
    assert not fake_db.ran("INSERT INTO bookings")


def test_payment_stops_if_tickets_sold_in_the_meantime(client, fake_db):
    login(client)
    _pending(client, qty=4)
    fake_db.queue_rows("SELECT tickets_remaining", [{"tickets_remaining": 1}])
    resp = client.post("/payment", data=GOOD_CARD)
    assert resp.status_code == 302 and "/event/3" in resp.headers["Location"]
    assert not fake_db.ran("INSERT INTO bookings")
