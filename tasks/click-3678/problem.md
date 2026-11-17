# An argument called "help" makes my command reject its own input as "not a valid boolean"

Our internal docs CLI has a command that takes the topic to print. The natural
name for it was `help` (as in `docs help networking`), so:

```python
import click

@click.command()
@click.argument("help")
def docs(help):
    """Print the internal docs for a topic."""
    click.echo(f"showing docs for {help}")

if __name__ == "__main__":
    docs()
```

```
$ python docs.py networking
Usage: docs.py [OPTIONS] HELP
Try 'docs.py --help' for help.

Error: Invalid value for '--help': 'networking' is not a valid boolean.
```

I expected `showing docs for networking`. I never declared anything called
`--help` myself, and the usage line it prints even shows `HELP` as a positional
argument, so it clearly knows about my argument — it just refuses to take a
value for it and complains about a `--help` I didn't write.

I hit the same wall going the other way: I tried renaming the flag to dodge it,

```python
@click.option("--assist", "help")
```

and `python docs.py --assist networking` fails with the identical "not a valid
boolean" error. Renaming the variable to `topic` makes everything work, but
that reads worse and I don't understand why one particular name is off limits.
