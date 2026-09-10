---
name: restaurant-deployment
description: Prepares the restaurant application for safe production deployment.
---

# Restaurant Deployment

Before deployment:

1. Run all automated tests.
2. Run the security review.
3. Verify requirements.txt.
4. Verify environment variables.
5. Disable Flask debug mode.
6. Verify database configuration.
7. Verify email configuration.
8. Check static files.
9. Check production logging.
10. Document deployment steps.
11. Confirm secrets are excluded from Git.
12. Confirm production configuration differs from development where necessary.

Do not deploy when:

- critical tests are failing
- security review reports CRITICAL issues
- security review reports unresolved HIGH issues
- required environment variables are missing
- production email configuration is incomplete

Before declaring the application ready, produce a report containing:

- application status
- tests passed
- tests failed
- security status
- required environment variables
- database status
- email status
- remaining risks

Final result must be one of:

READY FOR DEPLOYMENT

or

NOT READY FOR DEPLOYMENT