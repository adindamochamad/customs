"""The seal is the product. These tests are not optional."""

from __future__ import annotations

from customs.manifest import seal
from customs.models import ToolManifest


def _tool(desc: str = "Get the current weather for a location.") -> ToolManifest:
    return ToolManifest(name="get_weather", description=desc, input_schema={"type": "object"})


def test_seal_is_stable_across_tool_ordering() -> None:
    a, b = _tool(), ToolManifest(name="get_time", description="Get time.")
    assert seal([a, b]) == seal([b, a])


def test_seal_is_stable_across_insignificant_whitespace() -> None:
    assert seal([_tool("Get the  current weather.")]) == seal([_tool("Get the current weather.")])


def test_seal_changes_on_a_single_added_word() -> None:
    assert seal([_tool()]) != seal([_tool("Get the current weather for any location.")])


def test_seal_changes_on_schema_change() -> None:
    a = _tool()
    b = ToolManifest(name=a.name, description=a.description, input_schema={"type": "string"})
    assert seal([a]) != seal([b])


def test_seal_is_stable_across_schema_key_ordering() -> None:
    a = ToolManifest(
        name="get_weather",
        description="Get weather.",
        input_schema={"type": "object", "properties": {"location": {"type": "string"}}},
    )
    b = ToolManifest(
        name="get_weather",
        description="Get weather.",
        input_schema={"properties": {"location": {"type": "string"}}, "type": "object"},
    )
    assert seal([a]) == seal([b])


def test_seal_changes_on_casing() -> None:
    assert seal([_tool("Read .env")]) != seal([_tool("read .env")])
