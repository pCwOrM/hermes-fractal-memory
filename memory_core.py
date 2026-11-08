"""
Fractal Memory Core Engine.
Hierarchical vectorless episodic memory, procedural attractor clustering,
and O(1) coordinate anchoring for Hermes Agent.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _resolve_default_storage_path() -> Path:
    """
    Resolve the sanctioned Hermes per-plugin data directory:
    `<HERMES_HOME>/plugin-data/fractal-memory-engine/fractal_memory.json`.
    Uses the public `plugins.plugin_storage.plugin_data_dir` helper when running
    inside Hermes Agent, with a safe home-directory fallback for standalone tests.
    """
    try:
        from plugins.plugin_storage import plugin_data_dir  # type: ignore

        return plugin_data_dir("fractal-memory-engine") / "fractal_memory.json"
    except Exception:
        return (
            Path.home()
            / ".hermes"
            / "plugin-data"
            / "fractal-memory-engine"
            / "fractal_memory.json"
        )


@dataclass
class MemoryItem:
    """A procedural memory atom anchored on the fractal coordinate manifold."""

    key: str
    content: str
    ring: str  # "sensory", "task", "invariant"
    salience: float
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 1
    cx: float = 0.0
    cy: float = 0.0
    escape_time: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryItem:
        allowed = {
            "key",
            "content",
            "ring",
            "salience",
            "tags",
            "created_at",
            "last_accessed",
            "access_count",
            "cx",
            "cy",
            "escape_time",
        }
        filtered = {k: v for k, v in data.items() if k in allowed}
        return cls(**filtered)


class FractalCoordinateProjector:
    """
    Projects semantic text onto the complex coordinate manifold (cx, cy)
    and computes polynomial escape-time dynamics under z_{n+1} = z_n^2 + c.
    """

    @staticmethod
    def project_text(text: str, salt: str = "werr_fns_v1") -> Tuple[float, float]:
        """
        Deterministically maps text to canonical coordinates c = (cx, cy)
        within the cardioid/bulb boundary window [-2.0, 0.5] x [-1.2, 1.2].
        """
        clean = " ".join(text.lower().strip().split())
        digest1 = hashlib.sha256(f"{salt}:x:{clean}".encode("utf-8")).hexdigest()
        digest2 = hashlib.sha256(f"{salt}:y:{clean}".encode("utf-8")).hexdigest()

        val_x = int(digest1[:8], 16) / 0xFFFFFFFF  # [0.0, 1.0]
        val_y = int(digest2[:8], 16) / 0xFFFFFFFF  # [0.0, 1.0]

        cx = -2.0 + (val_x * 2.5)  # [-2.0, 0.5]
        cy = -1.2 + (val_y * 2.4)  # [-1.2, 1.2]
        return round(cx, 6), round(cy, 6)

    @staticmethod
    def compute_escape_time(cx: float, cy: float, max_iter: int = 30) -> int:
        """
        Evaluates polynomial escape iteration under z_{n+1} = z_n^2 + c.
        Boundary-adjacent attractors exhibit high escape depth.
        """
        zx, zy = 0.0, 0.0
        for i in range(max_iter):
            if zx * zx + zy * zy > 4.0:
                return i
            zx_new = zx * zx - zy * zy + cx
            zy_new = 2.0 * zx * zy + cy
            zx, zy = zx_new, zy_new
        return max_iter


class FractalMemoryEngine:
    """
    3-Tier Orbital Memory Manifold for Hermes Agent:
      - Ring 1 (Sensory Buffer, 0.60x): Fast ephemeral scratchpad, high decay.
      - Ring 2 (Contextual Task, 1.00x): Mid-term episodic tasks, moderate decay.
      - Ring 3 (Invariant Core, 1.60x): Permanent truths & identities, zero decay.
    """

    # Ring Capacities
    CAP_SENSORY = 64
    CAP_TASK = 128
    CAP_INVARIANT = 1024

    # Half-life Decay Factors per step
    DECAY_SENSORY = 0.82
    DECAY_TASK = 0.96
    DECAY_INVARIANT = 1.00  # Strict zero-decay

    def __init__(self, storage_path: Optional[Path | str] = None):
        self._lock = threading.RLock()
        self.storage_path = (
            Path(storage_path)
            if storage_path and str(storage_path).strip()
            else _resolve_default_storage_path()
        )
        self.auto_inject_context: bool = True
        self.min_recall_resonance: float = 0.30
        self.rings: Dict[str, Dict[str, MemoryItem]] = {
            "sensory": {},
            "task": {},
            "invariant": {},
        }
        self.turn_counter: int = 0
        self._load_from_disk()

    def configure(
        self,
        storage_path: Optional[Path | str] = None,
        auto_inject_context: Optional[bool] = None,
        min_recall_resonance: Optional[float] = None,
    ) -> None:
        """Update runtime configuration from Hermes PluginContext."""
        with self._lock:
            if storage_path is not None and str(storage_path).strip():
                new_path = Path(str(storage_path).strip())
                if new_path != self.storage_path:
                    self.storage_path = new_path
                    self.rings = {"sensory": {}, "task": {}, "invariant": {}}
                    self.turn_counter = 0
                    self._load_from_disk()
            if auto_inject_context is not None:
                self.auto_inject_context = bool(auto_inject_context)
            if min_recall_resonance is not None:
                try:
                    self.min_recall_resonance = max(0.0, min(1.0, float(min_recall_resonance)))
                except (TypeError, ValueError):
                    pass

    # -------------------------------------------------------------------------
    # Core Operations: Remember, Recall, Consolidate, Inspect, Wipe
    # -------------------------------------------------------------------------

    def remember(
        self,
        key: str,
        content: str,
        ring: str = "auto",
        salience: float = 0.75,
        tags: Optional[List[str]] = None,
    ) -> MemoryItem:
        """Stores or updates a memory item on the manifold."""
        with self._lock:
            key = str(key).strip()
            content_clean = str(content).strip()
            tags = [str(t).strip().lower() for t in (tags or []) if str(t).strip()]
            salience = max(0.0, min(1.0, float(salience)))

            cx, cy = FractalCoordinateProjector.project_text(f"{key} {content_clean}")
            escape_time = FractalCoordinateProjector.compute_escape_time(cx, cy)

            # Auto-assignment of ring based on salience & escape resonance
            if ring == "auto" or ring not in self.rings:
                if salience >= 0.85 or "invariant" in tags:
                    assigned_ring = "invariant"
                elif salience >= 0.50 or escape_time >= 15:
                    assigned_ring = "task"
                else:
                    assigned_ring = "sensory"
            else:
                assigned_ring = ring

            # Remove existing key from other rings to avoid duplication
            for r_name in self.rings:
                if key in self.rings[r_name]:
                    del self.rings[r_name][key]

            item = MemoryItem(
                key=key,
                content=content_clean,
                ring=assigned_ring,
                salience=salience,
                tags=tags,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                cx=cx,
                cy=cy,
                escape_time=escape_time,
            )

            # Capacity overflow check for sensory ring
            if assigned_ring == "sensory" and len(self.rings["sensory"]) >= self.CAP_SENSORY:
                lowest_k = min(
                    self.rings["sensory"],
                    key=lambda k: self.rings["sensory"][k].salience,
                )
                del self.rings["sensory"][lowest_k]

            self.rings[assigned_ring][key] = item
            self._save_to_disk()
            return item

    def recall(
        self,
        query: str,
        ring: str = "all",
        min_resonance: float = 0.25,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recalls top-K resonant memories based on lexical overlap, character trigram
        similarity, geometric manifold proximity, and ring priority.
        """
        with self._lock:
            query_clean = str(query).strip()
            if not query_clean:
                return []

            q_tokens = self._tokenize(query_clean)
            q_trigrams = self._trigrams(query_clean)
            q_cx, q_cy = FractalCoordinateProjector.project_text(query_clean)

            target_rings = (
                [ring] if ring in self.rings else ["invariant", "task", "sensory"]
            )

            candidates: List[Tuple[float, MemoryItem]] = []
            for r_name in target_rings:
                priority = (
                    1.5
                    if r_name == "invariant"
                    else (1.2 if r_name == "task" else 1.0)
                )
                for item in self.rings[r_name].values():
                    combined_text = f"{item.key} {item.content} {' '.join(item.tags)}"
                    # 1. Lexical Token Overlap + Trigram Morphology
                    m_tokens = self._tokenize(combined_text)
                    intersection = len(q_tokens.intersection(m_tokens))
                    union = len(q_tokens.union(m_tokens)) or 1
                    token_jaccard = intersection / union

                    m_trigrams = self._trigrams(combined_text)
                    tri_inter = len(q_trigrams.intersection(m_trigrams))
                    tri_union = len(q_trigrams.union(m_trigrams)) or 1
                    trigram_jaccard = tri_inter / tri_union

                    lex_score = 0.70 * token_jaccard + 0.30 * trigram_jaccard

                    # Exact substring match boost
                    if any(
                        tok in combined_text.lower()
                        for tok in q_tokens
                        if len(tok) > 3
                    ):
                        lex_score = min(1.0, lex_score + 0.35)

                    # 2. Geometric Coordinate Proximity
                    dist = math.sqrt((q_cx - item.cx) ** 2 + (q_cy - item.cy) ** 2)
                    geom_score = 1.0 / (1.0 + 1.2 * dist)

                    # 3. Escape-time stability factor [0.5, 1.0]
                    stability = 0.5 + 0.5 * (item.escape_time / 30.0)

                    # 4. Composite Resonance
                    resonance = (
                        (0.55 * lex_score + 0.45 * geom_score)
                        * item.salience
                        * stability
                        * priority
                    )

                    if resonance >= min_resonance:
                        candidates.append((resonance, item))

            candidates.sort(key=lambda x: x[0], reverse=True)
            results: List[Dict[str, Any]] = []

            now = time.time()
            for resonance, item in candidates[: max(1, int(limit))]:
                # Update access statistics (Hebbian reinforcement)
                item.last_accessed = now
                item.access_count += 1
                item.salience = min(1.0, item.salience + 0.04)

                # Promote sensory -> task after repeated recall
                if item.ring == "sensory" and item.access_count >= 2:
                    del self.rings["sensory"][item.key]
                    item.ring = "task"
                    self.rings["task"][item.key] = item

                results.append(
                    {
                        "key": item.key,
                        "content": item.content,
                        "ring": item.ring,
                        "salience": round(item.salience, 3),
                        "resonance": round(resonance, 3),
                        "tags": item.tags,
                        "cx": item.cx,
                        "cy": item.cy,
                        "access_count": item.access_count,
                    }
                )

            self._save_to_disk()
            return results

    def consolidate(
        self,
        retention_threshold: float = 0.35,
        promote_threshold: float = 0.80,
        prune_decayed: bool = True,
    ) -> Dict[str, Any]:
        """
        Consolidates active memories across rings:
        - Promotes high-resonance task items to Invariant.
        - Prunes sub-threshold decayed items from Sensory and Task rings.
        """
        with self._lock:
            pruned_sensory = 0
            pruned_task = 0
            promoted = 0

            # 1. Promote task -> invariant
            task_keys = list(self.rings["task"].keys())
            for k in task_keys:
                item = self.rings["task"][k]
                if item.salience >= promote_threshold and item.access_count >= 3:
                    del self.rings["task"][k]
                    item.ring = "invariant"
                    self.rings["invariant"][k] = item
                    promoted += 1

            # 2. Prune sensory & task
            if prune_decayed:
                sensory_keys = list(self.rings["sensory"].keys())
                for k in sensory_keys:
                    if self.rings["sensory"][k].salience < retention_threshold:
                        del self.rings["sensory"][k]
                        pruned_sensory += 1

                task_threshold = max(0.15, retention_threshold * 0.6)
                for k in list(self.rings["task"].keys()):
                    if self.rings["task"][k].salience < task_threshold:
                        del self.rings["task"][k]
                        pruned_task += 1

            self._save_to_disk()
            return {
                "status": "consolidated",
                "promoted_to_invariant": promoted,
                "pruned_sensory": pruned_sensory,
                "pruned_task": pruned_task,
                "total_sensory": len(self.rings["sensory"]),
                "total_task": len(self.rings["task"]),
                "total_invariant": len(self.rings["invariant"]),
                "state_seal": self.compute_state_seal(),
            }

    def step_decay(self) -> None:
        """Applies one turn of orbital decay to sensory and task rings."""
        with self._lock:
            self.turn_counter += 1
            for item in self.rings["sensory"].values():
                item.salience = max(0.01, item.salience * self.DECAY_SENSORY)

            for item in self.rings["task"].values():
                item.salience = max(0.01, item.salience * self.DECAY_TASK)

            # Invariant ring has DECAY = 1.0 (Zero decay)
            self._save_to_disk()

    def inspect(self, detailed: bool = False, ring: str = "all") -> Dict[str, Any]:
        """Provides operational telemetry, ring occupancy, and state seal."""
        with self._lock:
            summary: Dict[str, Any] = {
                "rings": {
                    "sensory": {
                        "count": len(self.rings["sensory"]),
                        "capacity": self.CAP_SENSORY,
                        "decay_rate": self.DECAY_SENSORY,
                    },
                    "task": {
                        "count": len(self.rings["task"]),
                        "capacity": self.CAP_TASK,
                        "decay_rate": self.DECAY_TASK,
                    },
                    "invariant": {
                        "count": len(self.rings["invariant"]),
                        "capacity": self.CAP_INVARIANT,
                        "decay_rate": self.DECAY_INVARIANT,
                    },
                },
                "total_items": (
                    len(self.rings["sensory"])
                    + len(self.rings["task"])
                    + len(self.rings["invariant"])
                ),
                "turn_counter": self.turn_counter,
                "state_seal": self.compute_state_seal(),
                "storage_path": str(self.storage_path),
            }

            if detailed:
                target_rings = (
                    [ring] if ring in self.rings else ["sensory", "task", "invariant"]
                )
                details = {}
                for r_name in target_rings:
                    details[r_name] = [
                        item.to_dict()
                        for item in sorted(
                            self.rings[r_name].values(),
                            key=lambda x: x.salience,
                            reverse=True,
                        )
                    ]
                summary["items"] = details

            return summary

    def wipe(self, target_ring: str = "sensory", confirm: bool = False) -> Dict[str, Any]:
        """Safely wipes selected rings or executes full reset."""
        with self._lock:
            if not confirm:
                return {
                    "status": "error",
                    "message": "Confirmation required (confirm=True).",
                }

            if target_ring == "sensory":
                cleared = len(self.rings["sensory"])
                self.rings["sensory"] = {}
            elif target_ring == "task":
                cleared = len(self.rings["task"])
                self.rings["task"] = {}
            elif target_ring == "all_non_invariant":
                cleared = len(self.rings["sensory"]) + len(self.rings["task"])
                self.rings["sensory"] = {}
                self.rings["task"] = {}
            elif target_ring == "full_factory_reset":
                cleared = (
                    len(self.rings["sensory"])
                    + len(self.rings["task"])
                    + len(self.rings["invariant"])
                )
                self.rings = {"sensory": {}, "task": {}, "invariant": {}}
                self.turn_counter = 0
            else:
                return {
                    "status": "error",
                    "message": f"Invalid target ring: '{target_ring}'",
                }

            self._save_to_disk()
            return {
                "status": "wiped",
                "target_ring": target_ring,
                "cleared_items": cleared,
                "state_seal": self.compute_state_seal(),
            }

    # -------------------------------------------------------------------------
    # Cryptographic State Seal & Utility
    # -------------------------------------------------------------------------

    def compute_state_seal(self) -> str:
        """Computes a canonical SHA-256 state seal of the memory manifold."""
        with self._lock:
            hasher = hashlib.sha256()
            for r_name in ["invariant", "task", "sensory"]:
                keys_sorted = sorted(self.rings[r_name].keys())
                for k in keys_sorted:
                    item = self.rings[r_name][k]
                    hasher.update(
                        f"{r_name}:{k}:{item.content}:{item.salience:.3f}".encode(
                            "utf-8"
                        )
                    )
            return f"[FRACTAL-MEM-SEAL:{hasher.hexdigest()[:16]}]"

    def _tokenize(self, text: str) -> set[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\u00C0-\u017F]{2,}\b", text.lower())
        return set(words)

    def _trigrams(self, text: str) -> set[str]:
        clean = re.sub(r"\s+", " ", text.lower().strip())
        if len(clean) < 3:
            return {clean} if clean else set()
        return {clean[i : i + 3] for i in range(len(clean) - 2)}

    def _save_to_disk(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": "1.0.1",
                "turn_counter": self.turn_counter,
                "rings": {
                    r_name: [item.to_dict() for item in items.values()]
                    for r_name, items in self.rings.items()
                },
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # Fail-safe in read-only or ephemeral sandbox environments
            pass

    def _load_from_disk(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.turn_counter = int(data.get("turn_counter", 0))
            raw_rings = data.get("rings", {})
            for r_name in ["sensory", "task", "invariant"]:
                self.rings[r_name] = {}
                for item_dict in raw_rings.get(r_name, []):
                    item = MemoryItem.from_dict(item_dict)
                    self.rings[r_name][item.key] = item
        except Exception:
            pass


_ENGINE_LOCK = threading.RLock()
_DEFAULT_ENGINE: Optional[FractalMemoryEngine] = None


def get_memory_engine(storage_path: Optional[Path | str] = None) -> FractalMemoryEngine:
    """Thread-safe singleton accessor for the FractalMemoryEngine."""
    global _DEFAULT_ENGINE
    with _ENGINE_LOCK:
        if _DEFAULT_ENGINE is None or storage_path is not None:
            _DEFAULT_ENGINE = FractalMemoryEngine(storage_path)
        return _DEFAULT_ENGINE
