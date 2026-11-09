"""Unit tests for Fractal Memory Core Engine."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import hooks  # noqa: E402
import memory_core  # noqa: E402
from memory_core import FractalCoordinateProjector, FractalMemoryEngine  # noqa: E402


def test_coordinate_projection_bounds():
    cx, cy = FractalCoordinateProjector.project_text("Quantum teleportation protocol")
    assert -2.0 <= cx <= 0.5
    assert -1.2 <= cy <= 1.2

    # Determinism check
    cx2, cy2 = FractalCoordinateProjector.project_text("Quantum teleportation protocol")
    assert cx == cx2
    assert cy == cy2

    # Escape time
    esc = FractalCoordinateProjector.compute_escape_time(cx, cy, max_iter=30)
    assert 0 <= esc <= 30


def test_three_ring_auto_assignment():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir) / "test_mem.json"
        engine = FractalMemoryEngine(storage_path=storage)

        # High salience -> Invariant ring
        item1 = engine.remember(key="arch_rule", content="Always use O(1) memory", salience=0.90)
        assert item1.ring == "invariant"
        assert "arch_rule" in engine.rings["invariant"]

        # Mid salience -> Task ring
        item2 = engine.remember(key="current_goal", content="Refactor auth pipeline", salience=0.60)
        assert item2.ring == "task"
        assert "current_goal" in engine.rings["task"]

        # Low salience -> Sensory ring
        item3 = engine.remember(key="temp_log", content="Fetched 200 OK from server", salience=0.20)
        assert item3.ring == "sensory"
        assert "temp_log" in engine.rings["sensory"]


def test_recall_and_hebbian_promotion():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir) / "test_mem.json"
        engine = FractalMemoryEngine(storage_path=storage)

        # Store in sensory ring explicitly
        engine.remember(key="user_coffee", content="User drinks espresso with oat milk", ring="sensory", salience=0.40)
        assert "user_coffee" in engine.rings["sensory"]

        # Recall 1st time
        hits = engine.recall("coffee espresso", min_resonance=0.1)
        assert len(hits) >= 1
        assert hits[0]["key"] == "user_coffee"
        assert hits[0]["access_count"] == 2
        # After 2 accesses, it should be promoted to task ring!
        assert "user_coffee" in engine.rings["task"]


def test_orbital_decay_and_consolidation():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir) / "test_mem.json"
        engine = FractalMemoryEngine(storage_path=storage)

        engine.remember(key="inv_truth", content="Lean 4 proof has 0 sorry", ring="invariant", salience=1.0)
        engine.remember(key="task_note", content="Check gas limits on Arbitrum", ring="task", salience=0.85)
        engine.remember(key="sensory_note", content="Temporary buffer noise", ring="sensory", salience=0.25)

        initial_inv_sal = engine.rings["invariant"]["inv_truth"].salience
        initial_task_sal = engine.rings["task"]["task_note"].salience
        initial_sen_sal = engine.rings["sensory"]["sensory_note"].salience

        # 3 turns of decay
        for _ in range(3):
            engine.step_decay()

        # Invariant never decays
        assert engine.rings["invariant"]["inv_truth"].salience == initial_inv_sal
        # Task decays moderately
        assert engine.rings["task"]["task_note"].salience < initial_task_sal
        # Sensory decays rapidly
        assert engine.rings["sensory"]["sensory_note"].salience < initial_sen_sal

        # Consolidate
        report = engine.consolidate(retention_threshold=0.30, prune_decayed=True)
        # sensory_note had salience 0.25 * 0.82^3 = ~0.137, which is < 0.30 -> pruned!
        assert "sensory_note" not in engine.rings["sensory"]
        assert report["pruned_sensory"] >= 1
        assert report["total_invariant"] == 1


def test_cryptographic_state_seal():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir) / "test_mem.json"
        engine = FractalMemoryEngine(storage_path=storage)

        seal1 = engine.compute_state_seal()
        assert seal1.startswith("[FRACTAL-MEM-SEAL:")

        engine.remember(key="k1", content="Val 1", ring="invariant")
        seal2 = engine.compute_state_seal()
        assert seal1 != seal2


def test_multi_profile_isolation_and_hook_separation():
    """
    Verify that when one Hermes process serves multiple profiles (switching
    `hermes_constants.get_hermes_home()`), each profile gets its own isolated
    store and `pre_llm_call` never injects Profile A's memories into Profile B's turns.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        profile_a_home = Path(tmpdir) / "profile_a"
        profile_b_home = Path(tmpdir) / "profile_b"
        active_home = {"path": profile_a_home}

        fake_hermes_constants = types.ModuleType("hermes_constants")
        fake_hermes_constants.get_hermes_home = lambda: active_home["path"]  # type: ignore[attr-defined]

        # Clear any test-level storage_path overrides so dynamic profile resolution runs
        saved_configs = dict(memory_core._PROFILE_CONFIGS)
        saved_default = dict(memory_core._DEFAULT_CONFIG)
        try:
            memory_core._PROFILE_CONFIGS.clear()
            memory_core._DEFAULT_CONFIG["storage_path"] = None

            with patch.dict(sys.modules, {"hermes_constants": fake_hermes_constants}):
                # 1. Profile A stores a secret invariant
                active_home["path"] = profile_a_home
                eng_a = memory_core.get_memory_engine()
                eng_a.remember(
                    key="profile_a_secret",
                    content="Profile A exclusive deployment key is ALPHA-9999",
                    ring="invariant",
                    salience=0.95,
                )
                assert eng_a.storage_path == (
                    profile_a_home / "plugin-data" / "fractal-memory-engine" / "fractal_memory.json"
                ).resolve()

                # 2. Switch active profile to Profile B in the same process
                active_home["path"] = profile_b_home
                eng_b = memory_core.get_memory_engine()
                assert eng_b is not eng_a
                assert eng_b.storage_path == (
                    profile_b_home / "plugin-data" / "fractal-memory-engine" / "fractal_memory.json"
                ).resolve()

                # Profile B's pre_llm_call must NOT inject Profile A's memory
                hook_res_b = hooks.pre_llm_call_hook(
                    user_message="What is the Profile A exclusive deployment key ALPHA-9999?"
                )
                assert hook_res_b is None

                # Profile A's pre_llm_call still recalls Profile A's memory
                active_home["path"] = profile_a_home
                hook_res_a = hooks.pre_llm_call_hook(
                    user_message="What is the Profile A exclusive deployment key ALPHA-9999?"
                )
                assert hook_res_a is not None
                assert "ALPHA-9999" in hook_res_a["context"]
        finally:
            memory_core._PROFILE_CONFIGS.clear()
            memory_core._PROFILE_CONFIGS.update(saved_configs)
            memory_core._DEFAULT_CONFIG.update(saved_default)


