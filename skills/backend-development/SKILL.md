---
name: restaurant-backend
description: Implements the restaurant backend using Python and Flask.
---

# Restaurant Backend Development

Use Python and Flask.

Responsibilities:

1. Create Flask routes.
2. Process reservation requests.
3. Validate all incoming data on the server.
4. Keep business logic separate from presentation.
5. Return useful error messages.
6. Never trust browser validation alone.
7. Use environment variables for secrets.
8. Log errors without exposing sensitive information.
9. Keep the code modular.
10. Prepare the application for production deployment.

Prefer clear separation between:

- routes
- validation
- database operations
- email logic
- configuration

Before finishing, verify:

- routes work
- invalid requests are rejected
- errors are handled safely
- secrets are not hard-coded
- debug information is not exposed to users