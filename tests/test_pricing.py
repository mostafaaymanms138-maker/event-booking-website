from datetime import date, timedelta

import pytest

import app as bce


def in_days(n):
    return date.today() + timedelta(days=n)


@pytest.mark.parametrize("days, expected", [
    (60, 20), (50, 20),
    (49, 15), (35, 15),
    (34, 10), (25, 10),
    (24, 5), (15, 5),
    (14, 0), (0, 0), (-3, 0),
    (61, 0),
])
def test_advance_discount_bands(days, expected):
    assert bce.calc_advance_discount(in_days(days)) == expected


def test_advance_discount_accepts_date_string():
    assert bce.calc_advance_discount(str(in_days(55))) == 20


@pytest.mark.parametrize("days, charge", [
    (60, 0.0), (41, 0.0),        # more than 40 days: free
    (39, 40.0), (25, 40.0),      # 25-39 days: 40%
    (24, 100.0), (1, 100.0),     # under 25 days: full price
])
def test_cancellation_charge_bands(days, charge):
    assert bce.calc_cancellation_charge(in_days(days), 100) == charge


def test_cancellation_charge_rounds_to_pence():
    assert bce.calc_cancellation_charge(in_days(30), 33.33) == 13.33


def test_total_without_discounts():
    assert bce.calc_total(20, 3, 0, False) == 60.0


def test_total_with_advance_discount_only():
    assert bce.calc_total(20, 2, 20, False) == 32.0


def test_total_with_student_discount_only():
    assert bce.calc_total(20, 1, 0, True) == 18.0


def test_total_discounts_stack_advance_first_then_student():
    # 100 - 20% = 80, then -10% = 72
    assert bce.calc_total(50, 2, 20, True) == 72.0


def test_free_event_costs_nothing():
    assert bce.calc_total(0, 4, 20, True) == 0.0


def test_booking_reference_format():
    ref = bce.gen_reference()
    prefix, year, number = ref.split("-")
    assert prefix == "BCE"
    assert year == str(date.today().year)
    assert 10000 <= int(number) <= 99999
