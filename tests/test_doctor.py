"""Compliance and manifest integrity tests for Hermes Plugin Doctor."""

import os
import sys
import yaml

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

import __init__ as plugin_module


class MockHermesContext:
    def __init__(self):
        self.hooks = {}
        self.tools = {}
        self.commands = {}

    def register_hook(self, event_name, callback):
        self.hooks[event_name] = callback

    def register_tool(self, name, toolset, schema, handler):
        self.tools[name] = {"toolset": toolset, "schema": schema, "handler": handler}

    def register_command(self, cmd_name, callback):
        self.commands[cmd_name] = callback


def test_manifest_structure():
    manifest_path = os.path.join(PLUGIN_DIR, "plugin.yaml")
    assert os.path.exists(manifest_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    assert manifest["name"] == "fractal-memory-engine"
    assert manifest["maintainer"] == "pCwOrM"
    assert manifest["category"] == "memory"
    assert manifest["tier"] == "community"

    # Verify hooks
    hooks_list = manifest["capabilities"]["provides_hooks"]
    assert "pre_agent_step" in hooks_list
    assert "post_agent_step" in hooks_list

    # Verify tools
    tools_list = manifest["capabilities"]["provides_tools"]
    assert "fractal_remember" in tools_list
    assert "fractal_recall" in tools_list
    assert "fractal_consolidate" in tools_list
    assert "fractal_memory_inspect" in tools_list
    assert "fractal_memory_wipe" in tools_list


def test_register_context_wiring():
    ctx = MockHermesContext()
    plugin_module.register(ctx)

    # Verify hooks registered
    assert "pre_agent_step" in ctx.hooks
    assert "post_agent_step" in ctx.hooks

    # Verify tools registered
    assert "fractal_remember" in ctx.tools
    assert "fractal_recall" in ctx.tools
    assert "fractal_consolidate" in ctx.tools
    assert "fractal_memory_inspect" in ctx.tools
    assert "fractal_memory_wipe" in ctx.tools

    # Verify slash commands
    assert "/memory" in ctx.commands
    assert "/remember" in ctx.commands
