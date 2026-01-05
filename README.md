# UMCP Platform Samples

This repository is a platform-style catalog of runnable, audit-oriented examples built around a canon-grade UMCP Tier-0→Tier-1 kernel and weld receipts.

Repository goals:
- Provide a reference Python package (`umcp`) implementing Tier-0→Tier-1 computations and weld checks.
- Provide small, self-contained samples organized by topic (kernel, weld, overlays, integrations, scripts, sql).
- Ensure every sample is reproducible via CI: clone → install → test.

## Quickstart (Python)

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest -q
