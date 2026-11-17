#!/usr/bin/env python3
"""report.py — aggregate results/*.json into a markdown table."""
import glob, json, os, collections
ROOT = os.path.expanduser("~/Desktop/swe-task-bench")
SHORT = {"claude-haiku-4-5-20251001":"Haiku 4.5","claude-sonnet-5":"Sonnet 5","claude-opus-5":"Opus 5"}
res = collections.defaultdict(dict)
for f in glob.glob(f"{ROOT}/results/*.json"):
    r = json.load(open(f)); res[r["pr"]][r["model"]] = r
models = [m for m in SHORT if any(m in v for v in res.values())]
tasks = {int(os.path.basename(d).split("-")[1]): json.load(open(f"{d}/task.json"))
         for d in glob.glob(f"{ROOT}/tasks/click-*") if os.path.exists(f"{d}/task.json")}
rows=[]
for pr in sorted(res):
    t = tasks.get(pr, {})
    gold = sum(1 for _ in open(f"{ROOT}/tasks/click-{pr}/gold.patch") )
    cells = []
    for m in models:
        r = res[pr].get(m)
        cells.append("—" if not r else ("✅" if r["resolved"] else
                     f'❌ {r["f2p_passed"]}/{r["f2p_total"]}' + (" ⚠️regress" if r["p2p_broken"] else "")))
    rows.append((pr, t.get("n_f2p",0), t.get("n_p2p",0), cells))
hdr = "| Task | F2P | P2P | " + " | ".join(SHORT[m] for m in models) + " |"
sep = "|---|---:|---:|" + "---|"*len(models)
print(hdr); print(sep)
for pr,f,p,cells in rows:
    print(f"| [click-{pr}](https://github.com/pallets/click/pull/{pr}) | {f} | {p} | " + " | ".join(cells) + " |")
print()
for m in models:
    done = [res[pr][m] for pr in res if m in res[pr]]
    solved = sum(1 for r in done if r["resolved"])
    regress = sum(1 for r in done if r.get("p2p_broken"))
    avg = round(sum(r["elapsed_s"] for r in done)/len(done),1) if done else 0
    print(f"**{SHORT[m]}**: {solved}/{len(done)} resolved · {regress} runs broke existing tests · avg {avg}s")
