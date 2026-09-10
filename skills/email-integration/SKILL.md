---
name: restaurant-email
description: Handles restaurant reservation email notifications.
---

# Restaurant Email Integration

After a reservation is successfully created:

1. Prepare a confirmation email for the customer.
2. Include the reservation reference.
3. Include the customer name.
4. Include the reservation date.
5. Include the reservation time.
6. Include the number of guests.
7. Include special requests when available.
8. Do not include passwords or internal system information.
9. Store email credentials in environment variables.
10. Handle email failures without losing the reservation.
11. Log email errors safely.
12. Do not expose SMTP credentials in source code.

Never hard-code:

- email passwords
- API keys
- SMTP credentials
- access tokens

Use environment variables such as:

MAIL_SERVER
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
RESTAURANT_EMAIL

The reservation should remain stored even if sending the email fails.

Before finishing, verify:

- email configuration loads correctly
- credentials are not hard-coded
- email contains the correct booking details
- email failures are handled safely