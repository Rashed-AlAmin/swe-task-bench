# Help output starts with a blank line where the usage line should be

I maintain an internal admin CLI at work. A couple of my subcommands take nothing at all, and `[OPTIONS]` showing up for them confused people on my team, so I passed an empty `options_metavar` to hide it.

```python
import click

@click.group()
def admin():
    """Cluster admin tools."""

@admin.command(options_metavar="")
def status():
    """Show cluster status."""
    click.echo("ok")

if __name__ == "__main__":
    admin()
```

Now the help for that subcommand has lost its first line:

```
$ python admin.py status --help

  Show cluster status.

```

The very first line is just empty. I was expecting:

```
Usage: admin.py status

  Show cluster status.
```

Passing `options_metavar=None` does exactly the same thing. If I give the command even one option back, the usage line shows up fine, so it only goes wrong when there's genuinely nothing to list after the program name. Our help-output snapshot tests all fail on this now and I can't work out what I did wrong.
