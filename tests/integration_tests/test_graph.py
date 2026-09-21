import pytest

from agent import graph

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_agent_simple_passthrough() -> None:
    inputs = {"changeme": "some_val"}
    # langgraph 1.0.10 leaves CompiledStateGraph's input type variable
    # unresolved unless input_schema= is passed explicitly, so ainvoke
    # rejects every argument type under --strict.
    res = await graph.ainvoke(inputs)  # type: ignore[arg-type]
    assert res is not None
