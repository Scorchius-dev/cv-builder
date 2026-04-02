# AI Career Pro

AI Career Pro is a Django web app that helps users create CV profiles and generate tailored cover letters from job descriptions.

## Live App

- Live URL: https://ai-career-pro-237ce7da783b.herokuapp.com/
- Admin URL: admin access restricted to staff/superusers

## Features

- User signup, login, and logout
- CV create, edit, and delete
- AI-powered tailored cover-letter generation
- Saved letters dashboard with search and pagination
- Premium upgrade flow with Stripe checkout and billing portal
- Premium PDF export for saved letters
- Responsive and accessible UI improvements

## UX Design Process

- Initial design intent: Provide a fast application workflow from CV profile to tailored letter.
- Accessibility considerations implemented: semantic HTML structure, skip-link usage, clear form labels, and readable feedback states.
- Responsive behavior implemented: Bootstrap grid/layout, mobile-stacking action controls, and adaptive navigation.
- Iterative improvements made: clearer call-to-action flow, structured output format for generated letters, and dedicated public homepage.

### Color Palette

- Primary brand blue: `#0d6efd`
	- Used for primary actions, navigation emphasis, and key call-to-action elements.
- Supporting blue shades: Bootstrap `primary` variants
	- Used across buttons, badges, and links for consistent interaction styling.
- Body text: `#1f2937`
	- Used for high readability on light backgrounds.
- Secondary text: `#6b7280`
	- Used for placeholders, helper text, and lower-emphasis copy.
- Surface/background base: `#f8f9fa` and `#ffffff`
	- Used for page background and card surfaces to maintain contrast and content separation.
- Success and warning accents: Bootstrap `success` and `warning` colors
	- Used for plan status, upgrade messaging, and positive/attention states.

### UX Artefacts

#### Wireframes (Low-Fidelity)

- [Homepage Wireframe](docs/ux/wireframes/homepage_wireframe.png)
- [Signup Page Wireframe](docs/ux/wireframes/signuppage_wireframe.png)
- [Login Page Wireframe](docs/ux/wireframes/loginpage_wireframe.png)
- [CV Form Wireframe](docs/ux/wireframes/cvform_wireframe.png)
- [Dashboard Wireframe](docs/ux/wireframes/dashboard_wireframe.png)
- [Upgrade Page Wireframe](docs/ux/wireframes/upgrade_wireframe.png)

#### Screenshots (Final Implementation)

- [Landing Page](docs/ux/screenshots/landingpage.png)
- [Login Page](docs/ux/screenshots/loginpage.png)
- [Signup Page](docs/ux/screenshots/signuppage.png)
- [Create CV Page](docs/ux/screenshots/createcvpage.png)
- [Generate Letter Page](docs/ux/screenshots/generateletterpage.png)
- [Dashboard Page](docs/ux/screenshots/dashboardpage.png)
- [Stripe Upgrade Page](docs/ux/screenshots/stripepage.png)
- [Subscription Page](docs/ux/screenshots/subscriptionpage.png)

## Design Change Log

1. Public landing page added at root URL.
	- Change: Introduced a public homepage and moved the authenticated generator flow to `/app/`.
	- Reason: New visitors needed context about app purpose before login.
	- Impact: Better onboarding, clearer navigation, and improved first-time UX.

2. Generated letter output standardized.
	- Change: Added server-side normalization and structured business-letter formatting.
	- Reason: Raw AI output could include inconsistent greeting/sign-off patterns and spacing.
	- Impact: More professional and predictable letter output quality.

3. Mobile responsiveness improvements.
	- Change: Adjusted navigation/actions to stack and remain usable on smaller screens.
	- Reason: Dashboard and action controls felt cramped on mobile.
	- Impact: Improved readability and tap targets on phones/tablets.

## Tech Stack

- Django
- PostgreSQL on Heroku (SQLite fallback for local development)
- Bootstrap 5
- Stripe
- Google GenAI
- ReportLab
- Gunicorn + WhiteNoise

