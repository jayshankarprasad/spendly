# Spec: Login and Logout

## Overview
Step 3 turns the existing `/login` page shell and the placeholder `/logout` route into a working session-based authentication flow. A visitor submits their email and password; the app verifies the credentials against the `users` table and starts a server-side session (Flask's signed cookie session, via a new `app.secret_key`). Logging out clears that session. This is the first feature that establishes "who is logged in," and it is the prerequisite for Step 4 (profile) and every expense route that needs to scope data to a specific user.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `init_db()`).
- Step 2 — Registration (users must be able to create an account before they can log in).

## Routes
- `GET /login` — render the login form (already exists, unchanged) — public
- `POST /login` — validate credentials, start the session, redirect to `landing` on success or re-render the form with an error — public
- `GET /logout` — clear the session, redirect to `landing` — logged-in (replaces the current placeholder string)

The existing `login` endpoint name must be kept; it gains `methods=["GET", "POST"]`. The existing `logout` endpoint name must be kept.

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) already covers this feature.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change `action="/login"` to `action="{{ url_for('login') }}"`; re-populate the `email` field with the submitted value when an error is shown (never re-populate the password); keep the existing `{% if error %}` block.
  - `templates/base.html` — nav links become session-aware: when `session.get('user_id')` is set, show the user's name and a "Sign out" link (`{{ url_for('logout') }}`) instead of "Sign in" / "Get started".

## Files to change
- `app.py` — set `app.secret_key` (from `os.environ.get("SECRET_KEY", ...)` with a hardcoded dev fallback is acceptable); import `session`; make `login` accept GET and POST and implement the POST handler; implement `logout` to clear the session and redirect.
- `templates/login.html` — as described above.
- `templates/base.html` — as described above.

## Files to create
- None (optionally `tests/test_login.py` if tests are added).

## New dependencies
No new dependencies (Flask's `session` and werkzeug's `check_password_hash` are already available).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug — verify with `check_password_hash`, never compare plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py`; always close the connection (`try/finally`)
- Keep endpoint names unchanged; use `url_for` for redirects and links
- Validation (server-side, in this order), each failure re-renders `login.html` with an `error` message:
  1. `email` and `password` both present (email `.strip().lower()`; password not stripped)
  2. Look up the user by email; if no row, or `check_password_hash` fails, show one generic error — "Invalid email or password." Do not reveal whether the email exists.
- Error responses for validation failures return HTTP 401 (or 200 with the form; pick one and be consistent).
- On success, store the minimum needed to identify the user in the session (e.g. `session['user_id'] = user['id']`), then redirect to `url_for('landing')`. Do not store the password or password hash in the session.
- `GET /logout` clears the session (`session.clear()`) and redirects to `url_for('landing')`; visiting it while already logged out is a harmless no-op redirect, not an error.
- Do not implement route protection / `login_required` for `/profile` or `/expenses/*` in this step — that belongs to Step 4 and later. This step only establishes and clears the session.
- Do not touch the other placeholder routes (`/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`).

## Definition of done
- [ ] `GET /login` still renders the form with no errors
- [ ] Submitting the seeded demo account (`demo@spendly.com` / `demo123`) logs in and redirects to `/`
- [ ] After logging in, the navbar on any page shows the signed-in state (name / "Sign out") instead of "Sign in" / "Get started"
- [ ] Submitting a correct email with the wrong password shows "Invalid email or password." and does not log in
- [ ] Submitting an email that doesn't exist shows the same "Invalid email or password." message (no information leak)
- [ ] Empty email or password shows an error and does not log in
- [ ] On any error the email field keeps its submitted value and the password field is empty
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/`, after which the navbar reverts to the signed-out state
- [ ] Visiting `/logout` while already logged out redirects to `/` without raising an error
- [ ] The login form posts via `url_for('login')`; no hardcoded `/login` remains in the template
- [ ] App starts with no errors and the landing, register, terms and privacy pages still work
