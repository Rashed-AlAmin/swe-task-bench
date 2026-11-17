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

## click-3021 — fixed the symptom, removed the protection (Haiku 4.5)

Passed 0 of 1 fail-to-pass. The most instructive miss in the set.

Both the model and the maintainers changed the same two lines. The code
deliberately writes the prompt in two pieces, and the comment above it says why:

```python
echo(text.rstrip(" "), nl=False, err=err)
# Echo a space to stdout to work around an issue where
# readline causes backspace to clear the whole line.
return f(" ")
```

The last character must pass through the input function, or readline lets
backspace wipe the line.

**Gold** keeps the split and generalises it — print everything but the last
character, pass the last character through:

```python
echo(text[:-1], nl=False, err=err)
return f(text[-1:])
```

**The model** instead suppressed the space conditionally:

```python
echo(text.rstrip(" "), nl=False, err=err)
return f(" " if text.endswith(" ") else "")
```

With no suffix it now passes an **empty** string through the input function.
The reported symptom is gone and the readline workaround the comment describes
is silently gone with it.

The test encodes the invariant rather than the symptom — with
`err=True` it asserts stdout receives `"x"` while stderr receives
`"Prompt to stderr with no suffi"`, i.e. the final character is still routed
through the input function:

```python
click.prompt("Prompt to stderr with no suffix", prompt_suffix="", err=True)
assert out == "x"
assert err == "Prompt to stderr with no suffi"
```

Diagnosable failure mode: **satisfied the report, not the invariant.** This is
the task that most directly rewards reading the comment above the line you are
changing, and it is the reason the candidate prompt says not to weaken existing
behaviour to make a symptom go away.
