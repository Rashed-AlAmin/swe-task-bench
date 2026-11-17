# Failure case studies

Material for the README. Each entry is read off a recorded run, not inferred.

## click-3225 — debug scaffolding left in the library (Haiku 4.5, trial 1)

Broke **554 of 577** pass-to-pass tests while passing 0 of 7 fail-to-pass.

The model did not misunderstand the bug or gut the feature. It inserted
`print(..., file=sys.stderr)` tracing into `Option.__init__` to investigate,
and never removed it:

```python
+        import sys
+        print(f"[Option.__init__] flag_value={flag_value!r}, ...", file=sys.stderr, flush=True)
```

Every test that asserts on stderr then fails. This is the clearest argument in
the repo for why a fail-to-pass set alone is not a grader: on a benchmark that
only checked whether the reported symptom went away, a library left full of
debug prints could still have scored.

Diagnosable failure mode: **investigation scaffolding not cleaned up**, not a
reasoning error.

## click-3299 — guessed the exception type instead of checking the type (Haiku 4.5)

The reported object raises on comparison with a string. The gold fix narrows
the comparison with `isinstance(default_value, str)`. The model instead wrapped
the comparison in `try/except TypeError` — but the object in question raises
`ValueError`, so the guard never fires.

Right instinct (the comparison is unsafe), wrong mechanism (guessed which
exception rather than avoiding the comparison). On a later trial the same model
solved it, which is why single runs are not reported as results.

## click-3013 — correct fix, wrong position (Haiku 4.5)

The model found the same one-line transformation as the gold patch, but applied
it *after* the de-duplication step that compares the partial word against the
last argument. The gold patch applies it before. The comparison therefore still
ran against the raw quoted string.

Near-misses of this shape — right edit, wrong place in the sequence — are the
most useful thing a task can produce, because they separate "knows the API"
from "understands the order of operations".
