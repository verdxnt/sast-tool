# Ground truth

Known vulnerabilities in each target, traced by hand **before** scanner code exists. This is the answer key for `docs/results.md`. Commit it before running your tool on the target, and don't edit past entries to match tool output. Add new ones with a dated note.

Line numbers refer to `app/app.py` at the pinned commit below. Traces copied unchanged from `Source-to-sink-log.md` in the target clone.

## we45/Vulnerable-Flask-App (commit `b6a4f97afd466e83e1f60781494252dec1c37039`)

Each chain: source, sanitizer, hops, sink. "In scope" says which release should find it.

| ID | Class | Route | In scope for |
|---|---|---|---|
| GT-1 | SQL injection | `/search` (POST) | v0.1 |
| GT-2 | Unsafe deserialization | `/yaml_hammer` (POST), file content | v0.1 |
| GT-2b | Path traversal (blocked by sanitizer, must not be flagged) | `/yaml_hammer` (POST), filename | v0.2 (safe case: tests false positives) |
| GT-3 | Template injection (SSTI) | 404 handler `pnf` | v0.1 |
| GT-4 | Template injection (SSTI) | `/search` error path, line 280 (`str(e)`) | v0.2 (taint passes through an exception) |

---

## GT-1: `/search` (POST)

**Vulnerability:** SQL injection

### Chain

```
source:     line 259   (search_term = content['search'])
sanitizer:  none       (nothing between 259 and 265 checks or escapes it)
hop:        line 261   (search_term is pasted into str_query via % formatting)
sink:       line 265   (db.engine.execute(str_query))
```

### Explanation

**Attack.** The client sends `' OR '1'='1`. Python pastes it in blindly:

```sql
... WHERE username = '' OR '1'='1';
```

Reading this the way the database does:

1. `username = ''` opens a quote and immediately closes it.
2. `OR '1'='1'` is now outside any quotes, so the database reads it as part of the command. `'1'='1'` is always true.

### Fix

Use a parameterized query, where you send the command and the data separately:

```python
db.engine.execute("... WHERE username = %s", (search_term,))
```

### What I learned from this trace

- `content = request.json` is a container. The source is the specific key, `content['search']`.
- `results = []` is server-made, so it isn't a source.
- The sink is the `db.engine.execute(...)` call, not the variable that holds its result.
- Reading or printing a value (line 260) isn't a sanitizer. Only code that makes it safe counts.

---

## GT-2 and GT-2b: `/yaml_hammer` (POST)

**Vulnerability:** Unsafe deserialization (`yaml.load` on an uploaded file)

### GT-2: Chain (file content)

```
source:     line 318   (f = request.files['file'])
sanitizer:  none       (for the content)
hop:        line 324   (f.save(file_path) writes the content to disk)
hop:        line 326   (open(file_path) reopens the same file)
hop:        line 327   (y = yfile.read() puts the content in y)
sink:       line 329   (ydata = yaml.load(y))
```

Note: `secure_filename` on line 320 only cleans `f.filename`, not the content.

### GT-2b: Chain (filename), broken by a sanitizer

```
source:     line 318   (f.filename)
sanitizer:  line 320   (fname = secure_filename(f.filename))
hop:        line 321   (fname = str(rand) + fname)
hop:        line 323   (file_path = cwd + '/Files/' + fname)
sink:       line 326   (open(file_path, 'r'))  also line 324 (f.save)
```

Taint is broken at 320, so path traversal is blocked. A naive tool would still flag line 326 (false positive).

### Explanation

An upload carries two client-controlled values: the filename and the content. Each has its own chain, and cleaning one does nothing for the other. `yaml.load` turns attacker-written text into live Python objects, and YAML can name functions to run, so this is remote code execution.

### Fix

```python
ydata = yaml.safe_load(y)
```

### What I learned from this trace

- Work backward from sinks: grep a sink list, name the argument, then walk up one assignment at a time.
- A hop is a line the value passes through. A line that only uses the variable (324 for `file_path`) isn't a hop on the way up, but it can be a second sink.
- Ask "sanitized *which value*?" A sanitizer on the filename says nothing about the content.
- A tool that follows variable names loses the trail between `f.save` (324) and `open` (326), because the only link is the path string. That's a false negative to design around.
- My first sink list missed `.save(`, so a sink list only finds what's on it.
- My grep also matched line 175, a docstring, which is a false positive from text search.

---

## GT-3: 404 handler `pnf` (`@app.errorhandler(404)`)

