"""Synthetic fixtures only. No actual model rankings, credentials, or API requests."""
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill"


def module(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


checker = module("check_evidence")
collector = module("collect_evidence")
NOW = dt.datetime(2026, 10, 6, 4, tzinfo=dt.timezone.utc)


def row(model="synthetic/model-a", **changes):
    value = {"task": "coding", "gmi_model_id": model, "gmi_catalog_id": model,
             "availability": "account_catalog", "gmi_source_url": "https://example.test/gmi",
             "gmi_checked_at": "2026-10-06T03:00:00Z", "identity_verified": True,
             "mapping_source_url": "https://example.test/identity", "benchmark_model_id": "synthetic-a-v1",
             "benchmark_deployment": "synthetic test host", "source_id": "aistupidlevel.info",
             "source_url": "https://example.test/fixture-only", "measured_at": "2026-10-06T00:00:00Z",
             "fetched_at": "2026-10-06T03:00:00Z", "suite_version": "synthetic-suite-v1",
             "metric": "coding", "coverage": "7/7", "coverage_complete": True, "language": "English",
             "score": 80, "source_rank": 1}
    value.update(changes)
    return value


def check(*rows, task="coding"):
    return checker.check({"format_version": 1, "rows": list(rows)}, task, NOW)


class EvidenceTests(unittest.TestCase):
    def test_exact_intersection(self):
        out = check(row(), row("synthetic/model-b", gmi_catalog_id="synthetic/model-b-v2"))
        self.assertEqual(out["groups"][0]["top_tie_group"], ["synthetic/model-a"])
        self.assertIn("id_not_exact_catalog_match", out["excluded"][0]["reasons"])

    def test_fresh_fetch_does_not_fix_stale_run(self):
        out = check(row(measured_at="2026-10-05T15:00:00Z"))
        self.assertFalse(out["groups"])
        self.assertIn("benchmark_stale_or_time_unknown", out["excluded"][0]["reasons"])

    def test_reasoning_uses_48_hour_limit(self):
        out = check(row(task="reasoning", metric="reasoning", measured_at="2026-10-05T00:00:00Z"), task="reasoning")
        self.assertTrue(out["groups"])

    def test_future_and_unknown_time_rejected(self):
        for value in ("2026-10-07T00:00:00Z", None, "2026-10-06T03:00:00"):
            self.assertFalse(check(row(measured_at=value))["groups"])

    def test_different_versions_stay_separate(self):
        out = check(row(), row("synthetic/model-b", suite_version="synthetic-suite-v2"))
        self.assertEqual(len(out["groups"]), 2)

    def test_ties_preserved_despite_score(self):
        out = check(row(score=83), row("synthetic/model-b", score=81))
        self.assertEqual(len(out["groups"][0]["top_tie_group"]), 2)

    def test_partial_coverage_excluded(self):
        self.assertFalse(check(row(coverage="5/7", coverage_complete=False))["groups"])

    def test_combined_cannot_be_axis_score(self):
        self.assertFalse(check(row(metric="combined"))["groups"])

    def test_docs_only_is_conditional(self):
        self.assertFalse(check(row(availability="official_docs"))["groups"])

    def test_unsupported_task_no_winner(self):
        self.assertEqual(check(row(), task="Chinese writing")["status"], "unsupported_task_no_ASL_winner")

    def test_nan_rejected(self):
        self.assertFalse(check(row(score=float("nan")))["groups"])

    def test_identity_requires_citation(self):
        self.assertFalse(check(row(mapping_source_url=None))["groups"])


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.env = {"GMI_API_KEY": "synthetic-gmi-not-a-real-key", "ASL_API_KEY": "synthetic-asl-not-a-real-key"}
        self.calls = []

    def transport(self, url, key):
        self.calls.append(url)
        if url == collector.GMI_URL:
            return {"data": [{"id": "synthetic/model-a"}]}
        axis = url.split("sortBy=")[-1]
        return {"success": True, "version": "fixture-1", "generated_at": "2026-10-06T03:00:00Z",
                "license": "Synthetic fixture; no real leaderboard data", "sort_by": axis, "period": "latest",
                "data": [{"id": "fixture-a", "name": "Synthetic Model A", "currentScore": 80}]}

    def test_three_dimensions_and_catalog_only(self):
        data = collector.collect(self.env, transport=self.transport)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(set(data["asl_raw"]), {"coding", "reasoning", "tooling"})
        self.assertNotIn("recommendations", data)
        self.assertNotIn(self.env["GMI_API_KEY"], json.dumps(data))
        self.assertNotIn(self.env["ASL_API_KEY"], json.dumps(data))

    def test_schedule_requires_explicit_license_attestation(self):
        with self.assertRaises(collector.EvidenceError):
            collector.collect(self.env, True, self.transport)
        self.assertFalse(self.calls)

    def test_schedule_optin(self):
        self.env["ASL_AUTOMATION_AUTHORIZED"] = "true"
        self.assertEqual(collector.collect(self.env, True, self.transport)["format_version"], 1)

    def test_missing_key_makes_no_network_request(self):
        with self.assertRaises(collector.EvidenceError):
            collector.collect({}, transport=self.transport)
        self.assertFalse(self.calls)

    def test_wrong_dimension_fails(self):
        payload = self.transport(collector.ASL_BASE + "coding", "fixture")
        with self.assertRaises(collector.EvidenceError):
            collector.validate_asl(payload, "reasoning")

    def test_empty_catalog_fails(self):
        with self.assertRaises(collector.EvidenceError):
            collector.validate_gmi({"data": []})

    def test_incomplete_asl_schema_fails(self):
        with self.assertRaises(collector.EvidenceError):
            collector.validate_asl({"success": True, "data": []}, "coding")

    def test_private_atomic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            collector.write_private_atomic(path, {"fixture": True})
            self.assertTrue(json.loads(path.read_text())["fixture"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_failed_collection_keeps_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text('{"old": true}')
            def failed(url, key):
                raise collector.EvidenceError("HTTP 429; no automatic retry")
            with self.assertRaises(collector.EvidenceError):
                collector.write_private_atomic(path, collector.collect(self.env, transport=failed))
            self.assertEqual(json.loads(path.read_text()), {"old": True})


if __name__ == "__main__":
    unittest.main()
