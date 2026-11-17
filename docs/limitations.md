# Limitations

What the tool misses or gets wrong. Each entry: one sentence, the smallest code that shows it, and a link to its `false-negative` or `false-positive` issue.

## By design

- Broken access control (e.g. we45's `/get/<cust_id>`) is invisible to SAST: the code is valid, only the missing authorization check is wrong, and there is no tainted value reaching a dangerous sink.

## Known misses

<!-- add as found -->
