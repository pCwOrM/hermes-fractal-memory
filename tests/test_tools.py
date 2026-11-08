"""Unit tests for Fractal Memory tool handlers and slash commands."""

from __future__ import annotations

import json
import os
import sys
import tempfile

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import memory_core  # noqa: E402
import tools  # noqa: E402


def setup_module() -> None:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    memory_core._DEFAULT_ENGINE = memory_core.FractalMemoryEngine(storage_path=tmp.name)


def test_fractal_remember_tool() -> None:
    res = tools.fractal_remember_handler(
        {
            "key": "deploy_target",
            "content": "Deploy smart contracts to Arbitrum One at chain ID 42161",
            "ring": "task",
            "salience": 0.8,
            "tags": ["web3", "arbitrum"],
        },
        task_id="t1",
        session_id="s1",
    )

    assert isinstance(res, str)
    parsed = json.loads(res)
    assert parsed["status"] == "stored"
    assert res["status"] == "stored"
    assert res["key"] == "deploy_target"
    assert res["ring"] == "task"
    assert "state_seal" in res


def test_fractal_recall_tool() -> None:
    res = tools.fractal_recall_handler(
        {
            "query": "Where do we deploy contracts on Arbitrum?",
            "limit": 3,
            "min_resonance": 0.2,
        },
        task_id="t1",
    )

    assert isinstance(res, str)
    parsed = json.loads(res)
    assert parsed["status"] == "success"
    assert res["count"] >= 1
    assert res["memories"][0]["key"] == "deploy_target"


def test_fractal_memory_inspect_tool() -> None:
    res = tools.fractal_memory_inspect_handler({"detailed": True})
    assert isinstance(res, str)
    parsed = json.loads(res)
    assert "rings" in parsed
    assert "total_items" in res
    assert res["total_items"] >= 1
    assert "items" in res


def test_fractal_consolidate_tool() -> None:
    res = tools.fractal_consolidate_handler({"retention_threshold": 0.2})
    assert isinstance(res, str)
    parsed = json.loads(res)
    assert parsed["status"] == "consolidated"
    assert "state_seal" in res


def test_fractal_memory_wipe_protection() -> None:
    err = tools.fractal_memory_wipe_handler(
        {"target_ring": "sensory", "confirm": False}
    )
    assert isinstance(err, str)
    assert err["status"] == "error"

    res = tools.fractal_memory_wipe_handler(
        {"target_ring": "sensory", "confirm": True}
    )
    assert isinstance(res, str)
    assert res["status"] == "wiped"


def test_cli_slash_commands() -> None:
    status_text = tools.memory_cli_status(raw_args="", session_id="s1", platform="cli")
    assert "Hermes Fractal Memory Telemetry" in status_text
    assert "Ring 1" in status_text
    assert "Ring 3" in status_text

    quick_res = tools.remember_cli_quick(
        "coding_standard Always include upper bounds on Python package dependencies"
    )
    assert "Invariant memory pinned" in quick_res
