# Can't pickle or deepcopy my command objects any more

We have a job runner that builds click commands in a parent process and ships them to worker processes, so the command and its options have to survive a pickle round-trip. After upgrading click this blew up everywhere, and I boiled it down to this:

```python
import pickle
import click

opt = click.Option(["--name"])
print(pickle.loads(pickle.dumps(opt)).name)
```

```
$ python repro.py
Traceback (most recent call last):
  File "repro.py", line 5, in <module>
    print(pickle.loads(pickle.dumps(opt)).name)
ValueError: <object object at 0x7f3b8c1d3150> is not a valid <some private click type>
```

I expected to get an option back that still has `name == "name"` and still has no value set for its default. A whole `click.Command` fails the same way, presumably because of the options hanging off it.

Our 3.10 CI box is worse: there `copy.copy(opt)` and `copy.deepcopy(opt)` raise that same ValueError too. On 3.12 both copies come back fine, which is why this took me two days to pin down — pickle is the only one that's broken on every version I tried.

Is there something I'm supposed to do to make these serializable?
