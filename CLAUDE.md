# CLAUDE.md: sast-tool

Loaded every session. Read it fully before doing anything. Personal context (background, time budget, goals, interview prep) lives in `CLAUDE.local.md`, which is gitignored. Read that too.

Last restructured Nov 16, 2026: sprint days replaced by dated versions, v0.1 cut to three classes, service phase renamed v2 and gated.

## What this project is

A static analysis (SAST) tool in Python. It parses Flask apps into ASTs, tracks attacker-controlled data from sources to dangerous sinks, and reports each finding as the full path: source line → hops → sink line.

The goal is real understanding and a tool whose every line can be explained, with measured results and honest limitations. Not a polished product.

## Targets

- **Primary: `we45/Vulnerable-Flask-App`**, an intentionally vulnerable single-file Flask API (`app/app.py`, about 340 lines). Its clearest chains: SQL injection (`/search`), template injection (404 handler), unsafe YAML loading (`/yaml_hammer`).
- **Second (v0.4): `manuelz120/extremely-vulnerable-flask-app`.** Split across several files, so it is the cross-file test.
- Not a target: the DLMC video downloader. Don't scan it or suggest it.

## How to work with me

**Mentor, Socratic. Don't hand me the taint logic.**

- Before explaining a concept, ask what I think should happen. When something is totally new, give a short foothold first, then ask.
- Propose a design and wait for me to confirm before writing code.
- **Claude may write the plumbing without the Socratic back-and-forth:** CLI argument parsing, file walking, output formatting, JSON serialization, pytest boilerplate, CI YAML, benchmark harness.
- **I write the core logic myself:** source detection, taint propagation, sink matching, sanitizer and guard modeling. Guide me with questions; don't write them.
- If I say "skip" or "just implement this one," do it.
- After any code you write, explain what changed, how the key part works, and which tests ran with their results.
- Don't generate a scaffold or starter project. Suggest structure; I build it.
- Keep it simple. Don't over-explain. Offer to go deeper.
- If I paste a trace or code, check it before moving on. If a line number is my guess, I'll say so.
- If a task won't fit the week's time budget (see `CLAUDE.local.md`), say so.

## Version roadmap

Release on Sundays. Each release is a git tag with measured results and written limits. If a phase slips, ship the smaller version with its real limits. A small honest release beats a late big one. Don't reorder without asking.

| Version | Target | What ships | Done when |
|---|---|---|---|
| v0.0 | Sun Nov 22 | Hand traces of the three we45 chains in `targets/ground_truth.md`, committed before any scanner code. Saved Bandit and Semgrep outputs. README stub. | Ground truth predates the scanner in git history |
| v0.1 | Sun Dec 6 | Parse a file, find routes, mark sources, propagate within a function, three sinks (SQLi, template injection, unsafe YAML). Chain output in text and JSON. Results table, README limits, CI running tests. | The three we45 chains are found, or each miss is explained; CI green |
| v0.2 | Sun Dec 27 | Per-sink sanitizers. Command injection and path traversal rules from my own snippets. Safe corpus. GitHub Action runs tests and the scanner on every PR. | Each rule has vulnerable and safe snippets; Action runs on PRs |
| v0.3 | Sun Jan 3 | Taint across functions within one file (per-function summaries). | Regression tests cover the new cases |
| v0.4 | Sun Jan 10 | Second target as the cross-file test (report misses; simple import resolution only if time allows). One-command benchmark harness. | Anyone can rerun the benchmark and get my counts |
| v1.0 | Sun Jan 24 | Stopping criteria met. Architecture diagram, limitations list, demo. LLM triage optional, cut first. | Every stopping criterion checked in the release note |

