#!/usr/bin/env python3
"""Check normalized evidence and preserve separate comparable groups; no network."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlparse

LIMITS = {"coding": 8, "reasoning": 48, "tooling": 48}


def date(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timezone missing")
    return parsed


def fresh(value, now, hours):
    try:
        age = (now - date(value)).total_seconds() / 3600
        return 0 <= age <= hours
    except (ValueError, TypeError, AttributeError):
        return False


def https(value):
    try:
        parts = urlparse(value)
        return parts.scheme == "https" and bool(parts.hostname)
    except (ValueError, TypeError):
        return False


def check(document, task, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if task not in LIMITS:
        return {"task": task, "groups": [], "excluded": [], "status": "unsupported_task_no_ASL_winner"}
    if document.get("format_version") != 1 or not isinstance(document.get("rows"), list):
        raise ValueError("Expected format_version 1 and rows array")
    groups, excluded = {}, []
    for row in document["rows"]:
        reasons = []
        if not isinstance(row, dict):
            excluded.append({"model_id": None, "reasons": ["malformed_row"]})
            continue
        model = row.get("gmi_model_id")
        if row.get("task") != task:
            continue
        if not isinstance(model, str) or not model.strip():
            reasons.append("missing_exact_GMI_id")
        if row.get("gmi_catalog_id") != model:
            reasons.append("id_not_exact_catalog_match")
        if row.get("availability") not in ("account_catalog", "official_mcp"):
            reasons.append("account_availability_unverified")
        if not https(row.get("gmi_source_url")):
            reasons.append("missing_GMI_source")
        if not fresh(row.get("gmi_checked_at"), now, 24):
            reasons.append("GMI_catalog_stale_or_time_unknown")
        if row.get("identity_verified") is not True or not https(row.get("mapping_source_url")):
            reasons.append("version_identity_unverified")
        if not row.get("benchmark_model_id") or not row.get("benchmark_deployment"):
            reasons.append("benchmark_identity_or_deployment_missing")
        if row.get("source_id") != "aistupidlevel.info" or not https(row.get("source_url")):
            reasons.append("unsupported_source_use_separate_assessment")
        if not fresh(row.get("measured_at"), now, LIMITS[task]):
            reasons.append("benchmark_stale_or_time_unknown")
        if not fresh(row.get("fetched_at"), now, 24):
            reasons.append("fetch_stale_or_time_unknown")
        for key in ("suite_version", "metric", "coverage", "language"):
            if not isinstance(row.get(key), str) or row[key].strip().lower() in ("", "unknown", "n/a"):
                reasons.append("missing_" + key)
        if row.get("coverage_complete") is not True:
            reasons.append("partial_or_unknown_task_coverage")
        if row.get("metric") != task:
            reasons.append("metric_is_not_requested_axis")
        score, rank = row.get("score"), row.get("source_rank")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            reasons.append("missing_finite_score")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            reasons.append("missing_source_tie_rank")
        if reasons:
            excluded.append({"model_id": model, "reasons": reasons})
            continue
        group_key = (row["source_id"], row["suite_version"], row["metric"], row["coverage"], row["language"])
        groups.setdefault(group_key, []).append(row)
    result = []
    for key, rows in groups.items():
        rows.sort(key=lambda r: (r["source_rank"], r["gmi_model_id"]))
        top_rank = rows[0]["source_rank"]
        result.append({"comparison": dict(zip(("source", "suite_version", "metric", "coverage", "language"), key)),
                       "top_tie_group": [r["gmi_model_id"] for r in rows if r["source_rank"] == top_rank],
                       "candidates": rows})
    return {"task": task, "checked_at": now.isoformat(), "status": "evidence_groups_not_universal_recommendation" if result else "no_verified_current_intersection",
            "groups": result, "excluded": excluded,
            "limits": ["Evidence truth and mapping citations require human/assistant review", "Do not merge groups or break source ties", "Cost and latency require independent GMI verification", "Benchmark deployment can differ from GMI"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--task", required=True)
    parser.add_argument("--now", help="ISO timestamp for reproducible tests only")
    args = parser.parse_args()
    try:
        document = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = check(document, args.task, date(args.now) if args.now else None)
    except (ValueError, OSError, TypeError, AttributeError):
        print("Evidence validation failed: check JSON schema and timezone-aware timestamps", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
