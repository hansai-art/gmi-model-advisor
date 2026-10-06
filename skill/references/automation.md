# Optional evidence collection

No background job is enabled by installing this Skill. Live web research at invocation works without API keys. The optional collector uses Python 3.10+ standard library and only GET requests to documented official endpoints; it does not run paid inference.

Run only when the user has already securely configured access:

```sh
python3 scripts/collect_evidence.py --out /private/path/snapshot.json
```

Required environment variables: `GMI_API_KEY`, `ASL_API_KEY`. Do not put credentials in chat, source files, command-line arguments, logs, or public artifacts. The script never creates credentials or configures persistent access.

For automated collection, additionally set `ASL_AUTOMATION_AUTHORIZED=true` only after verifying the user's ASL subscription permits scheduled access, then use `--scheduled`. This is an explicit local attestation, not a license-verification API. Recheck upstream terms before enabling. It does not grant redistribution rights.

The GitHub-ready export includes a daily workflow disabled until a user enables it in a private repository and configures secrets. Its result is a private raw evidence artifact, not a complete daily recommendation. Inspect actual API fields, establish exact GMI model mappings and apply the Skill to produce the recommendation. Both keys and current suite measurements are still required; ASL's separate axes may be stale even after a successful daily collection.

Collector validation confirms a recognizable envelope and model rows, not score meaning. Unexpected schema, authentication errors, HTTP 429, redirects, empty catalogs or incomplete responses fail closed; a failed run never overwrites the previous snapshot. No raw rankings are committed or sent to a public website. Mock tests establish error handling only; no live authenticated test has been performed.

For a true daily delivered recommendation, additionally configure and verify an authorized scheduler with an assistant that can read the private evidence, resolve IDs, judge task-specific evidence and message the approved destination. Keep it off until those steps are complete; never claim that evidence collection alone delivers recommendations.
