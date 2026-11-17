"""Shared test execution. Outcomes come from pytest's JUnit XML, not from
scraping stdout: FAILED lines carry a trailing ' - message' that makes text
parsing ambiguous for parametrised ids containing spaces.
"""
import os, subprocess as sp, tempfile, xml.etree.ElementTree as ET
VENV = os.path.expanduser("~/Desktop/swe-task-bench/.venv/bin/python")

def _nodeid(classname, name, files):
    """Rebuild 'tests/x/y.py::test[param]' from JUnit classname/name."""
    best = ""
    for f in files:
        dotted = f[:-3].replace("/", ".") if f.endswith(".py") else f.replace("/", ".")
        if (classname == dotted or classname.startswith(dotted + ".")) and len(dotted) > len(best):
            best, bestf = dotted, f
    if not best:
        return classname.replace(".", "/") + ".py::" + name
    rest = classname[len(best):].lstrip(".")
    return f"{bestf}::{rest + '::' if rest else ''}{name}"

def run_tests(wt, files):
    """-> (outcomes{nodeid: passed|failed|skipped}, tail_of_stdout)"""
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as fh:
        xml = fh.name
    r = sp.run([VENV, "-m", "pytest", "-p", "no:randomly", "--tb=no", "-q",
                f"--junit-xml={xml}", *files],
               cwd=wt, env={**os.environ, "PYTHONPATH": f"{wt}/src"},
               capture_output=True, text=True)
    out = {}
    try:
        for tc in ET.parse(xml).getroot().iter("testcase"):
            kids = {c.tag for c in tc}
            o = "failed" if kids & {"failure", "error"} else "skipped" if "skipped" in kids else "passed"
            out[_nodeid(tc.get("classname") or "", tc.get("name") or "", files)] = o
    except Exception as e:
        return {}, f"XML PARSE FAILED: {e}\n{r.stdout[-1200:]}"
    finally:
        os.unlink(xml)
    return out, r.stdout[-1200:]
