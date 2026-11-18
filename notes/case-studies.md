# Failure case studies

Material for the README. Every entry is read off a recorded run in `results/`
— the diff, the grader's verdict and the run metadata — not inferred from what
a model "would probably do". Run identifiers are given so each claim can be
checked against the file it came from.

Void records (runs the API killed) are excluded; see the README's Limitations.

---

## click-3021 — six attempts, one wrong answer

**The whole set agreed with itself and disagreed with the fix.**
`0/3` for Haiku 4.5, `0/3` for Sonnet 5. Not one trial passed the single
fail-to-pass test, and not one trial broke a pass-to-pass test. Six confident,
clean, wrong patches.

The code writes the prompt in two pieces, and the comment above it says why:

```python
echo(text.rstrip(" "), nl=False, err=err)
# Echo a space to stdout to work around an issue where
# readline causes backspace to clear the whole line.
return f(" ")
```

The last character must pass through the input function `f`, or readline lets
backspace wipe the line.

**Gold** keeps the split and generalises it — echo everything but the last
character, pass the last character through, so exactly one character always
reaches the input function:

```python
-            echo(text.rstrip(" "), nl=False, err=err)
-            # Echo a space to stdout to work around an issue where
+            echo(text[:-1], nl=False, err=err)
+            # Echo the last character to stdout to work around an issue where
                 # readline causes backspace to clear the whole line.
-            return f(" ")
+            return f(text[-1:])
```

**All six runs** wrote a variant of the same other idea: emit a space *only if
one was stripped*, otherwise emit nothing.

```python
+ input_prompt = " " if len(text) > len(stripped_text) else ""   # haiku t1
+ space = " " if text and text[-1] == " " else ""                # haiku t2
+ return f(text[len(stripped):])                                 # sonnet t1
+ return f(" " if text.endswith(" ") else "")                    # sonnet t2
+ return f("")                                                   # sonnet t3
```

Each is correct about the reported symptom and each passes an **empty** string
to `f` when `prompt_suffix=""`. The readline workaround the comment describes
is silently gone in every one of them.

The hidden test encodes the invariant rather than the symptom. With `err=True`
the prompt goes to stderr, so whatever `f` receives is the only thing that can
appear on stdout:

```python
click.prompt("Prompt to stderr with no suffix", prompt_suffix="", err=True)
assert out == "x"
assert err == "Prompt to stderr with no suffi"
```

The problem statement (`tasks/click-3021/problem.md`) is a user report about
`admin>` rendering as `admin> `. It never mentions readline, never mentions
`err=True`. The only clue available to the candidate was the comment sitting on
the line it was editing — and every attempt deleted it or routed around it.

Diagnosable failure mode: **satisfied the report, not the invariant.** This is
the task that most directly rewards reading the comment above the line you are
changing, and it is why the candidate prompt says not to weaken existing
behaviour to make a symptom go away.

A footnote on that task: `click-3021__claude-sonnet-5__t1` is the only
contamination-flagged run in the whole set. The agent tried
`pip download click --no-deps`; the egress blackhole refused it
(`ProxyError(... [Errno 111] Connection refused)`), and it then failed
honestly like the other five.

---

## click-3004 — the symptom fixed, the library regressed (Sonnet 5, trial 2)

The clearest argument in the repo for pass-to-pass tests.
Sonnet solved this task on trials 1 and 3 in 14–15 turns with ~35-line diffs.
On trial 2 it **passed all 5 fail-to-pass tests and still failed the task**,
because it broke 2 of 295 pass-to-pass tests.

**Gold** is two lines:

```python
+            elif isinstance(default_value, enum.Enum):
+                default_string = default_value.name
```

**Trial 2** wrote 78 lines across three files: a new public `ParamType`
method with a `.. versionadded:: 8.2.2` docblock, a `Choice` override, two
call-site changes in `core.py` and a CHANGES.rst entry.

```python
+    def get_default_display(self, value: t.Any, ctx: Context | None) -> str:
+        """Convert a default value of this type to a string for display ..."""
+        return str(value)
...
+    def get_default_display(self, value: t.Any, ctx: Context | None) -> str:
+        normalized_mapping = self._normalized_mapping(ctx=ctx)
+        if value in normalized_mapping:
+            return normalized_mapping[value]
+        return str(value)
```

The design is defensible. The bug is in `value in normalized_mapping`:
dict membership compares with `==`, and Python's numeric tower makes
`0.0 == 0` and `2 == 2.0` true with equal hashes. So the lookup silently
coerces a default across numeric types — exactly what the suite forbids in a
comment right above the cases it broke:

```python
# Values are not coerced to the type of the choice, even if equivalent.
([0, 1], 0.0, "0.0"),     # broke: rendered "0"
([1.0, 2.0], 2, "2"),     # broke: rendered "2.0"
```

Those two parameter sets are precisely the grader's
`p2p_broken_ids`.

Diagnosable failure mode: **a larger design than the bug needed, carrying an
equality assumption the existing suite already documents.** A benchmark that
scored only the reported symptom would have marked this run solved.

---

## click-3225 — two different ways to fail the same task (Haiku 4.5)

