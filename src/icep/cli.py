"""The ``icep`` command-line interface.

Subcommands mirror the demo flow: ``validate`` (schema + cross-references), ``seed`` (generate
evidence + hashes + metrics), ``serve`` (the dashboard), ``export`` (the audit pack), and
``metrics`` (a KPI snapshot). Argparse + rich only -- no heavy CLI framework.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from rich.console import Console
from rich.table import Table

from icep import __version__
from icep.clock import default_clock
from icep.config import get_settings
from icep.domain import ReviewState
from icep.loader import LoaderError
from icep.metrics import compute_metrics
from icep.repository import IcepRepository

_out = Console()
_err = Console(stderr=True)

_SEVERITY_STYLE = {"error": "bold red", "warning": "yellow", "info": "dim"}


def _cmd_validate(_args: argparse.Namespace) -> int:
    settings = get_settings()
    try:
        repo = IcepRepository.load(settings)
    except LoaderError as exc:
        _err.print(f"[bold red]Schema validation failed[/bold red]\n{exc}")
        return 1

    issues = repo.check_integrity()
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]

    for issue in issues:
        style = _SEVERITY_STYLE[issue.severity]
        _out.print(
            f"[{style}]{issue.severity.upper():7}[/{style}] [{issue.category}] {issue.message}"
        )

    _out.print(
        f"\nRegister loaded: {len(repo.controls)} controls, {len(repo.risks)} risks, "
        f"{len(repo.evidence)} evidence, {len(repo.policies)} policies, "
        f"{len(repo.catalog)} catalog entries."
    )
    _out.print(
        f"Integrity: [bold red]{len(errors)} error(s)[/bold red], "
        f"[yellow]{len(warnings)} warning(s)[/yellow], [dim]{len(infos)} info[/dim]."
    )
    return 1 if errors else 0


def _cmd_seed(_args: argparse.Namespace) -> int:
    from icep.seed import SeedError, seed

    try:
        result = seed()
    except (LoaderError, SeedError) as exc:
        _err.print(f"[bold red]Seeding failed[/bold red]\n{exc}")
        return 1
    _out.print(
        f"[green]Seeded[/green] {len(result.artifacts)} evidence artifact(s) "
        f"({result.collector_runs} from collectors)."
    )
    _out.print(f"  manifest -> {result.manifest_path}")
    _out.print(f"  metrics  -> {result.metrics_path}")
    _out.print(f"  index    -> {result.index_path}")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:  # pragma: no cover - launches a live server
    import uvicorn

    from icep.web.app import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="info")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    from icep.export import ExportError, build_audit_pack, build_readme_pdf

    try:
        if args.readme_pdf is not None:
            path = build_readme_pdf("README.md", args.readme_pdf)
            _out.print(f"[green]Wrote[/green] {path}")
            return 0
        result = build_audit_pack(args.out, with_pdf=not args.no_pdf)
    except (LoaderError, ExportError) as exc:
        _err.print(f"[bold red]Export failed[/bold red]\n{exc}")
        return 1
    _out.print(
        f"[green]Built audit pack[/green] with {result.file_count} file(s) -> {result.out_dir}"
    )
    _out.print(f"  markdown -> {result.markdown_dir}")
    if result.pdf_path is not None:
        _out.print(f"  pdf      -> {result.pdf_path}")
    else:
        _out.print("  pdf      -> [yellow]skipped[/yellow] (install the 'pdf' extra to include it)")
    _out.print(f"  manifest -> {result.manifest_path}")
    return 0


def _cmd_metrics(_args: argparse.Namespace) -> int:
    settings = get_settings()
    try:
        repo = IcepRepository.load(settings)
    except LoaderError as exc:
        _err.print(f"[bold red]{exc}[/bold red]")
        return 1
    metrics = compute_metrics(repo, default_clock().today(), settings.warn_days)

    table = Table(
        title=f"ISMS KPIs — {repo.organization.name} ({metrics.generated_on.isoformat()})"
    )
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    rows = [
        ("Annex A controls documented", f"{metrics.documented_total} / {metrics.catalog_total}"),
        ("Applicable (SoA)", str(metrics.soa_applicable)),
        (
            "Implemented / operating",
            f"{metrics.implemented_controls} ({metrics.implementation_pct}%)",
        ),
        ("NIS2 readiness (Art. 21(2))", f"{metrics.nis2_overall_pct}%"),
        (
            "Risks (high/critical unaccepted)",
            f"{metrics.risk_total} ({metrics.risks_high_or_critical_open})",
        ),
        ("Risks accepted", str(metrics.risks_accepted)),
        ("Improvement actions open (overdue)", f"{metrics.action_open} ({metrics.action_overdue})"),
        ("Controls overdue for review", str(metrics.review_counts.get(ReviewState.OVERDUE, 0))),
        (
            "Evidence expired / expiring",
            f"{metrics.evidence_expired} / {metrics.evidence_expiring}",
        ),
        (
            "Training pass rate",
            f"{metrics.training_pass_pct}% ({metrics.training_passed}/{metrics.training_completions})",
        ),
    ]
    for label, value in rows:
        table.add_row(label, value)
    _out.print(table)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="icep", description="ISMS control & evidence platform")
    parser.add_argument("--version", action="version", version=f"icep {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "validate", help="validate the register schema and cross-references"
    ).set_defaults(func=_cmd_validate)
    sub.add_parser("seed", help="generate evidence artifacts, hashes and metrics").set_defaults(
        func=_cmd_seed
    )

    serve = sub.add_parser("serve", help="serve the ISMS dashboard")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(func=_cmd_serve)

    export = sub.add_parser("export", help="build the audit pack (Markdown + PDF + manifest)")
    export.add_argument("--out", default="dist/audit-pack", help="output directory")
    export.add_argument("--no-pdf", action="store_true", help="skip the PDF (Markdown bundle only)")
    export.add_argument(
        "--readme-pdf", default=None, help="instead, render README.md to this PDF path"
    )
    export.set_defaults(func=_cmd_export)

    sub.add_parser("metrics", help="print a KPI snapshot").set_defaults(func=_cmd_metrics)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
