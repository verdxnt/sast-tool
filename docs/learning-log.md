## 2026-10-03: Running Bandit and Semgrep on an old project

**What I did:** Scanned three versions of a Flask app I built (before any
security fixes, partway through, and the current version) with Bandit
and Semgrep's free rules.

| Version | Bandit | Semgrep |
|---|---|---|
| Before fixes | 3 findings, incl. debug mode on | 1 finding (debug mode) |
| Partway | 2 Low | 0 |
| Current | 2 Low | 0 |


**What I learned:**
- Both tools catch simple one-line patterns like debug mode, and the
  finding goes away once it's fixed.
- Neither caught argument injection. Bandit warned about the subprocess
  call in every version, so it couldn't tell vulnerable from fixed.
- Why: yt-dlp treats any argument starting with `-` as an option, and
  some options run commands. So a "URL" like `--exec=...` could take
  over the command. A scanner just sees a list of strings passed to a
  program. It doesn't know that this program reads leading dashes as
  options, so it can't see the risk.
- My fix had two layers: checking the URL is http/https, and putting
  `--` before it so yt-dlp stops reading options. Bandit can't tell
  those layers are there, which is why its output didn't change.
