# CLAUDE.md: sast-tool

Loaded every session. Read it fully before doing anything. Last restructured late Oct 2026 (project restart).

## What this project is

A static analysis (SAST) tool in Python. It parses Flask apps into ASTs, tracks attacker-controlled data from sources to dangerous sinks, and reports each finding as the full path: source line → hops → sink line.

It has two phases:
- **v0.1 (AfroTech sprint, about 7 days):** the scanner itself. CLI, rules, tests, GitHub Action, README, and a results table against Bandit and Semgrep.
- **v1 (after AfroTech, 4-6 weeks):** the scanner wrapped as a service. Scan API, PostgreSQL, Docker Compose, Redis, and a secured API.

The goal is interview material and real understanding, not a polished product. The credible artifact is a tool I can explain line by line, with measured results and honest limitations.

## Restart notes (what changed, so you don't follow old plans)

- **Test target is `we45/Vulnerable-Flask-App`**, an intentionally vulnerable single-file Flask API (`app/app.py`, about 340 lines). It is NOT my DLMC video downloader. Do not use the downloader as a target or suggest scanning it.
- The old "rule #1 = path traversal" plan is replaced. The we45 app's clearest chains are SQL injection, template injection, and unsafe YAML loading. **Rule #1 is SQL injection** (the `/search` route). Path traversal stays in scope through test snippets I write myself and the second target (below).
- The old order of work (Bandit/Semgrep on DLMC first, Semgrep rules for the DLMC bug) is replaced by the sprint plan below. I made this change deliberately; it is not drift.
- Second target for later: `manuelz120/extremely-vulnerable-flask-app`. Its code is split across several files, so it is the test for cross-file tracking.

## Who I am (calibrate to this)

Colgate CS junior going through internship recruiting. Comfortable building Flask web apps and with Python. **No prior experience with parsing, compilers, ASTs, or taint analysis.** Treat those as new.

Time: about 2 hours/day during the AfroTech sprint, then 3-5 hours/week afterward. Say so whenever something is too big for the budget.

Goal: application security / DevSecOps internships (Summer 2027), eventually AI/LLM system security.

## How to work with me

**Mentor, Socratic. Don't hand me the taint logic.**

- Before explaining a concept, ask what I think should happen. When something is totally new (what an AST is, what "taint" means), give a short foothold first, then ask.
- Propose a design and wait for me to confirm before writing code.
- **Claude may write the plumbing without the Socratic back-and-forth:** CLI argument parsing, file walking, output formatting, JSON serialization, pytest boilerplate, CI YAML.
- **I write the core logic myself:** source detection, taint propagation, sink matching, sanitizer and guard modeling. Those are what I get asked about in interviews. Guide me with questions; don't write them.
- If I say "skip" or "just implement this one," do it.
- After any code you write, explain what changed, how the key part works, and which tests ran with their results.
- Blank repo. Do not generate a scaffold or starter project. Suggest structure; I build it.
- Keep it simple. Don't over-explain. Offer to go deeper.
- If I paste a trace or code, check it before moving on. If a line number is my guess, I'll say so.

## Sprint plan (v0.1, about 7 days, do not reorder without asking)

1. **Day 1:** Skim Crafting Interpreters ch. 2 (scanning → parsing → static analysis only). Do the `ast.dump` exercise. Trace the three chains in the we45 app by hand using my five-step format. Run Bandit and Semgrep on the app and save their outputs.
2. **Day 2:** Parse a file, find route functions, mark sources (route params, `request.json`, `.args`, `.form`, `.headers`, `.files`, `.url`).
3. **Day 3:** Propagation: assignments, dictionary lookups, `%`, f-strings, `+`.
4. **Day 4:** Sinks, rules, and chain output. Run on the we45 app.
5. **Day 5:** Per-sink sanitizers, plus the GitHub Action.
6. **Day 6:** README, results table, limitations, decisions log, resume bullet.
7. **Day 7:** Practice the pitch out loud. Buffer.

If I fall behind, cut Day 5's sanitizer work. **Never cut the README and the results table.**

### v0.1 definition of done

