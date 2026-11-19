# Decisions

Each decision and the alternative rejected. Newest at the bottom.

<!-- Template:

## NNN: <decision>
- Context: <the problem in two sentences>
- Options: <A, B, C, one line each>
- Decision: <which, and the main reason>
- Consequences: <what it costs and what it won't handle>
-->

## 001: Ground truth comes from my hand traces only
- Context: Semgrep flagged a chain (line 280) I hadn't traced, and both tools reported extra findings outside my list.
- Options: (A) add every tool finding to the ground truth; (B) keep only what I trace by hand, and add new chains as dated additions after tracing them myself.
- Decision: B. Rejected A.
- Consequences: Using the tools' output as the answer key would grade them against themselves and make my score circular. Costs time (GT-4 took a separate trace), and the key may miss bugs I don't find.

## 002: Taint state is a dict of name to path, not a set of names
- Context: A set answers "is this name tainted?" but can't say how it became tainted, and findings must print source, hops, sink.
- Options: (A) set of tainted names; (B) dict from name to the list of steps (line number and code) that tainted it.
- Decision: B. Rejected A. Each hop is copied into the new name's path at assignment time.
- Consequences: Slightly more bookkeeping per assignment. Enables the chain output. Because paths are copied, a later reassignment of the original name doesn't change other names' paths.

## 003: Taint state is per function, not per file
- Context: v0.1 scope is intra-procedural, single file.
- Options: (A) one shared taint state for the whole file; (B) a fresh dict for each function body.
- Decision: B. Rejected A.
- Consequences: Variables with the same name in different routes (`content`, `results`) can't contaminate each other. Misses taint passing between functions (that is v0.3).

## 004: Find tainted names inside expressions with ast.walk on the right side
- Context: In `str_query = "..." % search_term` the tainted name is nested inside a `BinOp`.
- Options: (A) handle each expression type by hand (`BinOp`, `JoinedStr`, ...); (B) walk every node on the right side and check each `Name` against the taint dict.
- Decision: B for v0.1. Rejected A for now.
- Consequences: Simple and catches nesting at any depth. Over-taints: it also sees names inside calls like `secure_filename(f.filename)`, so GT-2b will be a false positive until sanitizers exist (v0.2). Doesn't distinguish how the value is used.

## 005: Reassigning a tainted name to a clean value removes it from the state
- Context: `search_term = "fixed"` after `search_term` was tainted.
- Options: (A) keep the name tainted forever; (B) remove it, checking the right side before updating so `x = x + "safe"` stays tainted.
- Decision: B. Rejected A.
- Consequences: Fewer false positives. Unsound across branches (`if`/`else`), since the assignment might not run. Documented as a v0.1 limitation.
