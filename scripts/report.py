#!/usr/bin/env python3
"""report.py — aggregate results/*.json into the markdown results section.
Each (task, model) pair is run k times; a cell shows how many trials resolved.
"""
import glob, json, os, collections, statistics
ROOT = os.path.expanduser("~/Desktop/swe-task-bench")
SHORT = {"claude-haiku-4-5-20251001":"Haiku 4.5","claude-sonnet-5":"Sonnet 5","claude-opus-5":"Opus 5"}
runs = collections.defaultdict(list)
for f in glob.glob(f"{ROOT}/results/click-*.json"):
    r = json.load(open(f)); runs[(r["pr"], r["model"])].append(r)
models = [m for m in SHORT if any(k[1]==m for k in runs)]
prs = sorted({k[0] for k in runs})
tasks = {int(os.path.basename(d).split("-")[1]): json.load(open(f"{d}/task.json"))
         for d in glob.glob(f"{ROOT}/tasks/click-*") if os.path.exists(f"{d}/task.json")}

def cell(rs):
    if not rs: return "—"
    n = sum(1 for r in rs if r["resolved"]); k = len(rs)
    mark = "✅" if n==k else ("❌" if n==0 else "◐")
    reg = " ⚠️" if any(r.get("p2p_broken") for r in rs) else ""
    return f"{mark} {n}/{k}{reg}"

lines = ["| Task | Fix size | F2P | P2P | " + " | ".join(SHORT[m] for m in models) + " |",
         "|---|---|---:|---:|" + "---|"*len(models)]
for pr in prs:
    t = tasks.get(pr, {}); g = open(f"{ROOT}/tasks/click-{pr}/gold.patch").read()
    adds = sum(1 for l in g.splitlines() if l.startswith("+") and not l.startswith("+++"))
    dels = sum(1 for l in g.splitlines() if l.startswith("-") and not l.startswith("---"))
    cells = " | ".join(cell(runs.get((pr,m), [])) for m in models)
    lines.append(f"| [click-{pr}](https://github.com/pallets/click/pull/{pr}) | +{adds}/-{dels} | "
                 f"{t.get('n_f2p',0)} | {t.get('n_p2p',0)} | {cells} |")
lines.append("")
lines.append("✅ solved in every trial · ◐ solved in some trials · ❌ never solved · ⚠️ broke existing tests in at least one trial")
lines.append("")
for m in models:
    rs = [r for k,v in runs.items() if k[1]==m for r in v]
    pairs = [v for k,v in runs.items() if k[1]==m]
    always = sum(1 for v in pairs if all(r["resolved"] for r in v))
    never  = sum(1 for v in pairs if not any(r["resolved"] for r in v))
    flaky  = len(pairs) - always - never
    rate   = sum(1 for r in rs if r["resolved"]) / len(rs) * 100 if rs else 0
    reg    = sum(1 for r in rs if r.get("p2p_broken"))
    lines.append(f"**{SHORT[m]}** — {rate:.0f}% of {len(rs)} attempts resolved · "
                 f"{always} tasks always, {flaky} sometimes, {never} never · "
                 f"{reg} attempts broke existing tests · median {statistics.median([r['elapsed_s'] for r in rs]):.0f}s")
out = "\n".join(lines)
print(out)
rp = f"{ROOT}/README.md"; s = open(rp).read()
if "<!--RESULTS-->" in s:
    import re
    s = re.sub(r"<!--RESULTS-->.*?(?=\n---\n\n## Reproducing)", "<!--RESULTS-->\n\n"+out+"\n", s, flags=re.S)
    open(rp,"w").write(s)
