# Fish gives me zero completions as soon as I type an opening quote

I have a data importer CLI and the dataset names it completes have spaces in
them, so I end up quoting them while typing.

```python
import click

DATASETS = ["Sales Q1", "Sales Q2", "backfill"]

def complete_dataset(ctx, param, value):
    return [d for d in DATASETS if d.startswith(value)]

@click.command()
@click.option("--dataset", shell_complete=complete_dataset)
def importer(dataset):
    click.echo(f"loading {dataset}")
```

Completion is installed in fish the documented way:

```
$ eval (env _IMPORTER_COMPLETE=fish_source importer)
```

Unquoted, the prefix works:

```
$ importer --dataset Sa<TAB>
Sales Q1  Sales Q2
```

but fish then breaks the value at the space when I run it, so I started
quoting. And the moment there's an opening quote, I get nothing at all:

```
$ importer --dataset "Sa<TAB>
(no completions)
```

Same with a single quote, and same with a backslash-escaped space
(`Sales\ Q<TAB>`). I expected `"Sales Q1"` and `"Sales Q2"` to still be offered,
since that's exactly the case where quoting is needed. Bash and zsh handle the
quoted prefix fine with this same app, so I assume fish isn't meant to be
different here.
