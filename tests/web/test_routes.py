from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from icep.web.app import create_app

pytestmark = pytest.mark.web


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "path",
    ["/", "/controls", "/soa", "/risks", "/nis2", "/evidence", "/training", "/initiatives"],
)
def test_pages_render(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert "PaketPort Systems GmbH" in response.text


def test_control_detail(client: TestClient) -> None:
    response = client.get("/controls/A.8.16")
    assert response.status_code == 200
    assert "Monitoring activities" in response.text


def test_control_detail_404(client: TestClient) -> None:
    assert client.get("/controls/A.9.99").status_code == 404


def test_risk_detail(client: TestClient) -> None:
    response = client.get("/risks/R-001")
    assert response.status_code == 200
    assert "R-001" in response.text


def test_evidence_detail(client: TestClient) -> None:
    response = client.get("/evidence/EV-001")
    assert response.status_code == 200
    assert "EV-001" in response.text


def test_evidence_detail_404(client: TestClient) -> None:
    assert client.get("/evidence/EV-999").status_code == 404


def test_evidence_detail_renders_artifact_blockquote(client: TestClient) -> None:
    # the collector artifact starts with a "> summary" line; it must render as a blockquote,
    # not a literal ">" (regression guard for the mini Markdown renderer)
    text = client.get("/evidence/EV-001").text
    assert "<blockquote>" in text


def test_overview_has_charts(client: TestClient) -> None:
    text = client.get("/").text
    assert "<svg" in text  # inline SVG charts rendered server-side
    assert "NIS2 readiness" in text
