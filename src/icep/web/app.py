"""The FastAPI application factory.

``create_app`` loads and validates the whole register **at startup** and precomputes the metrics --
so an invalid register fails fast (the app refuses to boot) and every request is a fast in-memory
read. Presentation helpers are registered as Jinja globals; routes live in :mod:`icep.web.routes`.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from icep import __version__
from icep.clock import Clock, default_clock
from icep.config import Settings, get_settings
from icep.metrics import compute_metrics
from icep.repository import IcepRepository
from icep.seed import read_manifest
from icep.web import filters
from icep.web.routes import register_routes

__all__ = ["create_app", "NAV"]

_HERE = Path(__file__).resolve().parent
TEMPLATES_DIR = _HERE / "templates"
STATIC_DIR = _HERE / "static"

NAV: list[tuple[str, str]] = [
    ("/", "Overview"),
    ("/controls", "Controls"),
    ("/soa", "Statement of Applicability"),
    ("/risks", "Risks"),
    ("/nis2", "NIS2"),
    ("/evidence", "Evidence"),
    ("/training", "Awareness"),
    ("/initiatives", "Initiative"),
]


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    """Build the dashboard app; raises if the register is invalid (validation-at-boot)."""
    settings = settings or get_settings()
    clock = clock or default_clock()
    today = clock.today()

    repo = IcepRepository.load(settings)  # raises LoaderError on invalid data
    metrics = compute_metrics(repo, today, settings.warn_days)
    hashes = read_manifest(settings)

    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    templates.env.globals.update(
        band_color=filters.band_color,
        status_color=filters.status_color,
        audit_color=filters.audit_color,
        review_color=filters.review_color,
        label=filters.label,
        review_state_of=filters.review_state_of,
        effective_audit_of=filters.effective_audit_of,
        org=repo.organization,
        version=__version__,
        today=today,
        warn_days=settings.warn_days,
        nav=NAV,
    )
    templates.env.filters["dateiso"] = lambda value: value.isoformat() if value else "—"
    templates.env.filters["md"] = filters.md_to_html

    app = FastAPI(
        title="ISMS Control & Evidence Platform",
        version=__version__,
        docs_url=None,
        redoc_url=None,
    )
    app.state.repo = repo
    app.state.metrics = metrics
    app.state.today = today
    app.state.hashes = hashes
    app.state.settings = settings
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    register_routes(app)
    return app
