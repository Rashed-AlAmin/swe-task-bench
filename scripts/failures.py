#!/usr/bin/env python3
"""failures.py — what failed, and whether the task or the model is at fault.

A task no model ever solves is only interesting if it is hard. If the problem
statement simply left out what was needed, that is an authoring defect and the
task should be rewritten or dropped. This prints the evidence to judge which.
"""
import collections, glob, json, os, sys
ROOT = os.path.expanduser("~/Desktop/swe-task-bench")
runs = collections.defaultdict(list)
for f in glob.glob(f"{ROOT}/results/click-*.json"):
    r = json.load(open(f)); runs[r["pr"]].append(r)
for pr in sorted(runs):
    rs = runs[pr]; n = sum(1 for r in rs if r["resolved"])
    tag = "ALWAYS" if n == len(rs) else ("NEVER" if n == 0 else "SPLIT")
    gold = open(f"{ROOT}/tasks/click-{pr}/gold.patch").read()
    adds = sum(1 for l in gold.splitlines() if l.startswith("+") and not l.startswith("+++"))
    print(f"\n=== click-{pr}  {tag}  {n}/{len(rs)} resolved  gold=+{adds}")
    for r in sorted(rs, key=lambda r: (r["model"], r.get("trial", 0))):
        flags = r.get("contamination_flags") or []
        print(f"    {r['model'][:28]:28} t{r.get('trial','?')} "
              f"{'OK  ' if r['resolved'] else 'FAIL'} "
              f"f2p={r['f2p_passed']}/{r['f2p_total']} p2p_broken={r['p2p_broken']} "
              f"diff={r['diff_lines']}L shell={r.get('shell_calls','?')}"
              + (f"  FLAGGED:{flags[:1]}" if flags else ""))
    if tag == "NEVER" and "--diffs" in sys.argv:
        d = sorted(glob.glob(f"{ROOT}/results/click-{pr}__*.diff"))
        if d: print("    --- one attempt ---"); print("".join("    "+l for l in open(d[0]).read().splitlines(True)[:30]))