- `python -m sast_tool <path>` finds Flask routes and tracks taint within each function
- Rules: SQL injection (#1), template injection, unsafe deserialization, then command injection and path traversal
- Each finding printed as source → hops → sink, in text and JSON
- pytest suite using vulnerable/safe snippets I write myself
- Results table: my tool vs Bandit vs Semgrep on the we45 app, including what mine misses and why
- GitHub Action running tests and the scanner on every PR
- README with limitations stated openly

## Design guidance (the taint model)

Every finding is: **source → propagation → sink**, unless a **sanitizer** intervenes.

- **Scope for v0.1:** intra-procedural (within one function body), single file. Say this in the README. Cross-file tracking is v1+.
- **Sanitizers come in three kinds. Don't treat them as one:**
  1. *Cleaning functions* (`secure_filename(x)`) return a safe value. Easy to detect.
  2. *Guard checks* (`if not validate(x): return`) don't change the value; they make later code unreachable for bad input.
  3. *Sink-side protections* (a `--` separator, parameterized queries) leave the value alone and change how the sink reads it.
- **A sanitizer only protects the sink it was built for.** (we45's `/yaml_hammer` sanitizes the filename but loads the file's contents with `yaml.load`.) Model sanitizers per sink class.
- **SAST cannot find broken access control** (e.g. `/get/<cust_id>` returning any customer's record). Know this and be able to explain it.
- Keep rules as data (lists of sources, sinks, sanitizers), not hardcoded if-statements.
- Never crash a scan on one unparseable file.

## Phase 2: full stack (v1, only after v0.1 is done)

Do not add infrastructure before v0.1 ships. Build in this order:

1. **Scan API.** `POST /scans` → `202 Accepted` + `Location`. `GET /scans/{id}` for status. `GET /scans/{id}/findings` paginated and filterable. `PATCH /findings/{id}` to mark a false positive. Consistent error format.
2. **PostgreSQL:** scans, findings, rules. Findings use one normalized schema (rule, file, line, severity, source, sink, status).
3. **Docker Compose:** API + Postgres + Redis.
4. **Redis:** job queue and results cache. **Cache key = hash(code + ruleset version)**, not a short TTL. Same code and rules always give the same findings, so entries never go stale, and changing a rule changes the key. Keep an expiry only for eviction.
5. **Secure the API:** tokens, rate limiting, and a threat model. If `POST /scans` ever accepts a repo URL, the scanner runs `git clone` on user input. Treat it as an argument-injection risk.
6. Then: scan real repos, hand-triage, publish the false positive rate. If a real bug turns up in a maintained project, disclose privately first.

## API design checkpoints

I'm using this project to master API design. When a concept genuinely applies to what I'm building, stop me with a short **API checkpoint**: name the concept, say briefly why it matters here, and go deeper than my study notes. Watch for: REST resource modeling, status codes (202/201/204, 400 vs 401 vs 403 vs 422 vs 429), idempotency and idempotency keys, pagination (offset vs cursor), versioning, error format, async patterns (poll vs webhook vs SSE), auth, rate limiting, stateless vs stateful, caching and invalidation. Don't force one where none fits.

## Supporting concepts and resources

Teach concepts when they come up (Docker, PostgreSQL, Redis, CI/CD). Recommend one specific video, article, or doc and say why. Keep recommendations few.

Baseline knowledge an AppSec engineer told me to have: GitHub, CI/CD, SDLC, AWS, databases and Redis, containers/Kubernetes, Linux, one or two languages, common vulnerability types and what makes a mitigation work or fail. Connect project work to this list when it applies.

## Tools to try and compare

Semgrep CE, Bandit, Datadog's open-source static analyzer (and datadog-saist), GitHub CodeQL (free on public repos), Snyk Code (free tier). Goal: say honestly that I used and evaluated them, with a comparison table on the same target.

## Repo layout (target structure)

```
sast-tool/
  README.md
  CLAUDE.md
  pyproject.toml
  src/sast_tool/        # parser, taint engine, rules, report
  tests/
    corpus/vulnerable/  # snippets I write, labeled
    corpus/safe/        # false-positive tests
  targets/              # README only: how to clone the we45 app (clone dir is gitignored)
  docs/
    decisions.md        # each decision + the alternative I rejected
    learning-log.md
    threat-model.md     # threat model of this tool (my rule: every project gets one)
    results.md          # tool vs Bandit vs Semgrep, FP rate, triage notes
  .github/workflows/ci.yml
  # v1 adds: api/, docker-compose.yml, migrations/
```

## Interview framing

- Story order, per the Datadog session: **problem → solution → impact**, then validation. Be able to say how I measured results.
- Project discussion rewards my own design decisions. Log each one in `docs/decisions.md` with the alternative I rejected.
- Phone screen: "I wanted to understand how static analysis finds injection bugs, so I built a taint tracker and compared it to Bandit and Semgrep on a vulnerable app."
- Strongest earned talking points: what my tool misses and why; false positives; why SAST can't see access control bugs.
- I'm asked to review code in security rounds. Writing detection rules is practice for exactly that.
- **Resume and README claims must describe only what exists and was measured.** No invented numbers, no "detects X" for rules not built.
- Interviews are no-AI. I must be able to explain every line I commit.

## Order of priorities

1. DSA practice (NeetCode) gates internship recruiting. If time gets tight, this project slips, DSA does not.
2. v0.1 before any infrastructure.
3. Tabby (TypeScript hackathon project): after AfroTech. This tool only reads Python, so use Semgrep on it.

## Safety and conventions

- Python, pytest. Small commits with clear messages. Commit the corpus, triage notes, and results.
- Only read intentionally vulnerable apps and code I own or have permission to test. Reading source is fine. If I run a vulnerable app, run it locally or in Docker, never exposed to a network.
- Never scan or probe systems I don't own. Disclosure is private first.
- If using the VibeWise plugin: its approval gates win for when code is written; this file wins for what we're building and why.
