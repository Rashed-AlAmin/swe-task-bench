#!/usr/bin/env python3
"""run_task.py <PR#> <model> [trial]  — give one task to one model, then grade it.
The model gets the repo at the base commit plus the problem statement only.
The new tests are applied afterwards, by grade.py, and are never visible to it.
"""
import fcntl, json, os, re, shutil, subprocess as sp, sys, time
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
    trial = sys.argv[3] if len(sys.argv) > 3 else "1"
    T, slug = f"{ROOT}/tasks/click-{pr}", f"click-{pr}__{model}__t{trial}"
    task = json.load(open(f"{T}/task.json"))
    wt = f"{ROOT}/work/{slug}"
    # A git worktree shares the upstream object database, so a candidate could
    # run `git log --all --grep=...` and read the very fix it is being asked to
    # write. Export a history-free snapshot instead and re-init it, so `git
    # diff` still works but the future of the project does not exist.
    shutil.rmtree(wt, ignore_errors=True); os.makedirs(wt)
    with _WtLock():
        tar = sp.run(["git","archive",task["base_commit"]], cwd=REPO, capture_output=True, check=True)
    sp.run(["tar","-x","-C",wt], input=tar.stdout, check=True)
    sh(["git","init","-q"], wt, check=True)
    sh(["git","add","-A"], wt, check=True)
    sh(["git","-c","user.email=bench@local","-c","user.name=bench",
        "commit","-q","-m","base"], wt, check=True)
    problem = open(f"{T}/problem.md").read()
    t0 = time.time()
    r = sh(["claude","-p",PROMPT.format(problem=problem),"--model",model,
            "--permission-mode","acceptEdits","--max-turns","60",
            "--output-format","stream-json","--verbose",
            "--allowedTools","Read","Edit","Write","Grep","Glob","Bash"], cwd=wt, timeout=1800)
    elapsed = round(time.time()-t0, 1)
    os.makedirs(f"{ROOT}/results", exist_ok=True)
    open(f"{ROOT}/results/{slug}.jsonl","w").write(r.stdout)
    # The candidate has a shell. Nothing stops it fetching a released copy of
    # the library that already contains the fix, so every shell command it ran
    # is recorded and screened; a flagged run is reported, never silently kept.
    suspect, ncalls, cmdlog = [], 0, []
    for line in r.stdout.splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "assistant": continue
        for c in d.get("message", {}).get("content", []):
            if c.get("type") != "tool_use": continue
            if c["name"] in ("WebFetch", "WebSearch"):
                suspect.append(f'{c["name"]}:{json.dumps(c.get("input"))[:120]}'); continue
            if c["name"] != "Bash": continue
            cmd = (c.get("input") or {}).get("command", ""); ncalls += 1
            cmdlog.append(cmd.replace("\n", " ⏎ ")[:300])
            if re.search(r"\b(pip3?|uv|poetry|pipx)\b.*\b(install|download|add)\b|curl|wget|"
                         r"git\s+(clone|fetch|pull|remote)|pypi\.org|files\.pythonhosted|"
                         r"github\.com|raw\.githubusercontent", cmd):
                suspect.append(f"Bash:{cmd[:160]}")
    open(f"{ROOT}/results/{slug}.cmds.txt","w").write("\n".join(cmdlog))
    diff = sh(["git","diff"], wt).stdout
    g = sh([VENV, f"{ROOT}/scripts/grade.py", wt, T])
    if r.returncode != 0:
        print(f"  (agent exited {r.returncode}: {r.stderr[-200:]})", file=sys.stderr)
    try: verdict = json.loads(g.stdout.strip().splitlines()[-1])
    except Exception: verdict = {"resolved": False, "error": "grader crashed", "raw": g.stdout[-400:] + g.stderr[-400:]}
    rec = {"pr": int(pr), "model": model, "trial": int(trial), "title": task["title"], "elapsed_s": elapsed,
           "agent_exit": r.returncode, "diff_lines": len(diff.splitlines()),
           "shell_calls": ncalls, "contamination_flags": suspect, **verdict}
    json.dump(rec, open(f"{ROOT}/results/{slug}.json","w"), indent=2)
    open(f"{ROOT}/results/{slug}.diff","w").write(diff)
    print(json.dumps(rec))
    shutil.rmtree(wt, ignore_errors=True)
main()
