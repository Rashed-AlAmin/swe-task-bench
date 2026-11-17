# The default printed in --help isn't a value my CLI will accept

Writing a data importer and I wanted the checksum algorithm to come from an
enum so the rest of the pipeline can't pass a typo'd string around:

```python
import enum
import click

class HashType(enum.Enum):
    MD5 = enum.auto()
    SHA1 = enum.auto()

@click.command()
@click.option(
    "--checksum",
    type=click.Choice(HashType),
    default=HashType.SHA1,
    show_default=True,
)
def ingest(checksum):
    click.echo(f"using {checksum}")
```

Here's the help:

```
$ python ingest.py --help
Usage: ingest.py [OPTIONS]

Options:
  --checksum [MD5|SHA1]  [default: HashType.SHA1]
  --help                 Show this message and exit.
```

The allowed values are listed as `MD5|SHA1`, but the default is shown as
`HashType.SHA1`, which is not one of them — copy it off the help text and you
get `Error: invalid choice: HashType.SHA1`. I expected `[default: SHA1]`.

It gets stranger with an `enum.IntEnum`: the choices still come out as
`[LOW|HIGH]` but the default renders as the bare number, so the help line reads
`[LOW|HIGH]  [default: 2]`. Writing `default="SHA1"` instead does print the
right thing, which feels like it shouldn't matter.
