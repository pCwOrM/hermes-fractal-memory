"""
Hermes Agent Tool Handlers and CLI Commands for Fractal Memory Engine.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    from .memory_core import get_memory_engine
except (ImportError, ValueError):
    from memory_core import get_memory_engine


def fractal_remember_handler(params: Dict[str, Any], ctx: Optional[Any] = None) -> Dict[str, Any]:
    """Stores or updates a memory item on the fractal coordinate manifold."""
    key = params.get("key", "")
    content = params.get("content", "")
    ring = params.get("ring", "auto")
    salience = params.get("salience", 0.75)
    tags = params.get("tags", [])

    if not key or not content:
        return {"status": "error", "message": "Both 'key' and 'content' are required."}

    engine = get_memory_engine()
    item = engine.remember(key=key, content=content, ring=ring, salience=salience, tags=tags)

    return {
        "status": "stored",
        "key": item.key,
        "ring": item.ring,
        "salience": round(item.salience, 3),
        "cx": item.cx,
        "cy": item.cy,
        "escape_time": item.escape_time,
        "state_seal": engine.compute_state_seal(),
    }


def fractal_recall_handler(params: Dict[str, Any], ctx: Optional[Any] = None) -> Dict[str, Any]:
    """Retrieves top resonant memories from the manifold matching the query."""
    query = params.get("query", "")
    ring = params.get("ring", "all")
    min_resonance = params.get("min_resonance", 0.25)
    limit = params.get("limit", 5)

    if not query:
        return {"status": "error", "message": "'query' is required for fractal recall."}

    engine = get_memory_engine()
    results = engine.recall(
        query=query, ring=ring, min_resonance=min_resonance, limit=limit
    )

    return {
        "status": "success",
        "query": query,
        "count": len(results),
        "memories": results,
        "state_seal": engine.compute_state_seal(),
    }


def fractal_consolidate_handler(params: Dict[str, Any], ctx: Optional[Any] = None) -> Dict[str, Any]:
    """Consolidates active working memories into invariants and prunes decayed items."""
    retention_threshold = params.get("retention_threshold", 0.35)
    promote_threshold = params.get("promote_threshold", 0.80)
    prune_decayed = params.get("prune_decayed", True)

    engine = get_memory_engine()
    return engine.consolidate(
        retention_threshold=retention_threshold,
        promote_threshold=promote_threshold,
        prune_decayed=prune_decayed,
    )


def fractal_memory_inspect_handler(params: Dict[str, Any], ctx: Optional[Any] = None) -> Dict[str, Any]:
    """Inspects memory ring occupancy, telemetry, and state seal."""
    detailed = params.get("detailed", False)
    ring = params.get("ring", "all")

    engine = get_memory_engine()
    return engine.inspect(detailed=detailed, ring=ring)


def fractal_memory_wipe_handler(params: Dict[str, Any], ctx: Optional[Any] = None) -> Dict[str, Any]:
    """Safely wipes selected rings or resets the memory system."""
    target_ring = params.get("target_ring", "sensory")
    confirm = params.get("confirm", False)

    engine = get_memory_engine()
    return engine.wipe(target_ring=target_ring, confirm=confirm)


def memory_cli_status(args: Optional[str] = None, ctx: Optional[Any] = None) -> str:
    """CLI handler for Hermes Agent `/memory` slash command."""
    engine = get_memory_engine()
    stats = engine.inspect(detailed=False)
    rings = stats["rings"]

    output = [
        "🌀 Hermes Fractal Memory Telemetry 🌀",
        "========================================",
        f"State Seal: {stats['state_seal']}",
        f"Turn Count: {stats['turn_counter']} | Total Items: {stats['total_items']}",
        "----------------------------------------",
        f"• Ring 1 (Sensory 0.60x) : {rings['sensory']['count']}/{rings['sensory']['capacity']} items (Decay: {rings['sensory']['decay_rate']:.2f})",
        f"• Ring 2 (Task 1.00x)    : {rings['task']['count']}/{rings['task']['capacity']} items (Decay: {rings['task']['decay_rate']:.2f})",
        f"• Ring 3 (Invariant 1.60x: {rings['invariant']['count']}/{rings['invariant']['capacity']} items (Decay: {rings['invariant']['decay_rate']:.2f})",
        "========================================",
        "Tip: Use /remember <key> <content> to pin an invariant rule directly.",
    ]
    return "\n".join(output)


def remember_cli_quick(args: Optional[str] = None, ctx: Optional[Any] = None) -> str:
    """CLI handler for Hermes Agent `/remember` slash command."""
    if not args or not args.strip():
        return "Usage: /remember <key> <content>"

    parts = args.strip().split(maxsplit=1)
    key = parts[0]
    content = parts[1] if len(parts) > 1 else key

    engine = get_memory_engine()
    item = engine.remember(key=key, content=content, ring="invariant", salience=0.95, tags=["cli_pinned"])
    return f"✅ Invariant memory pinned: [{item.key}] in Ring 3 (Invariant Core). Seal: {engine.compute_state_seal()}"
