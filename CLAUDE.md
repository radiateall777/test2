# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A LangGraph agent built from the `new-langgraph-project` template. The graph in `src/agent/graph.py` is still the template's single-node placeholder that returns a fixed string — replace it with real logic rather than treating it as working behavior.

## Environment

Use the project virtualenv explicitly; there is no activation step in these commands and the global `python` is not the right interpreter:

```bash
.venv/bin/python -m pytest tests/unit_tests    # unit tests
.venv/bin/python -m pytest tests/unit_tests/test_configuration.py::test_placeholder    # single test
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy --strict src/
```

Dependencies are managed with `uv` (`uv.lock` is committed). The package is installed editable, so `src/agent` changes are picked up without reinstalling.

Run the dev server with `langgraph dev` (uses `.venv/bin/langgraph`). It reads `langgraph.json`, which points the `agent` graph at `./src/agent/graph.py:graph` and loads `.env`.

## Tests

Two suites with different requirements:

- `tests/unit_tests/` — no network, no credentials. This is what CI runs and what you should run by default.
- `tests/integration_tests/` — marked `@pytest.mark.langsmith` and needs a valid `LANGSMITH_API_KEY`. **Currently fails with a 401** because the key in `.env` is invalid or expired. A failure here is not necessarily your change.

Async tests use `anyio`, not `pytest-asyncio`. The `anyio_backend` fixture in `tests/conftest.py` pins the backend to asyncio, and test modules set `pytestmark = pytest.mark.anyio`. Note the integration CI workflow installs `pytest-asyncio` instead, which does not match this setup.

## Known broken commands

`make lint` sets `PYTHON_FILES=.` and runs `mypy --strict .`, which includes `tests/` and fails on two pre-existing errors there (an unannotated fixture in `conftest.py`, and the untyped dict passed to `ainvoke` in the integration test). Use `mypy --strict src/` directly, which is also what CI runs.

`ruff check .` passes across the repo.

## Graph conventions

State and runtime config are separate concepts, and both are plain type declarations rather than LangGraph-specific base classes:

- `State` is a `@dataclass` — the channels flowing through the graph. Nodes return a partial dict of the fields they update.
- `Context` is a `TypedDict` passed as `context_schema` to `StateGraph`. Nodes read it via `runtime.context`, which may be `None`, so the existing code guards with `(runtime.context or {}).get(...)`. Keep that guard when adding context reads.

Nodes are `async` and added via `.add_node(call_model)`, which derives the node name from the function name — renaming a node function changes the graph's edge names, so update `.add_edge` calls together with it.

`src/agent/__init__.py` re-exports `graph`, so both `from agent import graph` and `from agent.graph import graph` work and appear across the tests.

## Packaging quirk

`pyproject.toml` maps the same `src/agent` directory to two package names, `agent` and `langgraph.templates.agent`. The latter is a template-registry artifact. Keep both mappings in sync if you move the source directory.

Dev dependencies are declared twice with conflicting floors — `[project.optional-dependencies]` (mypy>=1.11.1, ruff>=0.6.1) and `[dependency-groups]` (mypy>=1.13.0, ruff>=0.8.2). `uv` uses the latter. `requires-python` claims `>=3.10` but CI only tests 3.11 and 3.12.
