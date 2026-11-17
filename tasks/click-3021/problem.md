# Prompt still has a space on the end even though I asked for no suffix

I'm writing a tiny interactive admin shell for our support team and I want the
prompt to look like a real shell prompt, so I'm drawing the whole thing myself
and turning the suffix off:

```python
import click

@click.command()
def shell():
    while True:
        line = click.prompt("admin>", prompt_suffix="")
        if line == "quit":
            return
        click.echo(f"ran {line}")

if __name__ == "__main__":
    shell()
```

When I run it there's a gap between my `>` and where I start typing, which is
not what I drew. I piped it so I could actually see the characters:

```
$ echo "status" | python admin.py | cat -A
admin> $
```

So the output is `admin>` plus a space. I expected exactly `admin>` with
nothing after it (`admin>$` in `cat -A`), since I passed an empty suffix.

Same deal with confirmations: `click.confirm("Wipe cache?", prompt_suffix="")`
gives me `Wipe cache? [y/N] ` instead of `Wipe cache? [y/N]`.

An older 7.x version we had pinned on another box renders these the way I
expect, so I don't think I'm holding it wrong? Anything with a normal `": "`
suffix looks fine, it's only when I blank the suffix out.
