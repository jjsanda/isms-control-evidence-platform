"""Dashboard routes. Handlers are thin reads over the in-memory repository in ``app.state``.

Charts are rendered to inline SVG here and passed to the templates as strings, so the templates stay
free of presentation maths and the pages contain no client-side rendering.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from icep.domain import Nis2Area
from icep.domain.common import control_sort_key
from icep.domain.nis2 import NIS2_ARTICLE, NIS2_TITLE
from icep.metrics import Metrics
from icep.repository import IcepRepository
from icep.web import charts
from icep.web.filters import STATUS_COLOR

__all__ = ["register_routes"]


def _render(request: Request, name: str, context: dict[str, object]) -> Response:
    response: Response = request.app.state.templates.TemplateResponse(request, name, context)
    return response


def _status_donut(metrics: Metrics) -> str:
    segments = [
        charts.Segment(label=status.value, value=metrics.status_counts.get(status, 0), color=color)
        for status, color in STATUS_COLOR.items()
        if metrics.status_counts.get(status, 0) > 0
    ]
    return charts.donut(segments, center_label="controls")


def _nis2_bars(repo: IcepRepository, metrics: Metrics) -> str:
    rows: list[tuple[str, float, str]] = []
    for area in Nis2Area:
        if area not in repo.nis2_by_area:
            continue
        pct = metrics.nis2_area_readiness.get(area, 0.0)
        color = "#059669" if pct >= 80 else "#f59e0b" if pct >= 50 else "#dc2626"
        rows.append((NIS2_ARTICLE[area], pct, color))
    return charts.hbars(rows)


def _residual_counts(repo: IcepRepository) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    for risk in repo.risks:
        key = (risk.residual_likelihood, risk.residual_impact)
        counts[key] = counts.get(key, 0) + 1
    return counts


def register_routes(app: FastAPI) -> None:
    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def overview(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        metrics: Metrics = st.metrics
        return _render(
            request,
            "overview.html",
            {
                "metrics": metrics,
                "status_donut": _status_donut(metrics),
                "nis2_bars": _nis2_bars(repo, metrics),
                "heatmap": charts.risk_heatmap(_residual_counts(repo)),
                "overdue": metrics.overdue_controls,
                "due_soon": metrics.due_soon_controls,
                "top_risks": metrics.top_residual_risks,
            },
        )

    @app.get("/controls")
    def controls(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        ordered = sorted(repo.controls, key=lambda c: control_sort_key(c.id))
        return _render(request, "controls.html", {"controls": ordered, "metrics": st.metrics})

    @app.get("/controls/{control_id}")
    def control_detail(request: Request, control_id: str) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        control = repo.control(control_id)
        if control is None:
            raise HTTPException(status_code=404, detail=f"control {control_id} not found")
        return _render(
            request,
            "control_detail.html",
            {
                "control": control,
                "evidence": repo.evidence_for_control(control_id),
                "risks": repo.risks_for_control(control_id),
                "policies": repo.policies_for_control(control_id),
                "actions": repo.actions_for_control(control_id),
                "soa": repo.soa_by_id.get(control_id),
                "hashes": st.hashes,
            },
        )

    @app.get("/soa")
    def soa(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        documented = repo.documented_control_ids
        entries = sorted(repo.soa, key=lambda e: control_sort_key(e.control_id))
        rows = [
            {
                "entry": e,
                "control": repo.catalog_by_id.get(e.control_id),
                "documented": e.control_id in documented,
            }
            for e in entries
        ]
        return _render(request, "soa.html", {"rows": rows, "metrics": st.metrics})

    @app.get("/risks")
    def risks(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        ordered = sorted(repo.risks, key=lambda r: (-r.residual_score, r.id))
        return _render(
            request,
            "risks.html",
            {
                "risks": ordered,
                "heatmap": charts.risk_heatmap(_residual_counts(repo)),
                "metrics": st.metrics,
            },
        )

    @app.get("/risks/{risk_id}")
    def risk_detail(request: Request, risk_id: str) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        risk = repo.risk(risk_id)
        if risk is None:
            raise HTTPException(status_code=404, detail=f"risk {risk_id} not found")
        controls = [repo.control(cid) for cid in risk.control_refs]
        return _render(
            request, "risk_detail.html", {"risk": risk, "controls": [c for c in controls if c]}
        )

    @app.get("/nis2")
    def nis2(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        metrics: Metrics = st.metrics
        measures = [
            {
                "area": area,
                "article": NIS2_ARTICLE[area],
                "title": NIS2_TITLE[area],
                "measure": repo.nis2_by_area.get(area),
                "readiness": metrics.nis2_area_readiness.get(area, 0.0),
            }
            for area in Nis2Area
            if area in repo.nis2_by_area
        ]
        return _render(
            request,
            "nis2.html",
            {"measures": measures, "reporting": repo.nis2_reporting, "metrics": metrics},
        )

    @app.get("/evidence")
    def evidence(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        ordered = sorted(repo.evidence, key=lambda e: e.id)
        return _render(
            request,
            "evidence.html",
            {"evidence": ordered, "hashes": st.hashes, "today": st.today, "metrics": st.metrics},
        )

    @app.get("/evidence/{evidence_id}")
    def evidence_detail(request: Request, evidence_id: str) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        item = repo.evidence_item(evidence_id)
        if item is None:
            raise HTTPException(status_code=404, detail=f"evidence {evidence_id} not found")
        controls = [repo.control(cid) for cid in item.control_refs]
        artifact_path = st.settings.evidence_dir.parent / item.artifact_path
        artifact_text = artifact_path.read_text(encoding="utf-8") if artifact_path.exists() else ""
        return _render(
            request,
            "evidence_detail.html",
            {
                "evidence": item,
                "controls": [c for c in controls if c],
                "sha256": st.hashes.get(item.artifact_path, ""),
                "artifact_text": artifact_text,
                "today": st.today,
            },
        )

    @app.get("/training")
    def training(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        return _render(
            request,
            "training.html",
            {
                "training": repo.trainings[0] if repo.trainings else None,
                "quiz": repo.quizzes[0] if repo.quizzes else None,
                "completions": repo.completions,
                "metrics": st.metrics,
            },
        )

    @app.get("/initiatives")
    def initiatives(request: Request) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        if not repo.initiatives:
            raise HTTPException(status_code=404, detail="no initiatives")
        return _render(request, "initiative.html", {"initiative": repo.initiatives[0]})

    @app.get("/initiatives/{initiative_id}")
    def initiative_detail(request: Request, initiative_id: str) -> Response:
        st = request.app.state
        repo: IcepRepository = st.repo
        match = next((i for i in repo.initiatives if i.id == initiative_id), None)
        if match is None:
            raise HTTPException(status_code=404, detail=f"initiative {initiative_id} not found")
        return _render(request, "initiative.html", {"initiative": match})
