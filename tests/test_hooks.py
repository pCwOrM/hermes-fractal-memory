"""Unit tests for Hermes Agent Lifecycle Hooks (`pre_llm_call` & `post_llm_call`)."""

from __future__ import annotations

import os
import sys
import tempfile

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import hooks  # noqa: E402
import memory_core  # noqa: E402


class MockTurnContext:
    def __init__(self, user_prompt: str = "") -> None:
        self.user_prompt = user_prompt
        self.extra_system_context = ""


def setup_module() -> None:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    memory_core.configure_runtime(
        storage_path=tmp.name,
        auto_inject_context=True,
        min_recall_resonance=0.30,
    )


def test_pre_llm_call_keyword_injection() -> None:
    engine = memory_core.get_memory_engine()
    engine.remember(
        key="db_port",
        content="PostgreSQL database port is 5432, primary schema is analytics",
        ring="invariant",
        salience=0.92,
    )

    res = hooks.pre_llm_call_hook(
        session_id="sess_01",
        user_message="What was the postgres database port number?",
        conversation_history=[],
        is_first_turn=False,
        model="nous-hermes-3",
        platform="cli",
    )

    assert res is not None
    assert "context" in res
    assert res["action"] == "injected"
    assert res["count"] >= 1
    assert "FRACTAL-ACTIVE-MEMORY" in res["context"]
    assert "5432" in res["context"]


def test_pre_step_legacy_context_injection() -> None:
    ctx = MockTurnContext(user_prompt="What was the postgres database port number?")
    res = hooks.fractal_pre_step_injector(ctx)

    assert res is not None
    assert res["action"] == "injected"
    assert "FRACTAL-ACTIVE-MEMORY" in ctx.extra_system_context
    assert "5432" in ctx.extra_system_context


def test_post_llm_call_decay_and_auto_consolidation() -> None:
    engine = memory_core.get_memory_engine()
    initial_turns = engine.turn_counter

    res = hooks.post_llm_call_hook(
        session_id="sess_01",
        user_message="What was the postgres database port number?",
        assistant_response="The PostgreSQL port is 5432.",
        model="nous-hermes-3",
        platform="cli",
    )

    assert res is not None
    assert res["action"] == "decayed"
    assert engine.turn_counter == initial_turns + 1
    assert res["state_seal"].startswith("[FRACTAL-MEM-SEAL:")
