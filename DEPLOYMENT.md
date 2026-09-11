# Production deployment (Version 8)

## Requirements

- Python 3.10+ and a persistent writable directory for SQLite
- Install dependencies with `python -m pip install -r requirements.txt`.
- Configure `RESERVATION_DATABASE` to a persistent path (the default is the project directory).
- Configure `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_FROM` using the platform secret manager. Never commit `.env` or credentials.

## Launch

Run the production WSGI server:

```sh
gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile - --error-logfile - app:app
```

The included `Procfile` uses the same command. Flask debug mode is disabled; do not use `flask run` in production.

## Database and email

`app.py` initializes the existing SQLite schema on startup and preserves booking references and reservations. Back up the SQLite file and ensure only the application user can write it. For multiple application instances, use a managed database before scaling beyond a single instance. SMTP credentials must be supplied as environment variables; verify delivery with a non-customer test address.

## Pre-release checklist

1. Install dependencies and run `pytest`.
2. Set all production environment variables and verify the database directory exists and is writable.
3. Confirm HTTPS is enabled at the reverse proxy/platform.
4. Confirm `.env` and SQLite files are excluded from Git.
5. Submit a test reservation, verify its reference, database row, and email.
6. Configure backups, monitoring, and log retention. Logs contain reservation references on email failures but not SMTP passwords.
