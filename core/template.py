"""
Jinja2 template engine — single shared instance.
Template directory is set to ./UI/ so all HTML files live directly there.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader

_TEMPLATES_DIR = Path(__file__).parent.parent / "UI"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
# Legacy templates remain in ``UI/`` while shared layouts and partials live in
# ``UI/templates/``. Keeping both loaders enables incremental page migration.
templates.env.loader = ChoiceLoader([
    FileSystemLoader(str(_TEMPLATES_DIR / "templates")),
    FileSystemLoader(str(_TEMPLATES_DIR)),
])
