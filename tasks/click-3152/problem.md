# An option that should take zero or one values refuses the bare form

I'm building a small backup CLI for our Postgres boxes. I want `--compress` to work three ways: leave it off and get the default, pass it on its own and get a sensible choice, or pass it with an explicit value.

```python
import click

@click.command()
@click.option("--compress", type=str, is_flag=False, flag_value="gzip", default="none")
def backup(compress):
    click.echo(compress)

if __name__ == "__main__":
    backup()
```

Two of the three work:

```
$ python backup.py
none
$ python backup.py --compress zstd
zstd
$ python backup.py --compress
Usage: backup.py [OPTIONS]
Try 'backup.py --help' for help.

Error: Option '--compress' requires an argument.
```

I expected the last one to print `gzip`. Same thing with an int version (`type=int, is_flag=False, flag_value=1, default=0`) — `--level` on its own errors out instead of giving me 1.

If I drop `default="none"` entirely the bare form suddenly starts working, but then omitting the option gives me `None` and I lose my default. I can't seem to have both. Am I holding this wrong, or is it a bug?
