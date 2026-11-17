#!/usr/bin/env bash
# sweep.sh <model> [parallelism] — run every task that has a problem statement.
ROOT=/home/rashed-al-amin/Desktop/swe-task-bench; MODEL=$1; N=${2:-3}
cd $ROOT
for pr in 3299 3013 3004 3509 3208 3152 3434 2940 3805 3484 3021 3884 3225 3678 3818 3865; do
  [ -f tasks/click-$pr/problem.md ] || continue
  [ -f results/click-${pr}__${MODEL}.json ] && continue
  echo "$pr"
done | xargs -P $N -I{} sh -c "timeout 1800 $ROOT/.venv/bin/python $ROOT/scripts/run_task.py {} $MODEL >> $ROOT/results/sweep-$MODEL.log 2>&1; echo done {}"
