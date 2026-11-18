# Results

Measured against `targets/ground_truth.md`. Counts, not percentages, until there are about 15 labeled cases. One section per release; never edit an old section.

## Baselines (2026-11-17, we45 commit b6a4f97, default rules)

Bandit 1.6.2 and Semgrep (`--config auto`) run on `app/app.py`. Raw outputs in `targets/baselines/`. Counted by chain, not by finding.

| Chain | Bandit | Semgrep |
|---|---|---|
| GT-1 SQL injection (`/search`) | missed | found (lines 261, 265) |
| GT-2 unsafe `yaml.load` (`/yaml_hammer`) | found (line 329) | found (line 329) |
| GT-3 template injection (404 handler) | missed | found (lines 103, 114) |
| GT-2b `secure_filename` path (must not be flagged) | not flagged | not flagged |
| **Ground-truth chains found** | **1 of 3** | **3 of 3** |

Notes:
- Both tools also flagged things outside my ground truth: MD5 password hashing (line 141, both), `random` for security (Bandit, lines 295 and 319), and Semgrep findings on JavaScript in `app/static/`.
- Semgrep flagged lines 271 and 281, which point at a fourth chain (line 280) not yet in the ground truth.
- Small sample: one app, three chains, default rules. This does not show one tool is better in general.

<!-- Template, copy per version:

## v0.1 (<date>, ground truth commit <hash>)

| Target | Class | Found / known | False positives (safe corpus) | Bandit | Semgrep |
|---|---|---|---|---|---|

Triage notes: why each miss or false positive happened.
-->
