#!/usr/bin/env bash
ROOT=/home/rashed-al-amin/Desktop/swe-task-bench; cd $ROOT
./scripts/sweep.sh claude-haiku-4-5-20251001 3 3
echo "HAIKU DONE"
./scripts/sweep.sh claude-sonnet-5 3 3
echo "CHAIN DONE"
