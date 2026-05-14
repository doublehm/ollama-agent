import pytest
from agent.toolkits.design import get_ui_patterns

def test_get_ui_patterns_react():
    res = get_ui_patterns.func(framework="react")
    assert isinstance(res, dict)
    assert "layout" in res
    assert "Tailwind" in res["layout"]

def test_get_ui_patterns_compose():
    res = get_ui_patterns.func(framework="compose")
    assert isinstance(res, dict)
    assert "components" in res
    assert "Material3" in res["components"]

def test_get_ui_patterns_unknown():
    res = get_ui_patterns.func(framework="unknown")
    assert "General UI best practices" in res
