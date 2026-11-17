# (DEPRECATED) sits one space further in than everything else

Small thing, but it's showing up in our docs. Our internal admin CLI has a
couple of commands we're phasing out, and the ones we never bothered to write a
docstring for print the deprecation marker misaligned:

```python
import click

@click.group()
def admin():
    """Internal admin tools."""

@admin.command(deprecated=True)
def purge_cache():
    pass
```

```
$ python admin.py purge-cache --help
Usage: admin.py purge-cache [OPTIONS]

   (DEPRECATED)

Options:
  --help  Show this message and exit.
```

Three spaces before `(DEPRECATED)` where everything else in the output is
indented by two. I expected it to line up:

```
  (DEPRECATED)
```

If I give the command a docstring it's fine — `Clear the cache. (DEPRECATED)`
indented normally. So it only looks wrong on the commands that have no
description, which is most of the ones we're deprecating.

Same thing happens on an option where I passed an empty help string:

```python
@click.option("--legacy-mode", help="", deprecated=True)
```

which renders as ` (DEPRECATED)` with a stray space at the front instead of
just `(DEPRECATED)`. We generate our command reference from this output so the
extra space is visible in the published docs.
