# FaceBingo architecture

The application is split by responsibility so routes remain thin and UI changes
do not require API changes.

```text
main.py                 application assembly and middleware
api/routes/             HTTP boundary, grouped by user-facing capability
api/schemas/            request and response contracts
api/dependencies.py     shared FastAPI dependencies
core/services.py        validation and application use cases
core/repositories.py    Supabase persistence adapters
core/storage.py         object-storage operations
UI/templates/           shared Jinja layouts and partials
UI/static/              global tokens and reusable styling
UI/scripts/             page-specific browser behavior
```

`global.css` owns the design tokens and shared components. `pages.css` owns
page layouts. Each page loads only its own JavaScript entry point; scripts use
data attributes and event listeners rather than inline handlers.

## Development checks

Run `poetry run python -m compileall api core main.py` before committing.
Start locally with `poetry run uvicorn main:app --reload`.
