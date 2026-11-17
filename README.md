# sast-tool

A taint-tracking static analyzer for Flask apps, written in Python. It parses code into ASTs and follows attacker-controlled data from request sources to dangerous sinks.

**Status: in progress.** It finds Flask route handlers. Taint tracking and rules are not built yet, and nothing has been measured. See [CHANGELOG.md](CHANGELOG.md) and the roadmap below.

## Roadmap

| Version | Scope |
|---|---|
| v0.1 | Sources, intra-function propagation, three sinks (SQL injection, template injection, unsafe YAML), results vs Bandit and Semgrep |
| v0.2 | Per-sink sanitizers, command injection, path traversal, safe corpus, GitHub Action |
| v0.3 | Taint across functions in one file |
| v0.4 | Second target (multi-file), reproducible benchmark |
| v1.0 | Stopping criteria met, full results and limitations |

## How this was built

Core analysis logic (source detection, propagation, sink matching, sanitizers) is hand-written. Plumbing (CLI, output formatting, CI, test boilerplate) is AI-assisted and reviewed line by line.
