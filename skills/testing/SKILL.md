---
name: restaurant-testing
description: Tests restaurant website functionality before release.
---

# Restaurant Testing

Test the complete restaurant application.

Test:

- home page
- navigation
- menu
- reservation form
- required fields
- invalid email
- invalid phone
- missing customer name
- zero guests
- negative guests
- past dates
- invalid reservation time
- successful reservation
- reservation reference
- database storage
- confirmation page
- email handling
- mobile layout
- error handling

Do not report the application as ready until critical tests pass.

For every failed test:

1. Explain the problem.
2. Identify the likely cause.
3. Recommend or implement a fix.
4. Run the relevant test again.
5. Confirm whether the fix worked.

Prefer automated tests where possible.

The testing workflow should be:

Build
↓
Test
↓
Failure?
↓
Fix
↓
Retest
↓
Pass