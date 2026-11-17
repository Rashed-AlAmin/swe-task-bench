# Ctrl-C sometimes dumps a traceback instead of printing "Aborted!"

Our deploy tool prompts for a host and then walks through the steps:

```python
import time
import click

@click.command()
@click.option("--target", prompt="Target host")
def deploy(target):
    for step in range(10):
        click.echo(f"step {step} on {target}")
        time.sleep(1)

if __name__ == "__main__":
    deploy()
```

Usually bailing out is clean:

```
$ python deploy.py
Target host: ^C
Aborted!
$ echo $?
1
```

But if I'm impatient and hit Ctrl-C a second time right after the first one
(or just hold it down), every so often I get this instead:

```
$ python deploy.py
Target host: ^C^CTraceback (most recent call last):
  File "deploy.py", line 12, in <module>
    deploy()
  ...
KeyboardInterrupt
$ echo $?
1
```

It's not every time — maybe one run in five — which is why it took me a while
to believe it was real. Same thing if I interrupt during the step loop.

The one that actually broke something: I Ctrl-C'd right as the last step
printed, after the deploy had already succeeded, and still got a traceback and
a failure status, so our wrapper rolled the release back for nothing.

I'd expect it to always print `Aborted!` and exit 1 when I interrupt it, and to
exit 0 if the work was already done.
