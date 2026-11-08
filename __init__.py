"""
Hermes Fractal Memory Engine: Vectorless Episodic Memory and Attractor Manifold.
Official Plugin for Hermes Agent (Nous Research Plugin v2 Specification).
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from . import hooks, schemas, tools
    from .memory_core import get_memory_engine
except (ImportError, ValueError):
    import hooks  # type: ignore
    import schemas  # type: ignore
    import tools  # type: ignore
    from memory_core import get_memory_engine  # type: ignore

__version__ = "1.0.1"
__author__ = "Volkan Dagli"

logger = logging.getLogger(__name__)


def _read_config(ctx: Any, key: str, default: Any = None) -> Any:
    """Safely read a plugin setting from Hermes PluginContext."""
    getter = getattr(ctx, "get_config", None)
    if callable(getter):
        try:
            val = getter(key, default)
            return default if val is None else val
        except TypeError:
            try:
                cfg = getter()
                if isinstance(cfg, dict):
                    return cfg.get(key, default)
            except Exception:
                pass
    cfg_dict = getattr(ctx, "plugin_config", None) or getattr(ctx, "config", None)
    if isinstance(cfg_dict, dict):
        return cfg_dict.get(key, default)
    return default


def register(ctx: Any) -> None:
    """
    Register Fractal Memory Engine tools, lifecycle hooks, and slash commands with Hermes Agent.
    """
    storage_path = _read_config(ctx, "storage_path", "")
    auto_inject = _read_config(ctx, "auto_inject_context", True)
    min_resonance = _read_config(ctx, "min_recall_resonance", 0.30)

    engine = get_memory_engine()
    engine.configure(
        storage_path=storage_path if storage_path else None,
        auto_inject_context=bool(auto_inject),
        min_recall_resonance=float(min_resonance),
    )

    # 1. Register Lifecycle Hooks (`pre_llm_call` context injection & `post_llm_call` orbital decay)
    if hasattr(ctx, "register_hook"):
        ctx.register_hook("pre_llm_call", hooks.pre_llm_call_hook)
        ctx.register_hook("post_llm_call", hooks.post_llm_call_hook)

    # 2. Register Interactive Fractal Memory Tools
    if hasattr(ctx, "register_tool"):
        ctx.register_tool(
            name="fractal_remember",
            toolset="memory",
            schema=schemas.FRACTAL_REMEMBER_SCHEMA,
            handler=tools.fractal_remember_handler,
        )
        ctx.register_tool(
            name="fractal_recall",
            toolset="memory",
            schema=schemas.FRACTAL_RECALL_SCHEMA,
            handler=tools.fractal_recall_handler,
        )
        ctx.register_tool(
            name="fractal_consolidate",
            toolset="memory",
            schema=schemas.FRACTAL_CONSOLIDATE_SCHEMA,
            handler=tools.fractal_consolidate_handler,
        )
        ctx.register_tool(
            name="fractal_memory_inspect",
            toolset="memory",
            schema=schemas.FRACTAL_MEMORY_INSPECT_SCHEMA,
            handler=tools.fractal_memory_inspect_handler,
        )
        ctx.register_tool(
            name="fractal_memory_wipe",
            toolset="memory",
            schema=schemas.FRACTAL_MEMORY_WIPE_SCHEMA,
            handler=tools.fractal_memory_wipe_handler,
        )

    # 3. Register In-Session Slash Commands (/fractal, /remember)
    if hasattr(ctx, "register_command"):
        try:
            ctx.register_command(
                name="fractal",
                handler=tools.memory_cli_status,
                description="Show Fractal Memory Engine 3-ring telemetry, occupancy, and SHA-256 state seal",
            )
            ctx.register_command(
                name="remember",
                handler=tools.remember_cli_quick,
                description="Pin a permanent invariant memory into Ring 3 (Usage: /remember <key> <content>)",
            )
        except TypeError:
            ctx.register_command("fractal", tools.memory_cli_status)
            ctx.register_command("remember", tools.remember_cli_quick)

    logger.info("Fractal Memory Engine v1.0.1 registered with Hermes Agent.")
