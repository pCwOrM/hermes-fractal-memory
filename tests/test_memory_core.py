"""Unit tests for Fractal Memory Core Engine."""

import os
import sys
import tempfile
from pathlib import Path

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

from memory_core import FractalCoordinateProjector, FractalMemoryEngine


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
