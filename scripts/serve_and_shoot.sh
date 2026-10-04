#!/usr/bin/env bash
# Seed the register, boot the dashboard, capture README screenshots, then tear down.
# Requires the 'media' extra (Playwright). Chromium is installed on first run.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${ICEP_PORT:-8021}"
export ICEP_NOW="${ICEP_NOW:-2026-07-07}"

echo "seeding evidence artifacts..."
uv run icep seed >/dev/null

echo "installing Playwright Chromium (no-op if already present)..."
uv run --extra media python -m playwright install chromium >/dev/null 2>&1 || true

echo "starting dashboard on port ${PORT}..."
uv run icep serve --host 127.0.0.1 --port "${PORT}" >/tmp/icep-serve.log 2>&1 &
SERVER_PID=$!
trap 'kill ${SERVER_PID} 2>/dev/null || true' EXIT

curl -sf --retry-connrefused --retry 40 --retry-max-time 30 \
  "http://127.0.0.1:${PORT}/healthz" >/dev/null

ICEP_BASE_URL="http://127.0.0.1:${PORT}" uv run --extra media python scripts/capture_screenshots.py

echo "screenshots written to docs/screenshots/"
