# `--help` blows up with a traceback when I turn on show_default

I'm building an internal release CLI. One of the options takes a small version
object we wrote ourselves, which deliberately refuses to be compared against
anything that isn't another version:

```python
import click

class Semver:
    def __init__(self, major, minor, patch):
        self.parts = (major, minor, patch)

    def __eq__(self, other):
        if type(other) is not Semver:
            raise TypeError("Semver can only be compared to Semver")
        return self.parts == other.parts

    def __str__(self):
        return ".".join(f"{p}" for p in self.parts)

@click.command()
@click.option("--min-version", default=Semver(1, 2, 0), show_default=True)
def release(min_version):
    click.echo(f"releasing above {min_version}")
```

Running it normally is fine:

```
$ python release.py
releasing above 1.2.0
```

But asking for help explodes:

```
$ python release.py --help
Traceback (most recent call last):
  ...
TypeError: Semver can only be compared to Semver
```

I expected the usual help page with `[default: 1.2.0]` in it. If I drop
`show_default=True` the help page renders fine, so something about printing the
default is poking at my object in a way I didn't expect. I know my `__eq__` is
strict, but it's strict on purpose and nothing else in our codebase trips over
it. Is `--help` supposed to require that defaults compare cleanly against
anything?
