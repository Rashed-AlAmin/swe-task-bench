#!/usr/bin/env bash
# Sanity controls. The grader MUST report:
#   null  -> not resolved  (an untouched tree fixes nothing)
#   gold  -> resolved      (the maintainers' own patch is correct)
#   cheat -> not resolved  (deleting the tests must not look like success)
# A task that fails any of the three is a broken ruler and does not ship.
set -uo pipefail
ROOT=~/Desktop/swe-task-bench; REPO=$ROOT/repo; PR=$1; T=$ROOT/tasks/click-$PR
BASE=$(python3 -c "import json;print(json.load(open('$T/task.json'))['base_commit'])")
for mode in null gold cheat; do
  WT=$ROOT/work/ctl-$PR-$mode
  git -C $REPO worktree remove --force $WT >/dev/null 2>&1; rm -rf $WT
  git -C $REPO worktree add --detach $WT $BASE >/dev/null 2>&1
  [ $mode = gold ] && git -C $WT apply $T/gold.patch
  if [ $mode = cheat ]; then
    # Simulate the laziest cheat: wipe the tests and leave a stub that passes.
    for f in $(python3 -c "import json;print(' '.join(json.load(open('$T/task.json'))['test_files']))"); do
      mkdir -p "$(dirname $WT/$f)"; printf 'def test_ok():\n    assert True\n' > $WT/$f
    done
  fi
  printf '%s %-5s %s\n' "$PR" "$mode" "$($ROOT/.venv/bin/python $ROOT/scripts/grade.py $WT $T)"
  git -C $REPO worktree remove --force $WT >/dev/null 2>&1
done
