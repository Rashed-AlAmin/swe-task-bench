# Command summaries get chopped off halfway

I'm building an internal reporting CLI and a couple of my command summaries
come out truncated in the group listing, in a way I can't explain.

```python
import click

@click.group()
def reports():
    pass

@reports.command()
def compare():
    """Weigh apples vs. pears before the quarterly roll-up."""

@reports.command()
def ingest():
    """Load the feed. retries are automatic and logged."""
```

```
$ python reports.py --help
...
Commands:
  compare  Weigh apples vs.
  ingest   Load the feed.
```

I expected `compare` to show the whole summary — there's plenty of room on the
line, and other commands with longer docstrings show in full. It stops dead at
`vs.` every time. Same thing with `e.g.` and `i.e.`, which I use a lot.

`ingest` is the opposite problem in a way: what follows the dot is clearly a
continuation of the same thought, but it still gets treated as a hard stop.

If the summary genuinely is too long for the terminal I'd expect it to be cut
with a trailing `...` so I can tell something was dropped. Right now a chopped
summary reads as if it were the whole thing, which is worse — I spent an hour
thinking my docstring was wrong.
