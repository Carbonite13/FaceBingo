"""
Jinja2 template engine — single shared instance.
Template directory is set to ./UI/ so all HTML files live directly there.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates

_TEMPLATES_DIR = Path(__file__).parent.parent / "UI"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
