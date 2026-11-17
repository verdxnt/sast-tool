# Targets

The apps the scanner is tested against. The clones live **outside this repo**, in the home directory, so they keep their own git history. Only this README, `ground_truth.md`, and `baselines/` are committed here.

## Primary: we45/Vulnerable-Flask-App

- Clone location: `~/Vulnerable-Flask-App`
- Upstream: https://github.com/we45/Vulnerable-Flask-App
- Pinned commit: `b6a4f97afd466e83e1f60781494252dec1c37039`
- File scanned: `~/Vulnerable-Flask-App/app/app.py`

The clone also holds my own notes and corpus commits on top of the pinned commit. `app/app.py` is unchanged from upstream, and the line numbers in `ground_truth.md` refer to it. Check that before every benchmark run:

```
git -C ~/Vulnerable-Flask-App diff b6a4f97 -- app/app.py   # must print nothing
```

To set it up on a fresh machine:

```
git clone https://github.com/we45/Vulnerable-Flask-App ~/Vulnerable-Flask-App
git -C ~/Vulnerable-Flask-App checkout b6a4f97afd466e83e1f60781494252dec1c37039 -- app/app.py
```

Read the source only. If you run it, run it locally or in Docker, never exposed to a network.

## Second (v0.4): manuelz120/extremely-vulnerable-flask-app

Not cloned yet. Clone it next to the first one when v0.4 starts, and pin its commit here:

```
git clone https://github.com/manuelz120/extremely-vulnerable-flask-app ~/extremely-vulnerable-flask-app
```

## Baselines

Save tool outputs in `baselines/`, named `<tool>-<target>.<ext>`, and record the tool version next to each. Create the folder first (`mkdir -p targets/baselines`), because `>` won't create it. For example:

```
bandit --version > targets/baselines/bandit-we45.txt
bandit -r ~/Vulnerable-Flask-App/app -f txt >> targets/baselines/bandit-we45.txt
semgrep --version > targets/baselines/semgrep-we45.json.version
semgrep --config auto --json ~/Vulnerable-Flask-App/app > targets/baselines/semgrep-we45.json
```

The Semgrep version goes in its own file so the JSON stays parseable.
