# qa-01 — a judge-graded codebase question

Every other task in this repo is a patch task: the agent edits the tree and a
pytest run decides the outcome. This one asks for an explanation instead, and
a rubric decides the outcome.

## The question

`instruction.md` hands the agent a situation, not a bug report. An empty
`prompt_suffix` still leaves a trailing byte; with `err=True` that byte turns up
on stdout while the rest of the prompt goes to stderr; and varying the suffix or
padding the prompt text changes nothing. The question deliberately names no
file, no function and no identifier, and avoids the word that is the answer, so
the agent has to find the mechanism rather than pattern-match on it.

## Why it is here

The mechanism cannot be read off the source. The function that builds the
prompt handles the suffix correctly, and the line that looks guilty — the one
stripping trailing spaces — is not the one responsible. The byte comes from a
hard-coded argument handed to the line-reading function, which prints it itself
and therefore never consults click's stream selection. An agent that reads and
reasons gets a confident, wrong answer; an agent that runs the code with the
streams captured separately sees it immediately.

This is not a guess about difficulty. The same defect appears in this repo as
[`click-3021`](../click-3021), the patch-task form, where Haiku 4.5 and Sonnet 5
each failed 0/3. All six attempts localised the right line and then proposed the
same wrong repair, and none of the six ever mentioned the stream split.

## How the rubrics map onto tests

The two rubric files play the roles the two test sets play elsewhere:

| patch task | this task |
|---|---|
| fail-to-pass tests | `rubric/positive.toml` — 10 criteria the answer must satisfy |
| pass-to-pass tests | `rubric/negative.toml` — 5 wrong claims that disqualify it |

Positive rows are the thing the task exists to measure: each states a mechanism
and cites the lines that establish it, then gives an explicit PASS/FAIL pair, so
a row can be checked without re-deriving the answer. Negative rows carry
`negate = true` and are written in the positive — the judge decides whether a
bad claim is *present*, and the score is flipped. They are not invented: each
one is a claim that actually appeared in the recorded attempts. The row that
catches the universal failure (treating "pass an empty string instead" as a
complete account, when an empty argument silently removes the workaround the
byte exists to provide) carries the heaviest weight.

Two negative rows carry explicit scope notes, which fence off the adjacent
*correct* statement so a right answer cannot trip them — for instance, saying
the suffix's trailing spaces are unrecoverable downstream is correct and must
not be read as "the suffix is dropped at construction".

`golden.md` is the reference answer: it satisfies all 10 positive rows and trips
none of the 5 negative ones. It is also what the rubrics were drafted against,
so it doubles as the calibration check — if a row cannot be confirmed against
the golden answer, the row is wrong.

## Limitation

A rubric is softer than a test suite, and this should be said plainly. Pytest
gives a bit; a judge gives a judgement, and judgements drift between models,
between runs, and with how the answer is worded. A verbose answer can satisfy a
row by accident, and a terse correct one can miss a row it implicitly covers.
The citation requirements and the runtime-evidence row narrow that gap — an
answer either shows executed output with the streams apart or it does not — but
they do not close it. Treat a score here as weaker evidence than a green test
run on `click-3021`, and read the answers.

## Files

- `instruction.md` — the question put to the agent
- `rubric/positive.toml` — 10 weighted criteria
- `rubric/negative.toml` — 5 criteria, all `negate = true`
- `golden.md` — reference answer
- `task.toml` — metadata, base commit, failure mode
