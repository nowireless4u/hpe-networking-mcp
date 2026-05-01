"""Smoke tests for AOS8 guided prompts registration."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

EXPECTED_PROMPTS = {
    "aos8_triage_client",
    "aos8_triage_ap",
    "aos8_health_check",
    "aos8_audit_change",
    "aos8_rf_analysis",
    "aos8_wlan_review",
    "aos8_client_flood",
    "aos8_compare_md_config",
    "aos8_pre_change_check",
}


def _capture_register():
    """Run register(mcp) against a fake MCP and return {name: fn} captured."""
    from hpe_networking_mcp.platforms.aos8.tools import prompts

    captured: dict[str, callable] = {}

    def fake_prompt(fn):
        captured[fn.__name__] = fn
        return fn

    fake_mcp = MagicMock()
    fake_mcp.prompt = fake_prompt
    prompts.register(fake_mcp)
    return captured


def test_register_attaches_all_nine_prompts():
    """register(mcp) must decorate exactly the 9 PROMPT-01..09 functions."""
    captured = _capture_register()
    assert set(captured.keys()) == EXPECTED_PROMPTS, sorted(captured.keys())


@pytest.mark.parametrize("prompt_name", sorted(EXPECTED_PROMPTS))
def test_each_prompt_returns_nonempty_summary_string(prompt_name: str):
    """Each prompt returns non-empty str ending with a Summarize section (D-02)."""
    captured = _capture_register()
    fn = captured[prompt_name]
    sig_param_count = fn.__code__.co_argcount
    sig_params = fn.__code__.co_varnames[:sig_param_count]
    kwargs = {p: "x" for p in sig_params}
    result = fn(**kwargs)
    assert isinstance(result, str), f"{prompt_name} did not return str"
    assert result.strip(), f"{prompt_name} returned empty string"
    assert "Summarize" in result, f"{prompt_name} missing Summarize section (D-02)"


def test_pre_change_check_references_write_memory():
    """PROMPT-09 must remind the operator about aos8_write_memory (WRITE-12 contract)."""
    captured = _capture_register()
    body = captured["aos8_pre_change_check"](config_path="/md/example")
    assert "aos8_write_memory" in body
