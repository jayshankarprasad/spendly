# Spec: Registration

## Overview
Step 2 turns the existing `/register` page shell into a working sign-up flow. A visitor submits their full name, email and password; the app validates the input, stores a new row in the `users` table with a werkzeug-hashed password, and sends the visitor to the login page. This is the first feature that writes user data from the web UI, and it is the prerequisite for login/logout (Step 3) and everything behind authentication.

## Depends on
- Step 1 — Database setup (`users` table, `get_db()`, `init_db()`).

## Routes
- `GET /register` — render the registration form (already exists, unchanged) — public
- `POST /register` — validate form, create the user, redirect to `login` on success or re-render the form with an error — public

The existing `register` endpoint name must be kept; it gains `methods=["GET", "POST"]`.

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`) already covers this feature.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — change `action="/register"` to `action="{{ url_for('register') }}"`; re-populate `name` and `email` inputs with the submitted values when an error is shown (never re-populate the password); keep the existing `{% if error %}` block.

## Files to change
- `app.py` — import `request`, `redirect`, `url_for`, `generate_password_hash`, `sqlite3`; make `register` accept GET and POST and implement the POST handler.
- `templates/register.html` — as described above.

## Files to create
- None (optionally `tests/test_registration.py` if tests are added).

## New dependencies
No new dependencies (werkzeug ships with Flask).

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`); never store or log plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py`; always close the connection (`try/finally`)
- Keep endpoint names unchanged; use `url_for` for redirects and links
- Validation (server-side, in this order), each failure re-renders `register.html` with an `error` message:
  1. `name`, `email`, `password` all present after `.strip()` (password is not stripped)
  2. Email contains a basic `@`/domain shape; normalise to lowercase and strip whitespace before storing
  3. Password is at least 8 characters (matches the form placeholder)
  4. Email not already registered — check by catching `sqlite3.IntegrityError` on insert (the `UNIQUE` constraint), not only a pre-check, to avoid a race
- Error responses for validation failures return HTTP 400 (or 200 with the form; pick one and be consistent); duplicate email message must not leak anything beyond "An account with this email already exists."
- On success, redirect to `url_for('login')`. No session/auto-login in this step (that belongs to Step 3). Do not add flash messages or a `secret_key` in this step.
- Do not touch the other placeholder routes.

## Definition of done
- [ ] `GET /register` still renders the form with no errors
- [ ] Submitting valid name, email and an 8+ character password creates a row in `users` and redirects to `/login`
- [ ] The stored `password_hash` is a werkzeug hash (not the plaintext password), verifiable with `check_password_hash`
- [ ] The stored email is lowercased and trimmed (e.g. `  Test@Example.COM ` is saved as `test@example.com`)
- [ ] Registering the same email twice shows "An account with this email already exists." and creates no second row
- [ ] Password shorter than 8 characters shows an error and creates no row
- [ ] Empty or whitespace-only name/email shows an error and creates no row
- [ ] On any error the name and email fields keep their submitted values and the password field is empty
- [ ] The form posts via `url_for('register')`; no hardcoded `/register` remains in the template
- [ ] App starts with no errors and the landing, login, terms and privacy pages still work
