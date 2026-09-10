---
name: restaurant-database
description: Designs and maintains the restaurant reservation database.
---

# Restaurant Database Design

Create a database suitable for restaurant reservations.

The reservation model should contain:

- id
- reservation_reference
- customer_name
- email
- phone
- reservation_date
- reservation_time
- guests
- special_requests
- status
- created_at

Rules:

1. Every reservation must have a unique identifier.
2. Every reservation must have a unique public reservation reference.
3. Validate required values.
4. Use appropriate data types.
5. Do not store unnecessary sensitive information.
6. Design the schema so it can later support an admin interface.
7. Keep database operations separate from presentation code.
8. Use parameterized queries or a safe ORM.
9. Avoid exposing internal database IDs to customers.
10. Prepare the schema for future extensions.

Possible future extensions include:

- menu items
- restaurant settings
- opening hours
- table availability
- reservation status history

Before finishing, verify:

- required columns exist
- constraints are correct
- reservation references are unique
- queries are safe
- database errors are handled correctly