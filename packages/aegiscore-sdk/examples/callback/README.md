# aegiscore-example-callback

A Aegiscore plugin (callback) scaffolded by ``aegiscore-sdk plugin new``.

## Build + install

```bash
uv build
pip install dist/*.whl
```

After install, the framework's plugin loader discovers this contribution
via the ``aegiscore.callbacks`` entry-point group.

## Test

```bash
pip install aegiscore-sdk[testing]
pytest
```

Use ``aegiscore_sdk.testing.FakeBackend`` / ``FakeLLM`` / ``FakeSandbox``
to write hermetic tests that don't need a live framework.
