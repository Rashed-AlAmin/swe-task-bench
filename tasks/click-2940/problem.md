# Tests of a command that reads stdin end with "Aborted!" and exit code 1

I'm writing a CSV importer that reads from a file or from stdin, which is the normal unix thing. It works perfectly when I run it by hand — `cat people.csv | python importer.py` prints every row and exits 0. But every test I write for it fails.

```python
import click
from click.testing import CliRunner

@click.command()
@click.argument("src", type=click.File("r"), default="-")
def importer(src):
    for line in src:
        click.echo(f"row: {line.strip()}")

def test_importer():
    result = CliRunner().invoke(importer, [], input="alice\nbob\n")
    assert result.exit_code == 0
    assert result.output == "row: alice\nrow: bob\n"
```

```
$ python -m pytest test_importer.py
AssertionError: assert 1 == 0
```

If I print `result.output` I get:

```
row: alice
row: bob

Aborted!
```

So all my rows are there, and then it tacks on a blank line and `Aborted!`, and `result.exception` is set. Nothing in my command aborts anything — there's no prompt and no confirm in it at all. The only way I've found to make the assertion pass is to chop the last two lines off, which feels wrong to have in every stdin test I own.
