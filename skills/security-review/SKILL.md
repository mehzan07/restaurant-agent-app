---
name: restaurant-security
description: Reviews the restaurant application for common security problems.
---

# Restaurant Security Review

Check for:

- hard-coded passwords
- exposed API keys
- exposed environment variables
- missing server-side validation
- SQL injection
- unsafe HTML output
- cross-site scripting risks
- insecure dependencies
- excessive error information
- unsafe file operations
- unnecessary permissions
- secrets committed to Git
- Flask debug mode enabled in production

Before deployment verify:

1. Secrets use environment variables.
2. Debug mode is disabled in production.
3. User input is validated.
4. Database queries are safe.
5. Sensitive information is not logged.
6. Internal error details are not shown to users.
7. Dependencies are reviewed.
8. Configuration files do not expose credentials.

Classify findings as:

CRITICAL
HIGH
MEDIUM
LOW

Do not recommend deployment while CRITICAL or HIGH security issues remain unresolved.