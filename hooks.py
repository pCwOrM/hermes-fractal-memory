"""
Hermes Agent Lifecycle Hooks for Fractal Memory Engine.
Seamlessly injects salient memories before agent steps and applies orbital decay after.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from .memory_core import get_memory_engine
except (ImportError, ValueError):
    from memory_core import get_memory_engine

logger = logging.getLogger("hermes.plugin.fractal_memory")


def fractal_pre_step_injector(turn_context: Any) -> Optional[Dict[str, Any]]:
    """
    Hook: pre_agent_step
    Intercepts the incoming user prompt or task state, queries the fractal memory
    manifold for top resonant memories, and injects a compact contextual memory block.
    """
    engine = get_memory_engine()

    # Extract user message / prompt from turn context
    prompt_text = ""
    if hasattr(turn_context, "user_prompt"):
        prompt_text = str(turn_context.user_prompt)
    elif isinstance(turn_context, dict):
        prompt_text = turn_context.get("user_prompt") or turn_context.get("message") or turn_context.get("input", "")
    elif hasattr(turn_context, "get"):
        prompt_text = str(turn_context.get("prompt", ""))

    if not prompt_text or len(prompt_text.strip()) < 3:
        return None

    # Recall top 3 resonant items
    recalled = engine.recall(query=prompt_text, limit=3, min_resonance=0.30)
    if not recalled:
        return None

    # Construct concise memory block
    mem_lines = ["\n[FRACTAL-ACTIVE-MEMORY: Top Resonant Invariants & Context]"]
    for m in recalled:
        mem_lines.append(f"• [{m['ring'].upper()}] {m['key']}: {m['content']} (resonance={m['resonance']})")
    mem_block = "\n".join(mem_lines) + "\n"

    # Inject into turn context if supported
    if hasattr(turn_context, "extra_system_context"):
        if turn_context.extra_system_context:
            turn_context.extra_system_context += "\n" + mem_block
        else:
            turn_context.extra_system_context = mem_block
    elif isinstance(turn_context, dict):
        existing = turn_context.get("extra_system_context", "")
        turn_context["extra_system_context"] = f"{existing}\n{mem_block}".strip()

    return {"action": "injected", "count": len(recalled), "memory_block": mem_block}


def fractal_post_step_decay(turn_context: Any) -> Optional[Dict[str, Any]]:
    """
    Hook: post_agent_step
    Applies orbital decay to sensory & task rings, and triggers automatic consolidation
    when sensory buffer utilization exceeds 75%.
    """
    engine = get_memory_engine()

    # Apply turn decay
    engine.step_decay()

    # Check auto-consolidation threshold
    sensory_count = len(engine.rings["sensory"])
    auto_consolidated = False
    if sensory_count >= int(engine.CAP_SENSORY * 0.75):
        engine.consolidate(retention_threshold=0.35, promote_threshold=0.80)
        auto_consolidated = True

    return {
        "action": "decayed",
        "turn": engine.turn_counter,
        "auto_consolidated": auto_consolidated,
        "state_seal": engine.compute_state_seal(),
    }