## Database Design and Data Handling

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

## CRUD and Business Logic

- CV CRUD: create, update, delete, and list operations with ownership checks.
- Cover letter CRUD: generate/save, view, and delete operations per authenticated user.
- Dashboard search and pagination for letter management.

## Forms and Validation

- `SignupForm` includes custom validation (e.g., duplicate email handling).
- `CVForm` validates required fields and trims whitespace.
- Templates render clear field-level and form-level error messages.

## User Notifications

- Near-real-time in-app notifications are implemented with Django messages for key events:
	- account creation
	- CV create/update/delete
	- letter create/delete
	- billing and premium state feedback
- Optional welcome email notification on signup when email is provided.

## Authentication, Authorization, and Access Control

- Registration, login, and logout are implemented with Django auth.
- Login state is reflected in navigation and page actions.
- Restricted routes are protected with `@login_required`.
- Access control is enforced with user-scoped object lookups to prevent cross-user access.

## Deployment Notes

- Procfile is configured for Gunicorn
- runtime.txt pins Python version for Heroku stability
- Static files served via WhiteNoise
- Database configured via DATABASE_URL

### Technical Stability Changes

1. Runtime stabilization.
	- Change: Pinned Heroku Python runtime to a stable version compatible with Django.
	- Reason: Admin route errors occurred with an incompatible runtime version.
	- Impact: Restored stable production behavior.

2. Static-file serving hardening.
	- Change: Enabled WhiteNoise middleware and manifest-based static asset storage.
	- Reason: Ensure reliable CSS/JS asset delivery in Heroku environment.
	- Impact: Consistent styling and static asset behavior after deploy.

Typical post-deploy steps:

1. `python manage.py migrate`
2. `python manage.py collectstatic --noinput`

## Deployment Procedure

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
- `SantTRIPE_PRICE_ID`

Optional:

- `STRIPE_CURRENCY`
- `STRIPE_PREMIUM_MONTHLY_PENCE`
- `STRIPE_PREMIUM_MONTHLY_DISPLAY`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`

## Security Notes

- Secrets are managed via environment variables and not hardcoded in source.
- `.env` is used for local development and should remain ignored in Git.
- Production deployment uses `DEBUG=False`.
- Allowed hosts and CSRF trusted origins are configured for deployed domain.
- Secure cookie and HTTPS-related settings are enabled in production mode.

## Version Control and Project Tracking

- Development was tracked with Git and GitHub commits.
- Agile planning/tracking was maintained using user stories and a GitHub Project board.
- User stories are documented in `USER_STORIES.md` and linked to delivered functionality.

## Testing

Run tests locally with:

`python manage.py test`

### Python Test Procedures

Automated tests cover:

- authentication and signup behavior
- CV CRUD operations
- privacy/authorization boundaries
- dashboard filtering
- key Stripe-related flow behaviors

### JavaScript Testing

- No dedicated JS test framework was added for this submission.
- JavaScript behavior (form submit states/copy actions/navigation UX) was validated manually during feature testing.

### Testing Documentation

- Test strategy: combination of automated Django tests and manual end-to-end verification on deployed app.
- Expected outcome: no failing tests and working deployed core flows.
- Actual outcome: test suite passes locally (`manage.py test`) and deployed workflows were validated.

## Agile Evidence

See project on github for user stories, priorities, and acceptance criteria.

## AI Usage Reflection

- AI-assisted code creation: Used for accelerating initial implementation of views/templates/forms and refactoring support.
- AI-assisted debugging: Used to diagnose deployment/runtime issues (e.g., runtime compatibility and environment/config mismatches).
- AI-assisted optimization: Used for iterative UX/accessibility/responsive and reliability improvements.
- AI-assisted test support: Used to improve and extend Django test coverage for key behaviors.
- Workflow impact: AI increased development speed, but final decisions were validated through tests, logs, and manual verification.
