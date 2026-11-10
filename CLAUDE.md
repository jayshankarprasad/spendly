# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Spendly" — a Flask expense tracker built as a step-by-step teaching project (CampusX). Only the landing/auth/legal page shells exist so far; most functionality is deliberately left as numbered "Step N" placeholders for students to implement.

## Commands

Windows, project venv at `venv/` (use its interpreter explicitly, not `python3`, which resolves to Windows Store Python):

```
.\venv\Scripts\python.exe app.py                      # run dev server (debug mode, http://localhost:5001)
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest                   # all tests
.\venv\Scripts\python.exe -m pytest path/to/test.py::test_name   # single test
```

pytest and pytest-flask are in `requirements.txt`, but no tests exist yet and no linter or build step is configured.

## Architecture

- `app.py` — single Flask app; all routes live here. The pages `landing`, `register`, `login`, `terms`, `privacy` just call `render_template`. The remaining routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<int:id>/edit`, `/expenses/<int:id>/delete`) return placeholder strings labelled with the step that will implement them (Steps 3, 4, 7, 8, 9). Step numbering has gaps (1, 3, 4, 7, 8, 9 appear) — don't guess the missing ones.
  - Keep endpoint names when implementing. Templates currently only link to `landing`, `login`, `register`, `terms`, `privacy` and `static` via `url_for`; wire the others in as they're built.
  - `/expenses/<id>/delete` is currently GET; make it POST-only in Step 9.
  - `login`/`register` routes are GET-only and the forms are not yet connected to any handler.
- `database/db.py` — only a comment stub for Step 1. It should provide `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`) and `seed_db()` (sample dev data). `database/__init__.py` is empty.
- `templates/` — Jinja templates extending `base.html` (navbar, footer; blocks `title`, `head`, `content`).
- `static/css/style.css` — the single stylesheet; `static/js/main.js` is essentially empty.
- `README.md` is not real documentation — just leftover prompts plus the run command above.