### Trial 1 — debug scaffolding left in the library

Broke **554 of 577** pass-to-pass tests while passing 0 of 7 fail-to-pass.

The model did not misunderstand the bug. It inserted
`print(..., file=sys.stderr)` tracing into `Option.__init__` to investigate,
and never removed it:

```python
+        import sys
+        print(f"[Option.__init__] flag_value={flag_value!r}, ...", file=sys.stderr, flush=True)
```

Every test that asserts on stderr then fails. Failure mode:
**investigation scaffolding not cleaned up**, not a reasoning error.

### Trial 3 — edited the tests it was told not to touch

545.1s, 120 turns, 115 diff lines, 66 shell calls. It added two private state
flags and a five-condition special case to `core.py`:

```python
+        self._default_from_flag_value = False
+        self._default_is_true_no_flag_value = False
...
+        source = ctx.get_parameter_source(self.name)
+        if (self.is_flag and value is not UNSET
+            and source in (ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP)
+            and not self._default_from_flag_value
+            and not self._default_is_true_no_flag_value
+            and isinstance(value, type)):
```

and then edited `tests/test_options.py` to agree with it — despite the
prompt's explicit *"Do NOT modify anything under `tests/`"*.

It bought nothing. `grade.py` reverts `tests/` and reapplies the official test
patch before running anything, so the run is graded against the real suite:
**F2P 5/7, 6 pass-to-pass tests broken, `tampered_with_tests: true`.**

This is the design point worth stating plainly: tampering is recorded as a
behavioural signal about the model, never as a scoring loophole. The grader
cannot be reached from inside the worktree.

---

## click-3884 — a task that separates the two models

Haiku 4.5 `0/3`, Sonnet 5 `3/3` — the widest separation in the set. Sonnet
solved it in 11, 13 and 14 turns, 9/9 every time. Haiku never solved it,
but was never far off: **5/9, 5/9 and 7/9** fail-to-pass, with zero
pass-to-pass breakage in all three.

The bug has two halves: `show_envvar` must handle a *sequence* of env var
names, and must treat an *empty* `envvar` as absent. Haiku's best trial got the
sequence half right at both call sites:

```python
+            else:
+                envvars_list = [x for x in self.envvar if x]
+                if envvars_list:
+                    envvar_str = ", ".join(f"'{x}'" for x in envvars_list)
+                    result += f" (env var: {envvar_str})"
```

What it left untouched is the auto-envvar branch, which still reads
`if envvar is None:`. Gold changes that test to `if not envvar`:

```python
-            if envvar is None:
+            if not envvar and (
+                self.allow_from_autoenv
+                and ctx.auto_envvar_prefix is not None
+                and self.name
+            ):
```

So with `envvar=""`, Haiku's version suppresses the output instead of falling
back to the generated name — the remaining failures.

Diagnosable failure mode: **fixed the half of the bug the report showed and
missed the half that only the falsiness of the value reveals.** Partial credit
across three trials, and no reward for it; the task is scored resolved or not.

---

## click-3865 — one character class apart (Sonnet 5, trials 2 and 3)

Nobody solved this one: Haiku `0/3`, Sonnet `0/3`. But two Sonnet trials
passed **all 6** fail-to-pass tests and still failed, on 2 of 30
pass-to-pass tests — in a 14-line diff whose one substantive line is almost
the gold fix.

The function shortens a help string at the first sentence end. The bug is that
`vs.` looks like a sentence end. Gold decides with *not lowercase*:

```python
if word.endswith(".") and (i == last_index or not words[i + 1][0].islower()):
```

Sonnet decided with *uppercase*:

```python
if word[-1] == "." and (i == last_index or words[i + 1][0].isupper()):
```

The two agree on letters and disagree on everything else. The suite already
contains the case that separates them:

```python
pytest.param("Pick a fruit. 3 remain.", 20, "Pick a fruit.", id="digit after dot")
```

`"3".islower()` is False, so gold stops. `"3".isupper()` is also False, so the
model keeps going. The grader's `p2p_broken_ids` are exactly that parameter
set and its no-wrap-mark twin.

Diagnosable failure mode: **the negation of a character class is not its
complement.** This is the single sharpest argument in the benchmark for
running the existing suite rather than only the new tests — the diff is small,
readable and looks right.

---

## click-3299 — guessed the exception type instead of checking the type (Haiku 4.5)

The reported object raises on comparison with a string. The gold fix narrows
the comparison with `isinstance(default_value, str)`. The model instead wrapped
the comparison in `try/except TypeError` — but the object in question raises
`ValueError`, so the guard never fires.

Right instinct (the comparison is unsafe), wrong mechanism (guessed which
exception rather than avoiding the comparison). On a later trial the same model
solved it, which is why single runs are never reported as results.

---

## click-3013 — correct fix, wrong position (Haiku 4.5)

The model found the same one-line transformation as the gold patch, but applied
it *after* the de-duplication step that compares the partial word against the
last argument. The gold patch applies it before. The comparison therefore still
ran against the raw quoted string.

Near-misses of this shape — right edit, wrong place in the sequence — are the
most useful thing a task can produce, because they separate "knows the API"
from "understands the order of operations".
