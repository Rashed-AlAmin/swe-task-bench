# swe-task-bench

A small, honest benchmark of **real** bugs from a real Python project, built to
measure whether a coding model can localize and fix a defect when it is told
only what a confused user saw — never what went wrong.

Every task is mined from a merged pull request in
[pallets/click](https://github.com/pallets/click). Nothing here is invented.

---

## Why this exists

An eval task is not a programming exercise. It is a **measuring instrument**.
A task every model solves measures nothing; a task no model solves measures
nothing. The useful task is the one that *separates* — and where the models
that fail, fail for a reason you can name.

That is the only thing this repository tries to do well.

---

## What one task is

| Artefact | What it is |
|---|---|
| `problem.md` | The bug as a user would report it — symptom only |
| `base_commit` | The commit immediately before the real fix landed |
| `gold.patch` | The maintainers' actual fix (reference, never the grading key) |
| `test.patch` | The tests that shipped with that fix |
| `fail_to_pass` | Tests that fail before the fix and pass after — *did you fix it?* |
| `pass_to_pass` | Tests that pass both before and after — *did you break anything?* |

`pass_to_pass` is the anti-cheat. Without it a model can delete a failing test,
or gut the feature, and look like it succeeded.

## How the problem statements are written

This is where most of the authoring effort went. Each statement is written in
the voice of a junior developer filing an issue against a library they do not
understand: a plausible app, the command they ran, the output they got, the
output they expected. They are checked mechanically so that **no statement
contains the name of any file, function, method, or attribute the real fix
touches**, and none describes the cause.

Saying "the off-by-one in the offset" measures reading comprehension.
Saying "page 2 shows me row 11 twice" measures engineering.

## How grading works

1. Export the project at `base_commit` into a **history-free** directory and
   re-initialise it as a fresh single-commit repository.
2. Hand the model the problem statement and nothing else. It never sees the tests.
3. Discard any edit it made under `tests/` — then apply the official `test.patch`.
4. Run `fail_to_pass` and `pass_to_pass`.

**Resolved** = every fail-to-pass test passes *and* no pass-to-pass test broke.

The export in step 1 is not a git worktree, and that distinction is the whole
ball game. A worktree shares the upstream object database, so a candidate can
run `git log --all --grep="..."` and read the exact commit it is being asked to
reproduce. The sealed export contains one commit named `base`; the project's
future does not exist inside it, while `git diff` still captures the
candidate's own work.

Outcomes are read from pytest's JUnit XML rather than scraped from stdout,
because `FAILED` lines carry a trailing ` - message` that makes text parsing
ambiguous for parametrised ids containing spaces.

### Controls

Every task is checked against three controls before it is allowed into the set:

- **null** — an untouched tree must grade *not resolved*
- **gold** — the maintainers' own patch must grade *resolved*
- **cheat** — deleting the tests and leaving a stub that passes must *still*
  grade not resolved, and must be flagged as tampering

A task that fails any of the three is a broken ruler and is dropped. All tasks
in this repo pass all three. `scripts/controls.sh <pr>` reproduces it.

The cheat control matters more than it looks. A grader that merely runs the
test files it is handed will happily score a deleted test suite as a pass. This
one restores `tests/` from the base commit before applying the official test
patch, so tampering is reverted rather than rewarded.

Of 30 mined candidates, 24 produced a usable fail-to-pass set; the rest changed
no observable test outcome and were discarded.

---

## Results

<!--RESULTS-->

| Task | Fix size | F2P | P2P | Haiku 4.5 |
|---|---|---:|---:|---|
| [click-3299](https://github.com/pallets/click/pull/3299) | +1/-1 | 1 | 551 | ✅ 1/1 |

✅ solved in every trial · ◐ solved in some trials · ❌ never solved · ⚠️ broke existing tests in at least one trial

**Haiku 4.5** — 100% of 1 attempts resolved · 1 tasks always, 0 sometimes, 0 never · 0 attempts broke existing tests · median 93s

---

## Reproducing

```bash
python3 -m venv .venv && .venv/bin/pip install pytest
git clone https://github.com/pallets/click repo
scripts/controls.sh 3299                     # verify a task's null/gold controls
.venv/bin/python scripts/run_task.py 3299 <model>
.venv/bin/python scripts/report.py
```

## Limitations

Stated plainly, because a benchmark that hides these is not worth reading:

- **One upstream project.** Everything is `click`, so these results describe
  mid-size pure-Python CLI library code and nothing else.
- **Small n.** With 16 tasks, a one-task difference is noise, not a finding.
- **One attempt per task.** No pass@k, no retries, no temperature sweep.
- **Contamination is possible.** These PRs are public and most merged in 2026;
  a model may have seen the fix. Recency lowers the risk, it does not remove it.
- **Environment, not container.** The reported numbers were produced in a
  pinned virtualenv on the host, not inside the supplied image, so they are
  reproducible on a comparable machine rather than bit-for-bit anywhere.
- **Timing sensitivity.** A few tasks exercise terminal, pager and interrupt
  behaviour. Those were graded on an unloaded machine; a heavily loaded host
  can turn them flaky in either direction.
- **Only Claude models are measured here.** The harness is model-agnostic —
  `run_task.py` takes any command-line coding agent — but these numbers cover
  the models the author had access to.

## Author

MD Rashed Al Amin — [github.com/Rashed-AlAmin](https://github.com/Rashed-AlAmin)
