# Learning log

Weekly devlog (Sundays, 5-10 lines) plus concept notes. Newest at the bottom.

<!-- Weekly template:
### Week of <date>
- Built:
- Broke / surprised me:
- Measured:
- Decided:
- Next:
-->

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

**How I traced it by hand**
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

## 2026-11-17: Symlinks and terminal redirection

**Symlink.** `ln -s ~/Vulnerable-Flask-App targets/Vulnerable-Flask-App` makes
a pointer, not a copy. The target app stays in its own git repo (so I can pin
its commit), but my tool can reach it at a path inside this repo. Git stores
only the link, and `.gitignore` (`targets/*/`) keeps it out of commits.

**Redirection.** `>` sends a command's output to a file and overwrites it, `>>`
appends. The shell opens the file before the command runs, so `>` creates the
file but not a missing folder, which is why I ran `mkdir -p targets/baselines`
first. Only stdout is redirected; error messages still print to the terminal.
That is how I saved the Bandit and Semgrep baselines, and kept the Semgrep
version in a separate file so the JSON stays parseable.
