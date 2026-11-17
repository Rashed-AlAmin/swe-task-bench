"""Contamination screen for candidate shell commands.

The candidate is allowed to build and test the code in front of it. What it
must not do is obtain a *different*, already-fixed copy of the library. So
`pip install -e .` is benign (it installs the local, still-buggy source) while
`pip install click`, any downloader, and any reach for PyPI/GitHub are not.
"""
import re

URL = re.compile(r"pypi\.org|files\.pythonhosted|github\.com|githubusercontent|"
                 r"https?://(?!localhost|127\.)", re.I)
GETTER = re.compile(r"\b(curl|wget|aria2c)\b", re.I)
VCS = re.compile(r"\bgit\s+(clone|fetch|pull|remote\s+add)\b", re.I)
INSTALL = re.compile(r"\b(?:pip3?|pipx|poetry|uv)\b(?:\s+pip)?\s+(install|download|add)\b", re.I)
LOCAL = re.compile(r"^(\.|\./|/|\$PWD|~)|^\.\[")   # '.', './x', absolute path, extras on '.'

def _segments(cmd):
    """A command line is many commands; screen each one separately."""
    return [seg for seg in re.split(r"&&|\|\||[;|\n]", cmd) if seg.strip()]

def _install_targets(seg):
    """Package names in one install command, ignoring flags and local paths."""
    m = INSTALL.search(seg)
    if not m: return []
    rest = re.sub(r"\d*[<>]+&?\S*", " ", seg[m.end():])   # drop 2>&1, >log
    out = []
    for tok in rest.split():
        if tok.startswith("-"): continue          # flags, including -e
        if LOCAL.match(tok): continue             # the local project
        if tok in ("install", "download", "add"): continue
        out.append(tok)
    return out

def flag_for(cmd):
    """-> reason string if the command could obtain an already-fixed copy."""
    for seg in _segments(cmd):
        if URL.search(seg):    return "reaches an external source"
        if GETTER.search(seg): return "downloader"
        if VCS.search(seg):    return "fetches external git history"
        tg = _install_targets(seg)
        if tg:                 return f"installs non-local package(s): {' '.join(tg[:3])}"
    return None
