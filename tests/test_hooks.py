"""Unit tests for Hermes Agent Lifecycle Hooks."""

import os
import sys
import tempfile

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import hooks
import memory_core


class MockTurnContext:
    def __init__(self, user_prompt=""):
        self.user_prompt = user_prompt
        self.extra_system_context = ""


def setup_module():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    memory_core._DEFAULT_ENGINE = memory_core.FractalMemoryEngine(storage_path=tmp.name)


def test_pre_step_injection():
    engine = memory_core.get_memory_engine()
    engine.remember(
        key="db_port",
        content="PostgreSQL database port is 5432, user is postgres",
        ring="invariant",
        salience=0.9,
    )

    ctx = MockTurnContext(user_prompt="What was the postgres database port number?")
    res = hooks.fractal_pre_step_injector(ctx)

    assert res is not None
    assert res["action"] == "injected"
    assert res["count"] >= 1
    assert "FRACTAL-ACTIVE-MEMORY" in ctx.extra_system_context
    assert "5432" in ctx.extra_system_context


def test_post_step_decay():
    engine = memory_core.get_memory_engine()
    initial_turns = engine.turn_counter

    ctx = MockTurnContext()
    res = hooks.fractal_post_step_decay(ctx)

    assert res is not None
    assert res["action"] == "decayed"
    assert engine.turn_counter == initial_turns + 1
