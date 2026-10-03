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
## 2026-10-03: Concept: tracing tainted data (source → sink)

**vocabulary**
| Term | Meaning | In my downloader |
|---|---|---|
| Source | Where untrusted data enters | The URL read from the request |
| Sink | Where data does something dangerous | The call that runs the subprocess |
| Sanitizer / validator | Code that makes the data safe | Scheme check; the `--` separator |
| Propagation (a "hop") | Data moving to a new place | Passed to a function, stored in a new variable, put in a list |
| Taint | The label "this came from an attacker" | Follows the value through every hop |

A vulnerability = tainted data reaches a sink without passing through
a sanitizer.

**How I traced it by hand** (run in the repo root)
1. Find sources:   `grep -n "request\." *.py`
2. Find sinks:     `grep -nE "subprocess|os\.system|open\(|send_file|eval\(" *.py`
3. Follow the value: `grep -n "url" *.py`
4. Each time the value is stored under a new name, grep the new name
   (`url` became an element of `command`, so I searched `command`).
5. Repeat until I reach the sink.

**What I learned**
- grep follows names, but taint follows values. When the value moves
  into a new variable or a list, a name search loses it.
- Hops that cross files, or hand work to another thread, are the
  hardest for tools to follow.
- A validator that returns True/False doesn't clean the value. A tool
  has to understand that the code after the check only runs if it passed.
