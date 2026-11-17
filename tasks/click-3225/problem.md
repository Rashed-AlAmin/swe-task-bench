# My flag hands me an object when I didn't pass the flag, but the class when I did

I'm building an exporter for our analytics dumps. The flags pick which writer
class to use, and I construct the writer myself afterwards with a path and a
batch size:

```python
import click

class JsonWriter:
    """Takes a path, writes rows to it."""

@click.command()
@click.option("--json", "writer", flag_value=JsonWriter,
              type=click.UNPROCESSED, default=True)
def export(writer):
    click.echo(repr(writer))

if __name__ == "__main__":
    export()
```

```
$ python export.py --json
<class '__main__.JsonWriter'>

$ python export.py
<__main__.JsonWriter object at 0x7f3c1a2b4d90>
```

Both runs should give me `<class '__main__.JsonWriter'>` — it's the same flag
with the same value, I just didn't type it the second time. Instead, when I
leave the flag off I get an already built object, so my `writer(path=...)` call
blows up with "object is not callable".

It's worse for our CSV writer, whose constructor requires a delimiter: running
the command with no flags at all dies with a `TypeError` from inside that
constructor before my function ever runs.

Also, with `show_default=True` the help screen prints the memory address
instead of the class name, which looks pretty odd in `--help` output.
