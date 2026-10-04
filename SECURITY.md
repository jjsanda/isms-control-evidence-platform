# Security policy

This is a **portfolio / demonstration project**. It models a fictional company
("PaketPort Systems GmbH") and contains **no real, confidential, or personal data** — every control,
risk, evidence record, credential-shaped string and audit finding is illustrative.

## Reporting

If you spot a security issue in the code (not the fictional content), please open a GitHub issue or
contact the author. There is no production deployment and no bug-bounty.

## Threat model & design choices

Even as a demo, the project is built to be safe by construction:

- **No secrets, no network at runtime.** The default stack runs fully offline with no API key. There
  are no credentials in the repository; the "access review" sample contains only fictional account
  names.
- **Read-only application.** The web app has no write path — it loads and validates the register at
  startup and serves it read-only. Data changes happen through reviewed pull requests to the YAML.
- **Strict input validation.** All structured data is parsed through Pydantic v2 with
  `extra="forbid"`; the app refuses to boot on invalid data.
- **Output safety.** Templates auto-escape; the small in-house Markdown renderer HTML-escapes input
  before applying any formatting.
- **Evidence integrity.** Generated evidence is anchored by a SHA-256 manifest so tampering is
  detectable.
- **Supply chain.** Dependencies are pinned in `uv.lock`; CI runs `pip-audit` and CodeQL.

See [`docs/adr/`](docs/adr/) for the rationale behind these choices.