def test_fail_closed_without_hermes_home_or_plugin_storage():
    """
    Verify that `_resolve_default_storage_path()` fails closed (raises RuntimeError)
    instead of falling back to a hardcoded `~/.hermes/plugin-data/...` path when neither
    `plugins.plugin_storage` nor `hermes_constants` is available.
    """
    with patch.dict(
        sys.modules,
        {"plugins": None, "plugins.plugin_storage": None, "hermes_constants": None},
    ):
        with pytest.raises(RuntimeError, match="cannot resolve profile-scoped storage path"):
            memory_core._resolve_default_storage_path()


def test_atomic_save_crash_preserves_existing_store():
    """
    Verify that `_save_to_disk` writes to a sibling temporary file and uses `os.replace`,
    so a crash mid-write never truncates or empties the existing store on disk.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = Path(tmpdir) / "atomic_test.json"
        engine = FractalMemoryEngine(storage_path=storage)
        engine.remember(
            key="persistent_rule",
            content="Never truncate the store before write completes",
            ring="invariant",
            salience=0.95,
        )

        original_bytes = storage.read_text(encoding="utf-8")
        original_parsed = json.loads(original_bytes)
        assert len(original_parsed["rings"]["invariant"]) == 1

        # Simulate a crash mid-write inside json.dump
        with patch("memory_core.json.dump", side_effect=OSError("disk full mid-write")):
            with pytest.raises(OSError, match="disk full mid-write"):
                engine.remember(
                    key="second_item",
                    content="This write crashes halfway through",
                    ring="task",
                )

        # Existing file on disk must be 100% intact (not truncated!) and no leftover .tmp files
        after_bytes = storage.read_text(encoding="utf-8")
        assert after_bytes == original_bytes
        leftover_tmps = list(Path(tmpdir).glob("*.tmp"))
        assert leftover_tmps == []
