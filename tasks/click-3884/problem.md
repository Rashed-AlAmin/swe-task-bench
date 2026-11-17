# Error message prints a Python list when my option has two env var names

Our weather report CLI accepts either of two environment variable names for
the same setting (we're migrating from the old unprefixed one):

```python
import click

@click.command()
@click.option(
    "--units",
    envvar=["WEATHER_UNITS", "UNITS"],
    show_envvar=True,
    required=True,
)
def report(units):
    click.echo(f"reporting in {units}")

if __name__ == "__main__":
    report()
```

Running it with nothing set:

```
$ python weather.py
Usage: weather.py [OPTIONS]
Try 'weather.py --help' for help.

Error: Missing option '--units' (env var: '['WEATHER_UNITS', 'UNITS']').
```

That inner `'[...]'` with the nested quotes is a Python list dumped into a user
facing message. I expected it to just name the two variables, something like
`(env var: 'WEATHER_UNITS', 'UNITS')`.

Related, and maybe the same thing: in another command we read the variable name
out of our own config and it can legitimately come back empty, so the option
ends up with `envvar=""` (and in one spot `envvar=[]`). Then `--help` prints

```
  --units TEXT  [env var: ]
```

which just looks broken. I'd expect it to say nothing at all there, exactly
like an option that was never given an env var in the first place.
