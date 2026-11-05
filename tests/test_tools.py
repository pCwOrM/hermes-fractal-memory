"""Unit tests for Fractal Memory tool handlers and CLI commands."""

import os
import sys
import tempfile
from pathlib import Path

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import memory_core
import tools


def setup_module():
    # Use temporary file for test runs
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.close()
    memory_core._DEFAULT_ENGINE = memory_core.FractalMemoryEngine(storage_path=tmp.name)


def test_fractal_remember_tool():
    res = tools.fractal_remember_handler({
        "key": "deploy_target",
        "content": "Deploy smart contracts to Arbitrum One at chain ID 42161",
        "ring": "task",
        "salience": 0.8,
        "tags": ["web3", "arbitrum"],
    })

    assert res["status"] == "stored"
    assert res["key"] == "deploy_target"
    assert res["ring"] == "task"
    assert "state_seal" in res


def test_fractal_recall_tool():
    res = tools.fractal_recall_handler({
        "query": "Where do we deploy contracts on Arbitrum?",
        "limit": 3,
        "min_resonance": 0.2,
    })

    assert res["status"] == "success"
    assert res["count"] >= 1
    assert res["memories"][0]["key"] == "deploy_target"


def test_fractal_memory_inspect_tool():
    res = tools.fractal_memory_inspect_handler({"detailed": True})
    assert "rings" in res
    assert "total_items" in res
    assert res["total_items"] >= 1
    assert "items" in res


def test_fractal_consolidate_tool():
    res = tools.fractal_consolidate_handler({"retention_threshold": 0.2})
    assert res["status"] == "consolidated"
    assert "state_seal" in res


def test_fractal_memory_wipe_protection():
    # Attempt wipe without confirmation -> rejected
    err = tools.fractal_memory_wipe_handler({"target_ring": "sensory", "confirm": False})
    assert err["status"] == "error"

    # Confirmed wipe of sensory
    res = tools.fractal_memory_wipe_handler({"target_ring": "sensory", "confirm": True})
    assert res["status"] == "wiped"


def test_cli_slash_commands():
    status_text = tools.memory_cli_status()
    assert "Hermes Fractal Memory Telemetry" in status_text
    assert "Ring 1" in status_text
    assert "Ring 3" in status_text

    quick_res = tools.remember_cli_quick("security_policy Never leak private keys or mnemonic")
    assert "Invariant memory pinned" in quick_res