v0.1 work in the old day order, spread across weeks:
- **Week of Nov 16 (v0.0):** Crafting Interpreters ch. 2 (timebox 1 hour; Python's `ast` means no parser to write), `ast.dump` exercise, hand traces, Bandit and Semgrep baselines.
- **Week of Nov 23:** sources (route params, `request.json`, `.args`, `.form`, `.headers`, `.files`, `.url`), then propagation (assignments, dict lookups, `%`, f-strings, `+`).
- **Week of Nov 30 (v0.1):** sinks, rules, chain output, run on we45, results table, CI.

Never cut the README and the results table.

### v0.1 definition of done

- `python -m sast_tool <path>` finds Flask routes and tracks taint within each function
- Rules: SQL injection (#1), template injection, unsafe YAML deserialization
- Each finding printed as source → hops → sink, in text and JSON
- pytest suite using vulnerable and safe snippets I write myself
- Results table: my tool vs Bandit vs Semgrep on we45, as **counts** ("3 of 3"), including what mine misses and why
- CI running tests
- README with limitations stated openly

### Measuring results

Report counts, not percentages, until there are about 15 labeled cases. Grow the labeled set with my own vulnerable/safe snippets and the second target. Never pick a corpus that flatters the numbers; publish the one committed as ground truth.

## Design guidance (the taint model)

Every finding is: **source → propagation → sink**, unless a **sanitizer** intervenes.

- **Scope through v0.2:** intra-procedural (one function body), single file. Say this in the README. Cross-function is v0.3; cross-file is v0.4.
- **Sanitizers come in three kinds. Don't treat them as one:**
  1. *Cleaning functions* (`secure_filename(x)`) return a safe value. Easy to detect.
  2. *Guard checks* (`if not validate(x): return`) don't change the value; they make later code unreachable for bad input.
  3. *Sink-side protections* (a `--` separator, parameterized queries) leave the value alone and change how the sink reads it.
- **A sanitizer only protects the sink it was built for.** (we45's `/yaml_hammer` sanitizes the filename but loads the file's contents with `yaml.load`.) Model sanitizers per sink class.
- **SAST cannot find broken access control** (e.g. `/get/<cust_id>` returning any customer's record). Know this and be able to explain it.
- Keep rules as data (lists of sources, sinks, sanitizers), not hardcoded if-statements.
- Never crash a scan on one unparseable file.

## v2: the service (gated)

Not started until v1.0 ships and the Feb 7 decision point has passed. It is a separate project of 4-6 weeks. Do not add infrastructure before then. Order when it starts:

1. **Scan API.** `POST /scans` → `202 Accepted` + `Location`. `GET /scans/{id}` for status. `GET /scans/{id}/findings` paginated and filterable. `PATCH /findings/{id}` to mark a false positive. Consistent error format.
2. **PostgreSQL:** scans, findings, rules. One normalized findings schema (rule, file, line, severity, source, sink, status).
3. **Docker Compose:** API + Postgres + Redis.
4. **Redis:** job queue and results cache. **Cache key = hash(code + ruleset version)**, not a short TTL. Expiry only for eviction.
5. **Secure the API:** tokens, rate limiting, and a threat model. If `POST /scans` accepts a repo URL, the scanner runs `git clone` on user input. Treat it as an argument-injection risk.
6. Then: scan real repos, hand-triage, publish the false positive rate. If a real bug turns up in a maintained project, disclose privately first.

## Tools to compare

Bandit and Semgrep CE are required for the results table. Optional later: Datadog's static analyzer, GitHub CodeQL, Snyk Code (free tier).

## Repo layout (target structure)

```
sast-tool/
  README.md            # 30-second layer: pitch, results table, limits, how this was built
  CHANGELOG.md         # one entry per release
  CLAUDE.md            # this file (public)
  CLAUDE.local.md      # personal context (gitignored)
  pyproject.toml
  src/sast_tool/       # parser, taint engine, rules, report
  tests/
    corpus/vulnerable/ # snippets I write, labeled
    corpus/safe/       # false-positive tests
  targets/
    README.md          # how to clone the targets (clone dirs are gitignored)
    ground_truth.md    # hand traces, committed before scanner code
    baselines/         # saved Bandit and Semgrep outputs
  docs/
    architecture.md    # parser → taint engine → rules → report
    decisions.md       # each decision + the alternative I rejected
    learning-log.md    # weekly devlog (Sundays)
    limitations.md     # known misses, each with a minimal repro
    release-checklist.md
    results.md         # tool vs Bandit vs Semgrep, counts, triage notes, per version
    threat-model.md    # threat model of this tool
  .github/workflows/ci.yml
  # v2 adds: api/, docker-compose.yml, migrations/
```

## Documentation habits

- **Sundays:** 5-10 line devlog entry in `docs/learning-log.md`.
- **Every feature:** failing test first, then the feature, then a CHANGELOG line.
- **Every decision:** an entry in `docs/decisions.md` with the alternative rejected.
- **Every discovered miss:** a GitHub issue labeled `false-negative` with the smallest repro, linked from `docs/limitations.md`.
- **Every release:** `docs/release-checklist.md`.

## Claims

- README, release notes, resume, and the GitHub repo description describe only what exists and was measured. No invented numbers, no "detects X" for rules not built. Templates stay unfilled until the number is measured.
- The README's "How this was built" section says where AI helped and how output was verified: core logic hand-written, plumbing AI-assisted.

## Safety and conventions

- Python, pytest. Small commits with clear messages. Commit the corpus, ground truth, baselines, and results.
- Only read intentionally vulnerable apps and code I own or have permission to test. If I run a vulnerable app, run it locally or in Docker, never exposed to a network.
- Never scan or probe systems I don't own. Disclosure is private first.
- Nothing from DLMC or ITS systems that isn't already public.
- If using the VibeWise plugin: its approval gates win for when code is written; this file wins for what we're building and why.
