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

### What the candidate could still cheat with, and how that is handled

The candidate has a shell, so it can try to fetch a released version of the
library that already contains the fix. This is not hypothetical: in an earlier
sweep the screen caught four runs doing exactly that — `pip download
click==8.5.1 --no-binary :all:` followed by unpacking the sdist, and
`pip install click==8.3.0` into a scratch venv. Those runs were discarded.

Two measures now apply, in this order.

**Prevention.** The agent is launched with every proxy variable pointing at a
dead local port, with only the Anthropic API exempted via `NO_PROXY` so the
agent itself can run. `pip` and `curl` inherit this and fail to reach PyPI.
`PYTHONPATH` is set to the worktree's `src/`, mirroring the grader, so the
suite is runnable offline and nothing needs installing in the first place.
This is verified by a probe run that asks an agent to fetch a package and
reports the refusal.

**Detection.** Every shell command is still recorded to
`results/<run>.cmds.txt` and screened for package installs, downloaders and
anything reaching for PyPI or GitHub. A flagged run is reported as flagged
rather than quietly counted — the screen is verified against known-bad and
known-good commands so it neither misses an install nor trips on
`python -m pytest`.

The limit of this is worth stating plainly: the block is environmental, not a
kernel sandbox. An agent that noticed the proxy variables and unset them could
still reach the network. That is what the screen remains in place to catch, and
why flagged runs are excluded rather than trusted.

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

| Task | Fix size | F2P | P2P | Haiku 4.5 | Sonnet 5 |
|---|---|---:|---:|---|---|
| [click-2940](https://github.com/pallets/click/pull/2940) | +8/-9 | 3 | 12 | ✅ 3/3 | ✅ 3/3 |
| [click-3004](https://github.com/pallets/click/pull/3004) | +2/-0 | 5 | 295 | ✅ 3/3 | ◐ 2/3 ⚠️ |
| [click-3013](https://github.com/pallets/click/pull/3013) | +2/-0 | 1 | 51 | ✅ 3/3 | ✅ 3/3 |
| [click-3021](https://github.com/pallets/click/pull/3021) | +12/-6 | 1 | 142 | ❌ 0/3 | ❌ 0/3 |
| [click-3152](https://github.com/pallets/click/pull/3152) | +6/-3 | 2 | 535 | ✅ 3/3 | ✅ 3/3 |
| [click-3208](https://github.com/pallets/click/pull/3208) | +5/-1 | 3 | 20 | ◐ 2/3 | ✅ 3/3 |
| [click-3225](https://github.com/pallets/click/pull/3225) | +20/-6 | 7 | 577 | ❌ 0/3 ⚠️ | ❌ 0/3 |
| [click-3299](https://github.com/pallets/click/pull/3299) | +1/-1 | 1 | 551 | ✅ 3/3 | ✅ 3/3 |
| [click-3434](https://github.com/pallets/click/pull/3434) | +8/-0 | 7 | 28 | ✅ 3/3 | ✅ 3/3 |
| [click-3484](https://github.com/pallets/click/pull/3484) | +12/-5 | 3 | 680 | ✅ 3/3 | ✅ 3/3 |
| [click-3509](https://github.com/pallets/click/pull/3509) | +3/-2 | 6 | 724 | ✅ 3/3 | ✅ 3/3 |
| [click-3678](https://github.com/pallets/click/pull/3678) | +44/-2 | 10 | 766 | ❌ 0/3 | ❌ 0/3 |
| [click-3805](https://github.com/pallets/click/pull/3805) | +9/-0 | 3 | 7 | ✅ 3/3 | ✅ 3/3 |
| [click-3818](https://github.com/pallets/click/pull/3818) | +52/-24 | 5 | 3 | ❌ 0/3 | ❌ 0/3 |
| [click-3865](https://github.com/pallets/click/pull/3865) | +20/-32 | 6 | 30 | ❌ 0/3 ⚠️ | ❌ 0/3 ⚠️ |
| [click-3884](https://github.com/pallets/click/pull/3884) | +13/-10 | 9 | 667 | ❌ 0/3 | ✅ 3/3 |

✅ solved in every trial · ◐ solved in some trials · ❌ never solved · ⚠️ broke existing tests in at least one trial

**Haiku 4.5** — 60% of 48 attempts resolved · 9 tasks always, 1 sometimes, 6 never · 4 attempts broke existing tests · median 149s
**Sonnet 5** — 67% of 48 attempts resolved · 10 tasks always, 1 sometimes, 5 never · 4 attempts broke existing tests · median 88s

*Of 96 graded runs, 2 edited `tests/` (reverted before grading) and 1 ran a command the screen flagged as reaching for the network (egress was blocked; the attempt failed).*

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
- **Three attempts per task.** Enough to separate "always solves" from
  "sometimes solves", not enough for a confidence interval.
- **A turn budget exists.** Each attempt gets 150 agent turns. The budget is
  reported per run (`turns`, `truncated`) so a failure that merely ran out of
  room is visible rather than silently counted as an inability to solve. An
  earlier 60-turn budget cut off 28% of runs mid-work and was discarded: at
  that cap the distribution of completed runs pressed against the ceiling
  (median 46, max 55), which measures the harness, not the model.
- **Contamination is possible.** These PRs are public and most merged in 2026;
  a model may have seen the fix. Recency lowers the risk, it does not remove it.
- **Environment, not container.** The reported numbers were produced in a
  pinned virtualenv on the host, not inside the supplied image, so they are
  reproducible on a comparable machine rather than bit-for-bit anywhere.
- **The agent's environment is not a developer's.** `PYTHONPATH` points at the
  worktree's `src/` instead of the editable install upstream's contributors
  use. The suite behaves identically, and it is why nothing needs `pip` — but
  it is a deliberate change to the project's normal setup, disclosed here
  rather than left for a reader to find in the code.
- **Void runs are excluded, not counted.** A run the API kills — a 429 session
  limit, a transport error — returns a success-shaped result with zero turns
  of work. Counting that as a failed attempt would understate whichever model
  hit the limit, so such records are marked `void`, dropped from every count,
  and re-run. Eight Sonnet attempts were voided this way and re-run on
  2026-11-18; the table above contains no void records.
- **Timing sensitivity.** A few tasks exercise terminal, pager and interrupt
  behaviour. Those were graded on an unloaded machine; a heavily loaded host
  can turn them flaky in either direction.
- **Only Claude models are measured here.** The harness is model-agnostic —
  `run_task.py` takes any command-line coding agent — but these numbers cover
  the models the author had access to.

## Author

MD Rashed Al Amin — [github.com/Rashed-AlAmin](https://github.com/Rashed-AlAmin)
