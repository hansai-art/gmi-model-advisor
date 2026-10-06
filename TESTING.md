# Verification report

Date: 2026-10-06 UTC.

## Executed checks

- Personal-skill validator: passed against the actual personal-skills checkout.
- Python unit tests: 27 passed (rerun directly for publication). Raw output: `test-results.txt`.
- CLI fixture check: `tests/fixtures/synthetic-evidence.json` → `tests/fixtures/synthetic-output.json` at fixed time `2026-10-06T04:00:00Z`.
- Scheduled collector without license attestation: exited with a clear prerequisite error and created no output file.

The synthetic CLI output preserves two tied current model candidates, excludes one stale measurement, and rejects one mismatched model version. Fixture model names, benchmark values and URLs are deliberately fictional and do not represent a real recommendation.

## Direct publication checks (2026-10-06 05:54 UTC)

The assistant handling the publication request directly executed these checks:

- All 27 offline unit/HTTP-boundary tests passed; Python compilation passed.
- The fixture CLI output exactly matched the committed expected JSON.
- Running the collector with both API keys absent returned exit code 2 and created no snapshot.
- The actual installed personal Skill passed the Skill validator; its instruction and Python source files match this export. Installation-specific UI assets are not required in the public package.
- Six added HTTP boundary checks cover GET-only requests/timeouts, HTTP error redaction, refused redirects, invalid JSON, response-size limits, and network-error redaction. These use mocked transport and do not claim authenticated connectivity.

### Public-source smoke use: Python debugging candidate

I followed the Skill against public sources rather than relying only on fixtures:

1. Read the [ASL homepage](https://aistupidlevel.info/), [methodology](https://aistupidlevel.info/methodology), and [DeepSeek V4 Flash model page](https://aistupidlevel.info/models/deepseek-v4-flash).
2. Read the [GMI index](https://docs.gmicloud.ai/llms.txt) and [model quickstart](https://docs.gmicloud.ai/model-quickstarts/text/deepseek-ai-deepseek-v4-flash).
3. Extracted exact documented API ID `deepseek-ai/DeepSeek-V4-Flash`. This is an official-docs candidate, not verified account availability or tested inference.
4. The retrieved ASL homepage and model detail were inconsistent, and the extracted model page did not provide a per-run timestamp or deployment revision. I therefore did not certify a current winner or transfer a combined score to coding. The source's joint-rank language was retained without inventing a unique winner.
5. The `.md` quickstart URL failed in the web reader; its ordinary documentation URL succeeded. No credentials were requested or transmitted.

Observed outcome: public-source discovery and exact-ID extraction worked. Full live model recommendation remains conditional on fresh per-axis evidence, version mapping and account catalog verification. This is a successful uncertainty-handling check, not an end-to-end authenticated integration pass.

## Independent behavioral checks

An independent assistant read the Skill in a fresh task without expected answers. Three text-only cases passed:

1. Asked for React and Traditional Chinese writing recommendations from ASL Combined. It kept task-specific evidence separate, noted ASL's Python/English scope and did not invent a direct writing/React winner.
2. Supplied Alpha-v2 coding score 96 measured on October 5 at 00:00 UTC, with an October 6 03:00 UTC evaluation and a GMI Alpha-v1 listing. It identified 27-hour-old coding evidence, refused to transfer the score to v1, and made no unsupported cheapest-model claim.
3. Asked whether installation means automatic daily recommendations and email. It distinguished installation, evidence collection, recommendation generation, scheduling and permission to message a recipient.

These checks used no paid inference, live authenticated APIs or external writes. The evaluation summary was supplied by the supervising task on 2026-10-06; it assesses instructions, not API connectivity.

## Unverified / deliberately out of scope

- No GMI or ASL credentials were provided, so the collector has not been authenticated against live APIs.
- Actual ASL per-axis score semantics and per-suite timestamp fields remain a required live integration review. The collector stores raw records rather than assuming them.
- The optional daily-evidence workflow remains disabled in a public repository. Offline CI does not use credentials or validate live API connectivity; exact commit results are available in the repository Actions history.
- No daily background job, delivered recommendation, email, public site, paid inference, or public leaderboard was enabled.
