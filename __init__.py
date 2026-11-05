"""
Hermes Fractal Memory Engine: Zero-Storage Episodic Memory and Attractor Manifold.
Official Plugin for Hermes Agent (Nous Research Plugin v2 Specification).
"""

try:
    from . import hooks, schemas, tools
except (ImportError, ValueError):
    import hooks, schemas, tools

__version__ = "1.0.0"
__author__ = "pCwOrM"


def register(ctx):
    """
    Register Fractal Memory Engine tools, lifecycle hooks, and CLI commands with Hermes Agent.

    Args:
        ctx: The Hermes plugin context instance.
    """
    # 1. Register Lifecycle Hooks (Pre-step memory recall & Post-step orbital decay)
    if hasattr(ctx, "register_hook"):
        ctx.register_hook("pre_agent_step", hooks.fractal_pre_step_injector)
        ctx.register_hook("post_agent_step", hooks.fractal_post_step_decay)

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

    # 3. Register Slash Commands
    if hasattr(ctx, "register_command"):
        ctx.register_command("/memory", tools.memory_cli_status)
        ctx.register_command("/remember", tools.remember_cli_quick)
