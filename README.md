# AI Career Pro

AI Career Pro is a Django web app that helps users create CV profiles and generate tailored cover letters from job descriptions.

## Assessment Criteria Mapping

This section maps project evidence to the assessment learning outcomes.

- LO1 (Agile planning and design): GitHub Project board + user stories in USER_STORIES.md, responsive UI, accessible structure, Bootstrap-based layout.
- LO2 (Data model, features, business logic): Custom models, ORM queries, migrations, CRUD, validation, and notifications.
- LO3 (Authentication and authorization): Signup/login/logout, login-state-aware UI, protected routes, ownership checks.
- LO4 (Testing): Automated Django tests for auth, CRUD, privacy, and key billing flows.
- LO5 (Git and secure code management): Git/GitHub workflow with environment variables and secret handling.
- LO6 (Deployment and security): Heroku deployment with PostgreSQL, WhiteNoise, production security settings, and documented deployment steps.
- LO7 (Object-based software concepts): Custom Django ORM models and relationships (`CV`, `CoverLetter`, `Profile`).
- LO8 (AI-assisted workflow): AI used for feature implementation, debugging, UX/performance improvements, and unit-test support.

## Live App

- Live URL: Add your deployed Heroku URL
- Admin URL: Add your deployed Heroku admin URL

## Features

- User signup, login, and logout
- CV create, edit, and delete
- AI-powered tailored cover-letter generation
- Saved letters dashboard with search and pagination
- Premium upgrade flow with Stripe checkout and billing portal
- Premium PDF export for saved letters
- Responsive and accessible UI improvements

## UX Design Process (LO1.1, LO1.5)

- Initial design intent: Provide a fast application workflow from CV profile to tailored letter.
- Accessibility considerations implemented: semantic HTML structure, skip-link usage, clear form labels, and readable feedback states.
- Responsive behavior implemented: Bootstrap grid/layout, mobile-stacking action controls, and adaptive navigation.
- Iterative improvements made: clearer call-to-action flow, structured output format for generated letters, and dedicated public homepage.

Add your own artefacts here before submission:

- Wireframes: Add links/images.
- Mockups: Add links/images.
- Design changes log: Briefly list what changed and why.

## Tech Stack

- Django
- PostgreSQL on Heroku (SQLite fallback for local development)
- Bootstrap 5
- Stripe
- Google GenAI
- ReportLab
- Gunicorn + WhiteNoise

## Database Design and Data Handling (LO1.2, LO2.1, LO7.1)

- Custom models:
	- `CV`: Stores reusable candidate profile data.
	- `CoverLetter`: Stores generated outputs linked to user and CV.
	- `Profile`: Stores premium/subscription metadata per user.
- Relationships:
	- User -> CV (one-to-many)
	- User -> CoverLetter (one-to-many)
	- CV -> CoverLetter (one-to-many)
	- User -> Profile (one-to-one)
- Migrations are used to evolve schema and are tracked in version control.
- Django ORM is used for all core create/read/update/delete operations with user ownership scoping.

## CRUD and Business Logic (LO2.2)

- CV CRUD: create, update, delete, and list operations with ownership checks.
- Cover letter CRUD: generate/save, view, and delete operations per authenticated user.
- Dashboard search and pagination for letter management.

## Forms and Validation (LO2.4)

- `SignupForm` includes custom validation (e.g., duplicate email handling).
- `CVForm` validates required fields and trims whitespace.
- Templates render clear field-level and form-level error messages.

## User Notifications (LO2.3)

- Near-real-time in-app notifications are implemented with Django messages for key events:
	- account creation
	- CV create/update/delete
	- letter create/delete
	- billing and premium state feedback
- Optional welcome email notification on signup when email is provided.

## Authentication, Authorization, and Access Control (LO3)

- Registration, login, and logout are implemented with Django auth.
- Login state is reflected in navigation and page actions.
- Restricted routes are protected with `@login_required`.
- Access control is enforced with user-scoped object lookups to prevent cross-user access.

## Deployment Notes

- Procfile is configured for Gunicorn
- runtime.txt pins Python version for Heroku stability
- Static files served via WhiteNoise
- Database configured via DATABASE_URL

Typical post-deploy steps:

1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`

## Deployment Procedure (LO6.2)

1. Push latest code to GitHub.
2. Trigger Heroku deployment from connected branch.
3. Ensure required config vars are set.
4. Run `python manage.py migrate` in Heroku console.
5. Run `python manage.py collectstatic --noinput` in Heroku console.
6. Verify live routes: homepage, signup/login, app flow, dashboard, and admin.

## Environment Variables

Required:

- `DJANGO_SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`

Optional:

- `STRIPE_CURRENCY`
- `STRIPE_PREMIUM_MONTHLY_PENCE`
- `STRIPE_PREMIUM_MONTHLY_DISPLAY`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`

## Security Notes (LO5.2, LO6.3)

- Secrets are managed via environment variables and not hardcoded in source.
- `.env` is used for local development and should remain ignored in Git.
- Production deployment uses `DEBUG=False`.
- Allowed hosts and CSRF trusted origins are configured for deployed domain.
- Secure cookie and HTTPS-related settings are enabled in production mode.

## Version Control and Project Tracking (LO1.3, LO5.1)

- Development was tracked with Git and GitHub commits.
- Agile planning/tracking was maintained using user stories and a GitHub Project board.
- User stories are documented in `USER_STORIES.md` and linked to delivered functionality.

## Testing

Run tests locally with:

`python manage.py test`

### Python Test Procedures (LO4.1)

Automated tests cover:

- authentication and signup behavior
- CV CRUD operations
- privacy/authorization boundaries
- dashboard filtering
- key Stripe-related flow behaviors

### JavaScript Testing (LO4.2)

- No dedicated JS test framework was added for this submission.
- JavaScript behavior (form submit states/copy actions/navigation UX) was validated manually during feature testing.

### Testing Documentation (LO4.3)

- Test strategy: combination of automated Django tests and manual end-to-end verification on deployed app.
- Expected outcome: no failing tests and working deployed core flows.
- Actual outcome: test suite passes locally (`manage.py test`) and deployed workflows were validated.

## Agile Evidence

See project on github for user stories, priorities, and acceptance criteria.

## AI Usage Reflection (LO8)

- AI-assisted code creation: Used for accelerating initial implementation of views/templates/forms and refactoring support.
- AI-assisted debugging: Used to diagnose deployment/runtime issues (e.g., runtime compatibility and environment/config mismatches).
- AI-assisted optimization: Used for iterative UX/accessibility/responsive and reliability improvements.
- AI-assisted test support: Used to improve and extend Django test coverage for key behaviors.
- Workflow impact: AI increased development speed, but final decisions were validated through tests, logs, and manual verification.
