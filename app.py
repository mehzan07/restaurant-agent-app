import os
from datetime import date
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

REQUIRED_FIELDS = ("name", "email", "phone", "reservation_date", "reservation_time", "guests")


def validate_reservation(data):
    errors = {}
    for field in REQUIRED_FIELDS:
        if not str(data.get(field, "")).strip():
            errors[field] = "This field is required."

    email = str(data.get("email", "")).strip()
    if email and ("@" not in email or "." not in email.rsplit("@", 1)[-1]):
        errors["email"] = "Enter a valid email address."

    reservation_date = str(data.get("reservation_date", "")).strip()
    if reservation_date:
        try:
            if date.fromisoformat(reservation_date) < date.today():
                errors["reservation_date"] = "Choose today or a future date."
        except ValueError:
            errors["reservation_date"] = "Enter a valid date."

    try:
        guests = int(data.get("guests", 0))
        if guests < 1 or guests > 20:
            errors["guests"] = "Choose between 1 and 20 guests."
    except (TypeError, ValueError):
        errors["guests"] = "Enter a valid number of guests."

    return errors


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or request.form.to_dict()
    errors = validate_reservation(data)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # Storage will be added in a later version.
    app.logger.info("Reservation request received for %s", data.get("reservation_date"))
    return jsonify({"success": True, "message": "Your reservation request has been received."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
