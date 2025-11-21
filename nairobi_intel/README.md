# Nairobi Intelligence Brief Collector

This package sketches an asynchronous data collection pipeline that aligns with the "Nairobi Intelligence Brief" format. It aggregates RSS feeds, social endpoints, and HTML bulletins into a structured brief that mirrors the sections in the master prompt.

## Components
- `models.py` defines `IntelItem`, `Brief`, and typed categories/reliability levels.
- `config.py` lists starting sources (RSS, social APIs, and bulletins) and exposes `default_app_config`.
- `sources.py` contains lightweight clients for RSS, Twitter/X recent search, YouTube search, and simple HTML scraping plus a stub for offline testing.
- `collector.py` orchestrates parallel fetching, deduplication, and report rendering.
- `app.py` offers a CLI to produce the brief with optional category filtering and stub data.

## Usage
Install the requirements and run the CLI. Network calls require valid API tokens where applicable.

```bash
pip install -r nairobi_intel/requirements.txt
# Offline generation using stubbed signals
python -m nairobi_intel.app --stub --offline
# Category-filtered brief with live fetches (requires network/API access)
python -m nairobi_intel.app --category "Social Media" --output brief.txt
```

Use the `--stub` flag to inject synthetic items and `--offline` to disable network calls entirely. Add real API keys via environment-driven headers or the `auth_token` fields in `config.py` before deploying.
