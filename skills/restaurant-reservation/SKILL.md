---
name: restaurant-reservation
description: Handles restaurant table reservation rules and validation.
---

# Restaurant Reservation

When processing a reservation:

1. Customer name is required.
2. A valid email or phone number is required.
3. Guest count must be valid.
4. Guest count must be greater than zero.
5. Reservation date cannot be in the past.
6. Reservation time must be inside restaurant opening hours.
7. Generate a unique reservation reference.
8. Save the reservation only after server-side validation.
9. Return a clear confirmation to the customer.
10. Never expose internal database IDs as customer booking references.
11. Invalid reservations must not be stored.
12. Special requests are optional.
13. Reservation status should have a valid value.

The reservation workflow should be:

Receive request
↓
Validate input
↓
Check business rules
↓
Generate reservation reference
↓
Save reservation
↓
Send confirmation
↓
Return result to customer

Before finishing, verify:

- required fields
- email format
- phone format
- guest count
- reservation date
- reservation time
- reservation reference
- successful database storage