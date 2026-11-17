#!/usr/bin/env bash
ROOT=/home/rashed-al-amin/Desktop/swe-task-bench; cd $ROOT
# wait out any in-flight haiku sweep
while pgrep -f "sweep.sh claude-haiku" >/dev/null; do sleep 15; done
./scripts/sweep.sh claude-haiku-4-5-20251001 3   # picks up 3865, skips done
./scripts/sweep.sh claude-sonnet-5 3
echo "CHAIN DONE"
