#!/usr/bin/env python3
"""verify.py <PR#> [--keep]
Checks out the base commit, applies test.patch, runs the touched test files
BEFORE and AFTER the gold patch, and records which tests flip fail->pass
(fail_to_pass) and which pass throughout (pass_to_pass).
"""
import json, os, re, shutil, subprocess as sp, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runner import run_tests
ROOT = os.path.expanduser("~/Desktop/swe-task-bench"); REPO = f"{ROOT}/repo"

def run(cmd, cwd=None, check=True):
    r = sp.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode: raise SystemExit(f"FAILED {cmd}\n{r.stdout}\n{r.stderr}")
    return r

def touched(p):
    return sorted(set(re.findall(r"^\+\+\+ b/(\S+)", open(p).read(), re.M)))

def main():
    pr = sys.argv[1]; T = f"{ROOT}/tasks/click-{pr}"
    meta = json.load(open(f"{T}/meta.json")); base = meta["base_commit"]
    wt = f"{ROOT}/work/click-{pr}"
    run(["git","worktree","remove","--force",wt], REPO, check=False); shutil.rmtree(wt, ignore_errors=True)
    run(["git","worktree","add","--detach",wt,base], REPO)
    tfiles = touched(f"{T}/test.patch")
    run(["git","apply",f"{T}/test.patch"], wt)
    pre, pre_log = run_tests(wt, tfiles)
    run(["git","apply",f"{T}/gold.patch"], wt)
    post, post_log = run_tests(wt, tfiles)
    f2p = sorted(i for i,o in post.items() if o=="passed" and pre.get(i)=="failed")
    p2p = sorted(i for i,o in post.items() if o=="passed" and pre.get(i)=="passed")
    broken = sorted(i for i,o in post.items() if o=="failed")
    out = {**meta, "test_files": tfiles, "fail_to_pass": f2p, "pass_to_pass": p2p,
           "broken_after_gold": broken, "n_f2p": len(f2p), "n_p2p": len(p2p)}
    json.dump(out, open(f"{T}/task.json","w"), indent=2)
    print(f"PR {pr}: F2P={len(f2p)} P2P={len(p2p)} still-failing-after-gold={len(broken)}")
    if not f2p: print("  !! NO fail-to-pass — unusable\n ", post_log[-400:].replace("\n"," ")[:300])
    if broken: print("  !! broken after gold:", broken[:3])
    if "--keep" not in sys.argv:
        run(["git","worktree","remove","--force",wt], REPO, check=False)
main()
