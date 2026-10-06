# Sources and evidence boundaries

Verified documentation entry points: 2026-10-06 UTC. Recheck terms and source structure before a new integration. Links are discovery anchors, not a saved current leaderboard.

## AI Stupid Level (ASL)

- Public boards: https://aistupidlevel.info/
- Reading rules and limitations: https://aistupidlevel.info/faq
- API contract and access terms: https://aistupidlevel.info/api-docs
- Methodology: https://aistupidlevel.info/asl-public-benchmark-methodology-2026.pdf

Select coding, reasoning, or tooling explicitly. Use the source's freshness limits; documented on the verification date: Coding 8 hours, Reasoning/Tool use 48 hours, based on measured time. Preserve benchmark versions, task coverage and statistical ties. The documented test scope is English; coding currently covers Python. Do not extrapolate this directly to Chinese writing or other modalities. Missing suites can change combined weights; combined is not a stable substitute for a missing axis.

API: `GET https://aistupidlevel.info/api/v1/models?period=latest&sortBy=coding` (also `reasoning`, `tooling`), with a Bearer token. The documented envelope has `success`, `version`, `generated_at`, `license`, and `data`; `version` is API schema version, not necessarily benchmark suite version. Actual authenticated payload has not been live-tested in this package. Preserve raw data and inspect the live schema instead of guessing how scores map to axes. A requested sort alone does not prove that `currentScore` is an axis-specific score.

Free API access is evaluation-only; automatic refresh needs a qualifying paid plan. Attribution is required. Do not mirror/re-sell full rankings; redistribution or commercial data products can need a separate agreement. Ordinary cited research summaries are distinct from building a public data feed. Never circumvent API requirements by scheduled scraping.

## GMI Cloud

- Official index for discovery: https://docs.gmicloud.ai/llms.txt
- LLM API: https://docs.gmicloud.ai/inference-engine/api-reference/llm-api-reference
- Pricing: https://docs.gmicloud.ai/inference-engine/billing/price
- Official MCP: https://docs.gmicloud.ai/mcp/gmi-mcp-server
- MCP endpoint, if already connected: https://mcp.gmicloud.ai/mcp

Preferred verified catalog: existing MCP `search_models` / `get_model` read tools, or `GET https://api.gmi-serving.com/v1/models` with an existing GMI Bearer credential. Read tools do not authorize generation. Search the docs index for per-model quickstarts to obtain exact API IDs when no authenticated route exists. Label each catalog row `account_catalog`, `official_mcp`, or `official_docs`. Model family marketing is insufficient.

Current pricing is in GMI Console → Inference → Model Hub, with possible region/service modifiers. Use direct official live evidence, not old blog prices. Model listing, request-schema support, account entitlement and successfully served inference are different claims. No inference call is included in this package.

## Other benchmarks

Use task-matched original sources when ASL does not cover the work, retaining their metric, version, setup and license separately. Artificial Analysis is a possible research source: https://artificialanalysis.ai/ . Its API terms (https://artificialanalysiscdn.com/legal/ProDataPlatformTerms.pdf) restrict external model/provider-selection products without prior written permission. Do not silently add it as an automated public fallback. Never mix benchmark scales into one numeric rank.
