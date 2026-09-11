import importlib
import sqlite3
from datetime import date, timedelta

import pytest


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    database = tmp_path / "test-reservations.sqlite3"
    monkeypatch.setenv("RESERVATION_DATABASE", str(database))
    monkeypatch.delenv("MAIL_SERVER", raising=False)
    monkeypatch.delenv("MAIL_USERNAME", raising=False)
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)
    monkeypatch.delenv("MAIL_FROM", raising=False)
    monkeypatch.delenv("RESTAURANT_EMAIL", raising=False)
    import app
    module = importlib.reload(app)
    yield module


@pytest.fixture
def client(app_module):
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def payload(**overrides):
    value = {
        "name": "Alex Morgan", "email": "alex@example.com", "phone": "5551234567",
        "reservation_date": (date.today() + timedelta(days=1)).isoformat(),
        "reservation_time": "7:00 PM", "guests": "2", "special_requests": "Window seat"
    }
    value.update(overrides)
    return value


def post(client, **overrides):
    return client.post("/api/reservations", json=payload(**overrides))


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.parametrize("overrides,field", [
    ({"name": ""}, "name"),
    ({"email": "not-an-email"}, "email"),
    ({"guests": "0"}, "guests"),
    ({"guests": "-1"}, "guests"),
    ({"reservation_date": (date.today() - timedelta(days=1)).isoformat()}, "reservation_date"),
    ({"reservation_time": "10:00 PM"}, "reservation_time"),
])
def test_invalid_reservations_are_rejected(client, overrides, field):
    response = post(client, **overrides)
    assert response.status_code == 400
    assert field in response.get_json()["errors"]


def test_success_reference_and_database_storage(client, app_module):
    response = post(client)
    body = response.get_json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["reference"] in body["message"]
    with sqlite3.connect(app_module.DATABASE) as db:
        row = db.execute("SELECT reservation_reference, customer_name FROM reservations").fetchone()
    assert row[0] == body["reference"]
    assert row[1] == "Alex Morgan"


def test_booking_references_are_unique(client):
    first = post(client).get_json()["reference"]
    second = post(client, email="other@example.com").get_json()["reference"]
    assert first != second


def test_email_success_behavior(client, app_module, monkeypatch):
    sent = []
    monkeypatch.setattr(app_module, "send_confirmation", lambda reservation: sent.append(reservation["reservation_reference"]))
    body = post(client).get_json()
    assert sent == [body["reference"]]


def test_email_failure_keeps_reservation_and_reference(client, app_module, monkeypatch):
    def fail(_reservation):
        raise RuntimeError("SMTP unavailable")
    monkeypatch.setattr(app_module, "send_confirmation", fail)
    response = post(client)
    body = response.get_json()
    assert response.status_code == 200
    assert body["reference"] in body["message"]
    with sqlite3.connect(app_module.DATABASE) as db:
        assert db.execute("SELECT 1 FROM reservations WHERE reservation_reference = ?", (body["reference"],)).fetchone()
