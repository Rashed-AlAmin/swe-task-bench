#!/usr/bin/env python3
"""grade.py <worktree> <task_dir>  -> JSON verdict.
SWE-bench protocol: the candidate NEVER sees the tests. We discard any edits the
candidate made under tests/, apply the official test patch, then run F2P + P2P.
Resolved = every fail_to_pass passes AND every pass_to_pass still passes.
"""
import json, os, re, subprocess as sp, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runner import run_tests

def sh(cmd, cwd, env=None, check=False):
    e = dict(os.environ); e.update(env or {})
    return sp.run(cmd, cwd=cwd, env=e, capture_output=True, text=True)

def main():
    wt, T = sys.argv[1], sys.argv[2]
    task = json.load(open(f"{T}/task.json"))
    # anti-cheat: candidate edits to tests are discarded outright
    tampered = sh(["git","status","--porcelain","--","tests"], wt).stdout.strip()
    sh(["git","checkout","--","tests"], wt); sh(["git","clean","-fd","tests"], wt)
    ap = sh(["git","apply",f"{T}/test.patch"], wt)
    if ap.returncode != 0:
        print(json.dumps({"resolved":False,"error":"test patch did not apply","stderr":ap.stderr[-500:]})); return
    status, _log = run_tests(wt, task["test_files"])
    ok = lambda i: status.get(i) == "passed"
    f2p_pass = [i for i in task["fail_to_pass"] if ok(i)]
    p2p_fail = [i for i in task["pass_to_pass"] if not ok(i)]
    resolved = len(f2p_pass) == len(task["fail_to_pass"]) and not p2p_fail
    print(json.dumps({"resolved": resolved, "f2p_passed": len(f2p_pass),
        "f2p_total": len(task["fail_to_pass"]), "p2p_broken": len(p2p_fail),
        "p2p_total": len(task["pass_to_pass"]), "tampered_with_tests": bool(tampered),
        "p2p_broken_ids": p2p_fail[:5]}))
main()
