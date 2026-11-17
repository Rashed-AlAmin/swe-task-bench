# Custom param type always sees None when it asks where a value came from

Our deploy CLI has a custom param type for config paths. It needs to know whether the path was actually typed by the user or just fell back to the default, so it asks the context — and lately it gets `None` no matter what I do.

```python
import click

class ConfigPath(click.ParamType):
    name = "configpath"

    def convert(self, value, param, ctx):
        click.echo(f"{param.name} origin={ctx.get_parameter_source(param.name)}")
        return value

@click.command()
@click.option("--config", type=ConfigPath(), default="/etc/deploy.toml")
def deploy(config):
    click.echo(f"using {config}")
```

```
$ python deploy.py
config origin=None
using /etc/deploy.toml
$ python deploy.py --config ./staging.toml
config origin=None
using ./staging.toml
```

I expected `ParameterSource.DEFAULT` on the first run and `ParameterSource.COMMANDLINE` on the second. If I ask the same question from inside the command body instead, I get the right answer both times, so the information clearly exists by then.

I hit the identical thing with an eager `--debug/--no-debug` flag whose callback only writes an env var when the flag wasn't left at its default — the callback sees `None`, decides the user typed it, and stomps the env var on every single run. Both of these worked on 8.3.3.
