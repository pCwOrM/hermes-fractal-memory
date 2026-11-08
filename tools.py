"""
Hermes Agent Tool Handlers and Slash Commands for Fractal Memory Engine.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    from .memory_core import get_memory_engine
except (ImportError, ValueError):
    from memory_core import get_memory_engine  # type: ignore


class _JsonToolResponse(str):
    """
    A JSON-serialized string return value (as required by Hermes tool handlers)
    that also supports dict-style key lookup (`res["status"]`, `"rings" in res`)
    for direct ergonomic inspection in Python tests.
    """

    _payload: Dict[str, Any]

    def __new__(cls, payload: Dict[str, Any]) -> _JsonToolResponse:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        obj = super().__new__(cls, text)
        obj._payload = payload
        return obj

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            return self._payload[key]
        return super().__getitem__(key)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str) and item in self._payload:
            return True
        return super().__contains__(str(item))

    def get(self, key: str, default: Any = None) -> Any:
        return self._payload.get(key, default)

    def keys(self):
        return self._payload.keys()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._payload)


def _json_response(payload: Dict[str, Any]) -> str:
    return _JsonToolResponse(payload)


def fractal_remember_handler(
    args: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> str:
    """Stores or updates a memory item on the fractal coordinate manifold."""
    try:
        params = args if isinstance(args, dict) else {}
        key = str(params.get("key", "")).strip()
        content = str(params.get("content", "")).strip()
        ring = str(params.get("ring", "auto")).strip()
        salience = float(params.get("salience", 0.75))
        tags = params.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(tags)]

        if not key or not content:
            return _json_response(
                {
                    "status": "error",
                    "message": "Both 'key' and 'content' are required.",
                }
            )

        engine = get_memory_engine()
        item = engine.remember(
            key=key, content=content, ring=ring, salience=salience, tags=tags
        )

        return _json_response(
            {
                "status": "stored",
                "key": item.key,
                "ring": item.ring,
                "salience": round(item.salience, 3),
                "cx": item.cx,
                "cy": item.cy,
                "escape_time": item.escape_time,
                "state_seal": engine.compute_state_seal(),
            }
        )
    except Exception as exc:
        return _json_response({"status": "error", "message": str(exc)})


def fractal_recall_handler(
    args: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> str:
    """Retrieves top resonant memories from the manifold matching the query."""
    try:
        params = args if isinstance(args, dict) else {}
        query = str(params.get("query", "")).strip()
        ring = str(params.get("ring", "all")).strip()
        min_resonance = float(params.get("min_resonance", 0.25))
        limit = int(params.get("limit", 5))

        if not query:
            return _json_response(
                {
                    "status": "error",
                    "message": "'query' is required for fractal recall.",
                }
            )

        engine = get_memory_engine()
        results = engine.recall(
            query=query, ring=ring, min_resonance=min_resonance, limit=limit
        )

        return _json_response(
            {
                "status": "success",
                "query": query,
                "count": len(results),
                "memories": results,
                "state_seal": engine.compute_state_seal(),
            }
        )
    except Exception as exc:
        return _json_response({"status": "error", "message": str(exc)})


def fractal_consolidate_handler(
    args: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> str:
    """Consolidates active working memories into invariants and prunes decayed items."""
    try:
        params = args if isinstance(args, dict) else {}
        retention_threshold = float(params.get("retention_threshold", 0.35))
        promote_threshold = float(params.get("promote_threshold", 0.80))
        prune_decayed = bool(params.get("prune_decayed", True))

        engine = get_memory_engine()
        report = engine.consolidate(
            retention_threshold=retention_threshold,
            promote_threshold=promote_threshold,
            prune_decayed=prune_decayed,
        )
        return _json_response(report)
    except Exception as exc:
        return _json_response({"status": "error", "message": str(exc)})


def fractal_memory_inspect_handler(
    args: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> str:
    """Inspects memory ring occupancy, telemetry, and state seal."""
    try:
        params = args if isinstance(args, dict) else {}
        detailed = bool(params.get("detailed", False))
        ring = str(params.get("ring", "all")).strip()

        engine = get_memory_engine()
        report = engine.inspect(detailed=detailed, ring=ring)
        return _json_response(report)
    except Exception as exc:
        return _json_response({"status": "error", "message": str(exc)})


def fractal_memory_wipe_handler(
    args: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> str:
    """Safely wipes selected rings or resets the memory system."""
    try:
        params = args if isinstance(args, dict) else {}
        target_ring = str(params.get("target_ring", "sensory")).strip()
        confirm = bool(params.get("confirm", False))

        engine = get_memory_engine()
        report = engine.wipe(target_ring=target_ring, confirm=confirm)
        return _json_response(report)
    except Exception as exc:
        return _json_response({"status": "error", "message": str(exc)})


def memory_cli_status(raw_args: str = "", **kwargs: Any) -> str:
    """Slash command handler for Hermes Agent `/fractal` telemetry dashboard."""
    engine = get_memory_engine()
    stats = engine.inspect(detailed=False)
    rings = stats["rings"]

    output = [
        "🌀 Hermes Fractal Memory Telemetry 🌀",
        "========================================",
        f"State Seal : {stats['state_seal']}",
        f"Turn Count : {stats['turn_counter']} | Total Items: {stats['total_items']}",
        f"Data File  : {stats['storage_path']}",
        "----------------------------------------",
        f"• Ring 1 (Sensory 0.60x)  : {rings['sensory']['count']}/{rings['sensory']['capacity']} items (Decay: {rings['sensory']['decay_rate']:.2f})",
        f"• Ring 2 (Task 1.00x)     : {rings['task']['count']}/{rings['task']['capacity']} items (Decay: {rings['task']['decay_rate']:.2f})",
        f"• Ring 3 (Invariant 1.60x): {rings['invariant']['count']}/{rings['invariant']['capacity']} items (Decay: {rings['invariant']['decay_rate']:.2f})",
        "========================================",
        "Tip: Use /remember <key> <content> to pin an invariant rule directly.",
    ]
    return "\n".join(output)


def remember_cli_quick(raw_args: str = "", **kwargs: Any) -> str:
    """Slash command handler for Hermes Agent `/remember <key> <content>`."""
    if not raw_args or not str(raw_args).strip():
        return "Usage: /remember <key> <content>"

    parts = str(raw_args).strip().split(maxsplit=1)
    key = parts[0]
    content = parts[1] if len(parts) > 1 else key

    engine = get_memory_engine()
    item = engine.remember(
        key=key,
        content=content,
        ring="invariant",
        salience=0.95,
        tags=["cli_pinned"],
    )
    return (
        f"✅ Invariant memory pinned: [{item.key}] in Ring 3 (Invariant Core). "
        f"Seal: {engine.compute_state_seal()}"
    )
