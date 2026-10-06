# Normalized evidence format

The assistant prepares this optional local format from verified live sources; do not ask the user to manually build a JSON dump. It is a deliberate adapter boundary: authenticated ASL score fields have not been verified, so raw `currentScore` must never be automatically relabeled coding/reasoning/tooling.

Top level: `format_version: 1`, `rows: []`. Each row has:

- `task`: coding / reasoning / tooling
- `gmi_model_id`, `gmi_catalog_id`: identical exact API strings; no fuzzy matching
- `availability`: account_catalog / official_mcp / official_docs (docs-only excluded from verified intersection, still usable as a conditional candidate in prose)
- `gmi_source_url`, `gmi_checked_at`: catalog provenance and timezone-aware time
- `identity_verified`: true only after full-version mapping; `mapping_source_url`: supporting original source
- `benchmark_model_id`, `benchmark_deployment`: preserve full evaluated identity and hosting setup
- `source_id`: aistupidlevel.info; `source_url`: actual evidence page
- `measured_at`: relevant suite's real run time; `fetched_at`: retrieval time
- `suite_version`: benchmark suite version, not API envelope version
- `metric`: requested axis; `score`: finite numeric native score
- `source_rank`: positive integer from source, same integer for its statistical ties
- `coverage`: exact coverage descriptor; `coverage_complete`: true only for all applicable tasks
- `language`: evaluated language
- Optional native uncertainty intervals, GMI pricing, currency/unit and deployment latency evidence remain in the row. Missing values stay null/unknown; the checker does not fabricate or use them for ranking.

The checker enforces source freshness (coding 8 h, reasoning/tooling 48 h) and local operational limits of 24 h for catalog/fetch checks. These local limits are implementation defaults, not claims about GMI policy. It preserves source/version/metric/coverage/language groups and source tie ranks. Separate groups have no overall winner. It excludes partial-coverage rows from the main comparison; report them separately with that caveat when useful.

A passing check is not proof that a supplied URL says what its row asserts. Verify citations and capability requirements separately. Timestamp unknown, version unknown, no source rank, provider mismatch or docs-only availability must remain visible limitations rather than being silently repaired.
