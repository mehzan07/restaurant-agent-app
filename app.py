import os
import secrets
import smtplib
import sqlite3
from datetime import date, datetime
from email.message import EmailMessage
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DATABASE = os.environ.get("RESERVATION_DATABASE", os.path.join(os.path.dirname(__file__), "reservations.sqlite3"))
REQUIRED_FIELDS = ("name", "email", "phone", "reservation_date", "reservation_time", "guests")
ALLOWED_TIMES = {"5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM"}
MAX_LENGTHS = {"name": 100, "email": 254, "phone": 30, "special_requests": 1000}


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_reference TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                reservation_date TEXT NOT NULL,
                reservation_time TEXT NOT NULL,
                guests INTEGER NOT NULL CHECK (guests > 0),
                special_requests TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TEXT NOT NULL
            )
        """)


def validate_reservation(data):
    errors = {}
    for field in REQUIRED_FIELDS:
        value = str(data.get(field, "")).strip()
        if not value:
            errors[field] = "This field is required."
        elif field in MAX_LENGTHS and len(value) > MAX_LENGTHS[field]:
            errors[field] = "This field is too long."
    special = str(data.get("special_requests", "")).strip()
    if len(special) > MAX_LENGTHS["special_requests"]:
        errors["special_requests"] = "Special requests are too long."
    email = str(data.get("email", "")).strip()
    if email and (len(email) > 254 or "@" not in email or "." not in email.rsplit("@", 1)[-1]):
        errors["email"] = "Enter a valid email address."
    reservation_date = str(data.get("reservation_date", "")).strip()
    if reservation_date:
        try:
            if date.fromisoformat(reservation_date) < date.today():
                errors["reservation_date"] = "Choose today or a future date."
        except ValueError:
            errors["reservation_date"] = "Enter a valid date."
    if str(data.get("reservation_time", "")).strip() not in ALLOWED_TIMES:
        errors["reservation_time"] = "Choose an available time."
    try:
        guests = int(data.get("guests", 0))
        if guests < 1 or guests > 20:
            errors["guests"] = "Choose between 1 and 20 guests."
    except (TypeError, ValueError):
        errors["guests"] = "Enter a valid number of guests."
    return errors


def create_reference():
    return f"TR-{datetime.now().strftime('%y%m%d')}-{secrets.randbelow(10000):04d}"


def send_confirmation(reservation):
    server = os.environ.get("MAIL_SERVER")
    username = os.environ.get("MAIL_USERNAME")
    password = os.environ.get("MAIL_PASSWORD")
    try:
        port = int(os.environ.get("MAIL_PORT", "587"))
    except ValueError:
        raise RuntimeError("Invalid email service configuration")
    sender = os.environ.get("MAIL_FROM") or username or os.environ.get("RESTAURANT_EMAIL")
    if not server or not sender or not (1 <= port <= 65535):
        raise RuntimeError("Email service is not configured")

    special = reservation["special_requests"] or "None"
    message = EmailMessage()
    message["Subject"] = f"Your Citrine & Salt reservation — {reservation['reservation_reference']}"
    message["From"] = sender
    message["To"] = reservation["email"]
    message.set_content(
        f"Hello {reservation['customer_name']},\n\nYour reservation is confirmed.\n\n"
        f"Booking reference: {reservation['reservation_reference']}\n"
        f"Date: {reservation['reservation_date']}\nTime: {reservation['reservation_time']}\n"
        f"Guests: {reservation['guests']}\nSpecial requests: {special}\n\n"
        "We look forward to welcoming you.\nCitrine & Salt"
    )
    with smtplib.SMTP(server, port, timeout=15) as smtp:
        smtp.ehlo()
        if port != 25:
            smtp.starttls()
            smtp.ehlo()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or request.form.to_dict()
    errors = validate_reservation(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    connection = get_db()
    try:
        reference = create_reference()
        while connection.execute("SELECT 1 FROM reservations WHERE reservation_reference = ?", (reference,)).fetchone():
            reference = create_reference()
        connection.execute("""
            INSERT INTO reservations
            (reservation_reference, customer_name, email, phone, reservation_date,
             reservation_time, guests, special_requests, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (reference, str(data["name"]).strip(), str(data["email"]).strip(),
              str(data["phone"]).strip(), str(data["reservation_date"]).strip(),
              str(data["reservation_time"]).strip(), int(data["guests"]),
              str(data.get("special_requests", "")).strip(), "confirmed",
              datetime.utcnow().isoformat(timespec="seconds") + "Z"))
        connection.commit()
        reservation = connection.execute("SELECT * FROM reservations WHERE reservation_reference = ?", (reference,)).fetchone()
    except sqlite3.Error:
        connection.rollback()
        app.logger.exception("Unable to save reservation")
        return jsonify({"success": False, "message": "We could not save your reservation. Please try again."}), 500
    finally:
        connection.close()

    try:
        send_confirmation(reservation)
        message = f"Your reservation is confirmed. Booking reference: {reference}. A confirmation email has been sent."
    except Exception:
        app.logger.exception("Reservation confirmation email failed for reference %s", reference)
        message = f"Your reservation is confirmed. Booking reference: {reference}. We could not send the email, so please keep this reference."
    return jsonify({"success": True, "reference": reference, "message": message})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
