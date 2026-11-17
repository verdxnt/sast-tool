# Release checklist (about 20 minutes)

- [ ] Tests green, CI passing
- [ ] CHANGELOG: move "Unreleased" under the version heading
- [ ] `docs/results.md`: new section with this version's counts
- [ ] README results table and status line updated
- [ ] `docs/limitations.md` current
- [ ] Git tag (`git tag v0.1.0 && git push --tags`)
- [ ] GitHub release written (template below)
- [ ] Devlog line in `docs/learning-log.md`
- [ ] v0.1, v0.4, v1.0 only: resume line, 2-3 sentence LinkedIn post

## Release note template

```
## v0.X.0: <one-line summary>

### What changed
- <one line per change>

### Measured results (target: <name>, ground truth commit <hash>)
| Class | Found in previous | Found in this | False positives |
|---|---|---|---|

### Known limits
- <what it still misses, with a link to the issue>

### How to reproduce
<the one command>
```
