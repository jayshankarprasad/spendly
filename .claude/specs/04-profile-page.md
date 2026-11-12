# Spec: Profile Page

## Overview
Step 4 turns the `/profile` placeholder into a real page for a signed-in user. It shows the user's account details (name, email, member-since date) and a quick summary of their expense activity (total spent, number of expenses recorded). This is a read-only view — no editing of profile fields or expenses happens here. It depends on session-based login being in place so the page knows which user is viewing it.

## Depends on
- Step 1 — Database setup (`users`, `expenses` tables, `get_db()`).
- Step 3 — Login/Logout (session cookie with `user_id`; not yet merged to `main`).

## Routes
- `GET /profile` — render the signed-in user's profile with account info and expense summary — logged-in only (redirect to `login` if no `session['user_id']`)

The existing `profile` endpoint name must be kept; it changes from a placeholder string to a real handler.

## Database changes
No database changes. Uses the existing `users` table (`id`, `name`, `email`, `created_at`) and `expenses` table (`user_id`, `amount`) to compute summary stats with an aggregate query.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; shows name, email, "member since" date (formatted from `created_at`), total amount spent, and number of expenses logged.
- **Modify:**
  - `templates/base.html` — nav must already distinguish signed-in state (from Step 3); add a "Profile" link next to "Sign out" when `session.get('user_id')` is set, pointing to `url_for('profile')`.

## Files to change
- `app.py` — implement the `profile` route: require login (redirect to `url_for('login')` if not authenticated), fetch the user row and an aggregate expense summary, render `profile.html`.
- `templates/base.html` — add the "Profile" nav link for signed-in users.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not relevant to this read-only page, but never display `password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `get_db()` from `database/db.py`; always close the connection (`try/finally`)
- Keep endpoint names unchanged; use `url_for` for all links
- Auth check: if `session.get('user_id')` is missing, redirect to `url_for('login')` — do not render the page for anonymous visitors
- Expense summary must be computed with a single aggregate SQL query (`SUM(amount)`, `COUNT(*)`) filtered by `user_id`, not by loading all rows into Python
- Handle the zero-expenses case (new user): show 0 / ₹0 rather than erroring or showing blank values
- Do not add profile editing, password changes, or expense editing — those are out of scope for this step
- Do not touch the other placeholder routes (`/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`)

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in (e.g. as the seeded `demo@spendly.com` user) shows the user's name and email
- [ ] The profile page shows the correct total spent and expense count, matching the sum/count of that user's rows in `expenses`
- [ ] A freshly registered user with zero expenses sees `0` / `₹0`, not an error
- [ ] The nav shows a "Profile" link when signed in, which links to `/profile` via `url_for`
- [ ] No `password_hash` value appears anywhere in the rendered page
- [ ] App starts with no errors and the landing, login, register, terms and privacy pages still work
