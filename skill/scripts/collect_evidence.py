#!/usr/bin/env python3
"""Collect authorized, private raw evidence. Never infer axis score semantics."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.error
import urllib.request

GMI_URL = "https://api.gmi-serving.com/v1/models"
ASL_BASE = "https://aistupidlevel.info/api/v1/models?period=latest&sortBy="
AXES = ("coding", "reasoning", "tooling")
MAX_BYTES = 8_000_000


class EvidenceError(ValueError):
    pass


def timestamp(value):
    if not isinstance(value, str):
        raise EvidenceError("Missing timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError("Invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise EvidenceError("Timestamp must include timezone")
    return parsed


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise EvidenceError("Redirect refused; verify official endpoint")


def fetch_json(url, key):
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + key,
        "Accept": "application/json", "User-Agent": "gmi-model-advisor/1.0"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise EvidenceError(f"HTTP {exc.code}; no automatic retry") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise EvidenceError("Network request failed; no automatic retry") from None
    if len(raw) > MAX_BYTES:
        raise EvidenceError("Response too large")
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError):
        raise EvidenceError("Response is not valid JSON") from None


def validate_gmi(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list) or not payload["data"]:
        raise EvidenceError("Unrecognized or empty GMI catalog")
    ids = []
    for row in payload["data"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise EvidenceError("GMI catalog row lacks exact model id")
        ids.append(row["id"])
    if len(ids) != len(set(ids)):
        raise EvidenceError("Duplicate GMI model ids")
    return payload


def validate_asl(payload, axis):
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise EvidenceError("Unrecognized ASL envelope")
    if not isinstance(payload.get("version"), str) or not payload["version"]:
        raise EvidenceError("ASL API version missing")
    timestamp(payload.get("generated_at"))
    if not isinstance(payload.get("license"), str) or not payload["license"]:
        raise EvidenceError("ASL attribution/license metadata missing")
    if payload.get("sort_by") != axis or payload.get("period") != "latest":
        raise EvidenceError("ASL requested dimension/period not confirmed")
    rows = payload.get("data")
    if not isinstance(rows, list) or not rows:
        raise EvidenceError("ASL data missing or empty")
    for row in rows:
        if not isinstance(row, dict) or not row.get("id") or not isinstance(row.get("name"), str) or not row["name"]:
            raise EvidenceError("ASL row identity missing")
    # Do not treat currentScore as an axis score: actual score schema needs review.
    return payload


def collect(env, scheduled=False, transport=fetch_json):
    if scheduled and env.get("ASL_AUTOMATION_AUTHORIZED") != "true":
        raise EvidenceError("Scheduled ASL access requires a verified qualifying plan and explicit opt-in")
    for name in ("GMI_API_KEY", "ASL_API_KEY"):
        if not env.get(name):
            raise EvidenceError(f"Missing securely configured {name}")
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    gmi = validate_gmi(transport(GMI_URL, env["GMI_API_KEY"]))
    asl = {axis: validate_asl(transport(ASL_BASE + axis, env["ASL_API_KEY"]), axis) for axis in AXES}
    return {
        "format_version": 1, "collection_started_at": started,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "raw_evidence_requires_semantic_review",
        "attribution": "AI Stupid Level — https://aistupidlevel.info/",
        "gmi_source": GMI_URL, "gmi_catalog": gmi,
        "asl_sources": {a: ASL_BASE + a for a in AXES}, "asl_raw": asl,
        "limitations": ["Not a recommendation", "No paid inference run", "Benchmark measurement timestamps, suite versions, axis scores and exact identity mappings need review", "Do not republish raw rankings"]}


def write_private_atomic(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".snapshot-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scheduled", action="store_true")
    args = parser.parse_args()
    try:
        payload = collect(os.environ, args.scheduled)
        write_private_atomic(args.out, payload)
    except (EvidenceError, OSError) as exc:
        # Error text only comes from our controlled validation, never HTTP bodies or credentials.
        if isinstance(exc, EvidenceError):
            print(f"Collection failed: {exc}", file=sys.stderr)
        else:
            print("Collection failed: could not save private snapshot", file=sys.stderr)
        return 2
    print("Private raw snapshot saved. Axis semantics and exact model mappings still need review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