**Vulnerability:** Server-side template injection (SSTI)

### Chain (original code)

```
source:     line 112   (request.url, the URL the client requested)
sanitizer:  none
hop:        lines 103-112   (% formatting pastes the URL into the template text)
sink:       line 114   (render_template_string(template, ...))
```

### Explanation

The URL is pasted into the template *text* before `render_template_string` parses it, so Jinja reads the attacker's input as template code. A URL containing `{{ 7*7 }}` renders as `49`. Jinja runs inside the Python process, so the attacker can reach Python objects and from there the operating system, which makes this remote code execution. Passing `dir`, `help` and `locals` into the template gave that code more to work with.

It has the same shape as the `/search` SQL injection: a `%` builds a command out of client text, and an interpreter (here Jinja, there the database) then runs it.

### Fix

Context parameter passing. The template text is fixed, and the value is passed as a variable:

```python
template = '''... <h3> {{ current_url }}</h3> ...'''
return render_template_string(template, current_url=request.url), 404
```

### What I learned from this trace

- The source is the `request.url` read on line 112, not line 103 where the statement starts.
- Order is the reason the fix works: Jinja parses the template first and fills in values afterward as plain text, so a value is never parsed as template code. Flask also autoescapes HTML in values.
- Principle: data goes in the context, never in the template string. It's the same idea as a parameterized SQL query.
- My first fix attempt left `% request.url` after switching to `{{ }}`, used an undefined variable (`user_input`), and kept `dir`, `help` and `locals` that the template never used.
- The same mistake is on line 280 in `/search` (`str(e)` pasted into a template string), which is traced below as GT-4.


## GT-4: `/search` exception handler (`search_customer`, `except` block)

**Vulnerability:** Server-side template injection (SSTI), triggered through SQL injection

### Chain (original code)

```
source:     line 255   (request.json, the JSON body the client sent)
sanitizer:  none
hop:        line 259   (content['search'] → search_term)
hop:        line 261   (% formatting pastes search_term into str_query)
hop:        line 265   (db.engine.execute raises a database error; SQLAlchemy copies the SQL statement into the error message)
hop:        lines 270-280   (except ... as e; % str(e) pastes the message into the template text)
sink:       line 281   (render_template_string(template, ...))
```

### Preconditions

- A valid JWT for any user. `verify_jwt` checks the token, and nothing checks roles.
- The payload must make the query fail, for example with an unclosed quote. A payload that runs cleanly never reaches `except`.
- SQLAlchemy 1.x. In 2.0, `Engine.execute` was removed, so line 265 raises `AttributeError`. That message holds no attacker data, so there's no SSTI (and no SQLi).
- The route decorator needs its `@`. Without it, the function is never registered.

### Explanation

`search_term` goes into the SQL text unescaped. A payload like `{{7*7}}'` leaves an unmatched quote, so the database rejects the statement. SQLAlchemy builds its error message from the driver error plus the full statement (`[SQL: SELECT ... WHERE username = '{{7*7}}'';]`), so `str(e)` contains the payload exactly as sent. That message is pasted into the template text before Jinja parses it, so Jinja runs it and the page shows `49`. As in GT-3, this reaches Python objects and the OS: remote code execution for anyone with a valid token.

One payload uses both bugs: the SQL injection causes the error, and the error message carries the template code to the sink.

### Fix

1. **Fixes the SSTI:** keep the template text fixed and pass the message as a variable (`{{ error }}` with `render_template_string(template, error=str(e))`). Drop `dir`, `help` and `locals`.
2. **Better:** don't send exception text to the client at all. `str(e)` also leaks the SQL query and table names.

```python
except Exception:
    app.logger.exception("search failed")
    return jsonify({'Error': 'Search failed'}), 500
```

3. **Parameterizing the query** (the SQLi fix) removes this trigger but not the bug. Any other exception whose message includes user input would reach the sink again.

### What I learned from this trace

- Taint can pass through an exception: `e` is tainted when the call that raised it took tainted input and the library copies that input into the message.
- A finding can have preconditions (auth, a payload that causes an error, the library version). They decide whether it's exploitable, so the GT records them.
- Bugs can chain: here the SQLi is the trigger for the SSTI.
- Sources are where attacker data enters (`request.*`); sinks are where it exits to an interpreter. I mixed these up in Step 2.
- SAST rule idea: mark `e` as tainted only when the `try` block passed tainted data to a call. That catches this case without flagging every `except` block.