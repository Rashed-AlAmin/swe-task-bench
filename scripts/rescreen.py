#!/usr/bin/env python3
"""rescreen.py — recompute contamination flags for recorded runs.
Because every shell command was logged, the screen can be corrected and
re-applied without spending a single new model call.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screen import flag_for
ROOT = os.path.expanduser("~/Desktop/swe-task-bench")
changed = 0
for jf in sorted(glob.glob(f"{ROOT}/results/click-*.json")):
    cf = jf[:-5] + ".cmds.txt"
    if not os.path.exists(cf): continue
    rec = json.load(open(jf))
    flags = [f"{flag_for(c)} :: {c[:160]}" for c in open(cf).read().splitlines() if c.strip() and flag_for(c)]
    if flags != rec.get("contamination_flags"):
        rec["contamination_flags"] = flags; json.dump(rec, open(jf,"w"), indent=2); changed += 1
print(f"rescreened {len(glob.glob(f'{ROOT}/results/click-*.json'))} runs, updated {changed}")
