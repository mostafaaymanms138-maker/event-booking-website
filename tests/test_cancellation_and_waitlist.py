from datetime import date, timedelta

from conftest import login


def booking_row(days_away, total=100.0, qty=2):
    return {"id": 9, "event_id": 3, "quantity": qty, "total_price": total,
            "reference": "BCE-2026-11111",
            "event_date": date.today() + timedelta(days=days_away)}


def test_free_cancellation_when_far_away(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(60)])
    client.post("/cancel/9")
    update = fake_db.ran("SET status='cancelled'")[0]
    assert update[1] == (0.0, 9)


def test_cancellation_charges_full_price_when_close(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(5)])
    client.post("/cancel/9")
    assert fake_db.ran("SET status='cancelled'")[0][1] == (100.0, 9)


def test_cancellation_returns_tickets_to_the_event(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(60, qty=3)])
    client.post("/cancel/9")
    assert fake_db.ran("tickets_remaining=tickets_remaining+")[0][1] == (3, 3)


def test_cannot_cancel_someone_elses_booking(client, fake_db):
    login(client)                                   # query finds no row for this user
    assert client.post("/cancel/9").status_code == 404


def test_cancellation_notifies_first_person_on_waiting_list(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(60)])
    fake_db.queue_rows("SELECT user_id FROM waiting_list", [{"user_id": 42}])
    client.post("/cancel/9")
    notify = fake_db.ran("UPDATE waiting_list SET notified=1")
    assert len(notify) == 1 and notify[0][1] == (42, 3)


def test_cancellation_with_empty_waiting_list_notifies_nobody(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(60)])
    client.post("/cancel/9")
    assert not fake_db.ran("UPDATE waiting_list")


def test_admin_cancellation_also_notifies_waiting_list(client, fake_db):
    login(client, admin=True)
    fake_db.queue_rows("FROM bookings b JOIN events", [booking_row(60)])
    fake_db.queue_rows("SELECT user_id FROM waiting_list", [{"user_id": 7}])
    client.post("/admin/bookings/cancel/9")
    assert fake_db.ran("UPDATE waiting_list SET notified=1")[0][1] == (7, 3)


def test_joining_waiting_list_inserts_once(client, fake_db):
    login(client, user_id=4)
    client.post("/waitlist/3")
    assert fake_db.ran("INSERT INTO waiting_list")[0][1] == (4, 3)


def test_joining_waiting_list_twice_does_not_duplicate(client, fake_db):
    login(client, user_id=4)
    fake_db.queue_rows("SELECT id FROM waiting_list", [{"id": 1}])
    client.post("/waitlist/3")
    assert not fake_db.ran("INSERT INTO waiting_list")


def _waitlist_row(notified):
    return {"joined_at": date.today(), "notified": notified, "event_id": 3,
            "event_name": "Jazz Night", "event_date": date.today() + timedelta(days=30),
            "venue_name": "The Hall"}


def test_my_bookings_tells_notified_user_a_place_opened(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM waiting_list w", [_waitlist_row(1)])
    resp = client.get("/my-bookings")
    assert b"A place has opened" in resp.data


def test_my_bookings_shows_waiting_for_users_still_in_line(client, fake_db):
    login(client)
    fake_db.queue_rows("FROM waiting_list w", [_waitlist_row(0)])
    resp = client.get("/my-bookings")
    assert b"Waiting" in resp.data and b"A place has opened" not in resp.data
