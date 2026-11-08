"""
Hermes Agent Lifecycle Hooks (`pre_llm_call`, `post_llm_call`) for Fractal Memory Engine.
Seamlessly injects top resonant memories before LLM turns and applies orbital decay after.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from .memory_core import get_memory_engine
except (ImportError, ValueError):
    from memory_core import get_memory_engine  # type: ignore

logger = logging.getLogger("hermes.plugin.fractal_memory")


def _extract_prompt_text(args: tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    """Extract user message from Hermes `pre_llm_call` kwargs or turn context objects."""
    for key in ("user_message", "user_prompt", "prompt", "message", "input"):
        val = kwargs.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    if args:
        turn_context = args[0]
        if isinstance(turn_context, str) and turn_context.strip():
            return turn_context.strip()
        if hasattr(turn_context, "user_prompt") and turn_context.user_prompt:
            return str(turn_context.user_prompt).strip()
        if hasattr(turn_context, "user_message") and turn_context.user_message:
            return str(turn_context.user_message).strip()
        if isinstance(turn_context, dict):
            for key in ("user_message", "user_prompt", "prompt", "message", "input"):
                val = turn_context.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()

    history = kwargs.get("conversation_history")
    if isinstance(history, list):
        for msg in reversed(history):
            if isinstance(msg, dict) and msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

    return ""


def pre_llm_call_hook(*args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
    """
    Hook: `pre_llm_call`
    Fires once per turn before the tool-calling loop. Queries the 3-ring fractal
    memory manifold for top resonant memories and returns `{"context": mem_block}`
    so Hermes appends the recalled invariants to the current turn's user message.
    """
    try:
        engine = get_memory_engine()
        if not engine.auto_inject_context:
            return None

        prompt_text = _extract_prompt_text(args, kwargs)
        if not prompt_text or len(prompt_text) < 3:
            return None

        recalled = engine.recall(
            query=prompt_text,
            limit=3,
            min_resonance=engine.min_recall_resonance,
        )
        if not recalled:
            return None

        mem_lines = ["[FRACTAL-ACTIVE-MEMORY: Top Resonant Invariants & Context]"]
        for m in recalled:
            mem_lines.append(
                f"• [{m['ring'].upper()}] {m['key']}: {m['content']} (resonance={m['resonance']})"
            )
        mem_block = "\n".join(mem_lines)

        # Support legacy turn_context mutation in unit tests if passed positionally
        if args:
            turn_context = args[0]
            if hasattr(turn_context, "extra_system_context"):
                existing = getattr(turn_context, "extra_system_context", "") or ""
                turn_context.extra_system_context = (
                    f"{existing}\n{mem_block}".strip() if existing else mem_block
                )
            elif isinstance(turn_context, dict):
                existing = turn_context.get("extra_system_context", "") or ""
                turn_context["extra_system_context"] = (
                    f"{existing}\n{mem_block}".strip() if existing else mem_block
                )

        return {
            "context": mem_block,
            "action": "injected",
            "count": len(recalled),
            "memory_block": mem_block,
        }
    except Exception as exc:
        logger.debug("pre_llm_call_hook skipped on error: %s", exc)
        return None


def post_llm_call_hook(*args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
    """
    Hook: `post_llm_call`
    Fires once per turn after the tool-calling loop completes.
    Applies orbital decay to sensory & task rings, and triggers automatic
    consolidation when sensory buffer utilization reaches 75%.
    """
    try:
        engine = get_memory_engine()
        engine.step_decay()

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
    except Exception as exc:
        logger.debug("post_llm_call_hook skipped on error: %s", exc)
        return None


# Backwards-compatible aliases
fractal_pre_step_injector = pre_llm_call_hook
fractal_post_step_decay = post_llm_call_hook
