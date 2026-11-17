# Error message tells me to run something that then errors

Our deploy tool enables `-h` as a help alias at the top level, and one of the
subcommands uses `-h` as the short form of `--host`:

```python
import click

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def deployctl():
    pass

@deployctl.command()
@click.option("-h", "--host", default="localhost")
@click.argument("service")
def restart(host, service):
    click.echo(f"restarting {service} on {host}")
```

If I forget the argument:

```
$ python deployctl.py restart
Usage: deployctl.py restart [OPTIONS] SERVICE
Try 'deployctl.py restart -h' for help.

Error: Missing argument 'SERVICE'.
```

So I do what it says, and get another error instead of help:

```
$ python deployctl.py restart -h
Usage: deployctl.py restart [OPTIONS] SERVICE
Try 'deployctl.py restart -h' for help.

Error: Option '-h' requires an argument.
```

Which is a nice little loop. `--help` still works on that subcommand, so I'd
expect the suggestion to say `--help` there, since `-h` has clearly been taken
over by my own option. Our users keep pasting the suggested command into
tickets saying the CLI is broken.

Even on subcommands that don't define `-h`, the suggestion is always the short
one, which is a bit cryptic when you're reading it cold.
