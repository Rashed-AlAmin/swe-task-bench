#!/usr/bin/env bash
# sweep.sh <model> [parallelism] [trials] — run every task, k trials each.
ROOT=/home/rashed-al-amin/Desktop/swe-task-bench; MODEL=$1; N=${2:-3}; K=${3:-3}
cd $ROOT
for t in $(seq 1 $K); do
  for pr in 3299 3013 3004 3509 3208 3152 3434 2940 3805 3484 3021 3884 3225 3678 3818 3865; do
    [ -f tasks/click-$pr/problem.md ] || continue
    [ -f results/click-${pr}__${MODEL}__t${t}.json ] && continue
    echo "$pr $t"
  done
done | xargs -P $N -L1 sh -c 'timeout 1800 '"$ROOT"'/.venv/bin/python '"$ROOT"'/scripts/run_task.py $0 '"$MODEL"' $1 >> '"$ROOT"'/results/sweep-'"$MODEL"'.log 2>&1; echo "done $0 t$1"'
