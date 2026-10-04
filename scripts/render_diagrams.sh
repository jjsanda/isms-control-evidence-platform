#!/usr/bin/env bash
# Render every Mermaid source under docs/diagrams/src to a committed PNG (+ SVG) via
# @mermaid-js/mermaid-cli. GitHub shows the PNGs with no client-side JavaScript, and they survive
# README embedding everywhere. Sources stay the single point of edit; re-run after changing one.
# Requires Node.js (uses npx; Chromium is downloaded by puppeteer on first run).
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="docs/diagrams/src"
OUT="docs/diagrams/rendered"
PCONF="docs/diagrams/puppeteer-config.json"
THEME="docs/diagrams/mermaid-config.json"
mkdir -p "$OUT"

shopt -s nullglob
sources=("$SRC"/*.mmd)
if [ ${#sources[@]} -eq 0 ]; then
  echo "no .mmd sources in $SRC" >&2
  exit 1
fi

for src in "${sources[@]}"; do
  name="$(basename "$src" .mmd)"
  echo "rendering $name"
  npx -y @mermaid-js/mermaid-cli@11 -p "$PCONF" -c "$THEME" -i "$src" -o "$OUT/$name.png" -b white -s 2 --quiet
  npx -y @mermaid-js/mermaid-cli@11 -p "$PCONF" -c "$THEME" -i "$src" -o "$OUT/$name.svg" -b transparent --quiet
done

echo "rendered $(ls "$OUT" | wc -l) files into $OUT"
