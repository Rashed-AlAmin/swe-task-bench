#!/usr/bin/env python3
"""run_task.py <PR#> <model>  — give one task to one model, then grade it.
The model gets the repo at the base commit plus the problem statement only.
The new tests are applied afterwards, by grade.py, and are never visible to it.
"""
import fcntl, json, os, shutil, subprocess as sp, sys, time
ROOT = os.path.expanduser("~/Desktop/swe-task-bench")
REPO, VENV = f"{ROOT}/repo", f"{ROOT}/.venv/bin/python"
PROMPT = """You are fixing a bug in this Python repository (the `click` library).
A user has filed the following report:

--- BEGIN REPORT ---
{problem}
--- END REPORT ---

Reproduce and fix the underlying bug by editing the library source under `src/`.

Rules:
- Do NOT modify anything under `tests/`. Your change is graded by tests you cannot see.
- Do not disable, skip or weaken any existing behaviour to make the symptom go away.
- Keep the fix minimal and correct for the general case, not just the exact example shown.
When you are done, stop. Do not ask questions."""

class _WtLock:
    """git worktree add/remove mutate shared .git metadata; serialise them."""
    def __enter__(self):
        self.f = open(f"{ROOT}/work/.wt.lock", "w"); fcntl.flock(self.f, fcntl.LOCK_EX); return self
    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()

def sh(cmd, cwd=None, check=False, **kw):
    r = sp.run(cmd, cwd=cwd, capture_output=True, text=True, **kw)
    if check and r.returncode: raise SystemExit(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r

def main():
    pr, model = sys.argv[1], sys.argv[2]
    T, slug = f"{ROOT}/tasks/click-{pr}", f"click-{pr}__{model}"
    task = json.load(open(f"{T}/task.json"))
    wt = f"{ROOT}/work/{slug}"
    with _WtLock():
        sh(["git","worktree","remove","--force",wt], REPO); shutil.rmtree(wt, ignore_errors=True)
        sh(["git","worktree","add","--detach",wt,task["base_commit"]], REPO, check=True)
    problem = open(f"{T}/problem.md").read()
    t0 = time.time()
    r = sh(["claude","-p",PROMPT.format(problem=problem),"--model",model,
            "--permission-mode","acceptEdits","--max-turns","60",
            "--allowedTools","Read","Edit","Write","Grep","Glob","Bash"], cwd=wt, timeout=1800)
    elapsed = round(time.time()-t0, 1)
    diff = sh(["git","diff"], wt).stdout
    g = sh([VENV, f"{ROOT}/scripts/grade.py", wt, T])
    if r.returncode != 0:
        print(f"  (agent exited {r.returncode}: {r.stderr[-200:]})", file=sys.stderr)
    try: verdict = json.loads(g.stdout.strip().splitlines()[-1])
    except Exception: verdict = {"resolved": False, "error": "grader crashed", "raw": g.stdout[-400:] + g.stderr[-400:]}
    os.makedirs(f"{ROOT}/results", exist_ok=True)
    rec = {"pr": int(pr), "model": model, "title": task["title"], "elapsed_s": elapsed,
           "agent_exit": r.returncode, "diff_lines": len(diff.splitlines()), **verdict}
    json.dump(rec, open(f"{ROOT}/results/{slug}.json","w"), indent=2)
    open(f"{ROOT}/results/{slug}.diff","w").write(diff)
    print(json.dumps(rec))
    with _WtLock():
        sh(["git","worktree","remove","--force",wt], REPO)
main()
