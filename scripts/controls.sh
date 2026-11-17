#!/usr/bin/env bash
# Sanity controls: the grader MUST say not-resolved for an untouched tree,
# and resolved for the official fix. Anything else means the task is broken.
set -uo pipefail
ROOT=~/Desktop/swe-task-bench; REPO=$ROOT/repo; PR=$1; T=$ROOT/tasks/click-$PR
BASE=$(python3 -c "import json;print(json.load(open('$T/task.json'))['base_commit'])")
for mode in null gold; do
  WT=$ROOT/work/ctl-$PR-$mode
  git -C $REPO worktree remove --force $WT >/dev/null 2>&1; rm -rf $WT
  git -C $REPO worktree add --detach $WT $BASE >/dev/null 2>&1
  [ $mode = gold ] && git -C $WT apply $T/gold.patch
  printf '%s %-5s %s\n' "$PR" "$mode" "$($ROOT/.venv/bin/python $ROOT/scripts/grade.py $WT $T)"
  git -C $REPO worktree remove --force $WT >/dev/null 2>&1
done
