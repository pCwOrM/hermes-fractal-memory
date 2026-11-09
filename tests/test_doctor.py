"""
Compliance and manifest integrity tests for Hermes Plugin Validate & Catalog Validator.
Verifies strict compliance with `hermes_cli/plugin_validate.py` and `scripts/validate_plugin_catalog.py`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

import yaml

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

import __init__ as plugin_module  # noqa: E402


class MockHermesContext:
    def __init__(self, custom_config: Dict[str, Any] | None = None) -> None:
        self.hooks: Dict[str, Callable[..., Any]] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.commands: Dict[str, Dict[str, Any]] = {}
        self._config: Dict[str, Any] = custom_config or {}

    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def register_hook(
        self, event_name: str, callback: Callable[..., Any], **kwargs: Any
    ) -> None:
        self.hooks[event_name] = callback

    def register_tool(
        self,
        name: str,
        toolset: str,
        schema: Dict[str, Any],
        handler: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        self.tools[name] = {
            "toolset": toolset,
            "schema": schema,
            "handler": handler,
        }

    def register_command(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
        args_hint: str = "",
        **kwargs: Any,
    ) -> None:
        self.commands[name] = {
            "handler": handler,
            "description": description,
            "args_hint": args_hint,
        }


def test_manifest_top_level_structure() -> None:
    manifest_path = PLUGIN_DIR / "plugin.yaml"
    assert manifest_path.exists()

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["name"] == "fractal-memory-engine"
    assert "version" in manifest
    assert "description" in manifest
    assert manifest["requires_hermes"] == ">=0.21.0"

    # Must be at top level for hermes_cli/plugin_validate.py
    assert "capabilities" not in manifest
    assert isinstance(manifest.get("provides_hooks"), list)
    assert set(manifest["provides_hooks"]) == {"pre_llm_call", "post_llm_call"}

    assert isinstance(manifest.get("provides_tools"), list)
    assert set(manifest["provides_tools"]) == {
        "fractal_remember",
        "fractal_recall",
        "fractal_consolidate",
        "fractal_memory_inspect",
        "fractal_memory_wipe",
    }
    assert manifest.get("requires_env") == []
    assert "config_schema" in manifest
    assert "storage_path" in manifest["config_schema"]
    assert "auto_inject_context" in manifest["config_schema"]
    assert "min_recall_resonance" in manifest["config_schema"]


def test_register_context_wiring_and_schemas() -> None:
    manifest = yaml.safe_load((PLUGIN_DIR / "plugin.yaml").read_text(encoding="utf-8"))
    ctx = MockHermesContext(
        custom_config={"auto_inject_context": True, "min_recall_resonance": 0.28}
    )
    plugin_module.register(ctx)

    # Exact capability parity required by hermes plugins validate
    assert set(ctx.hooks.keys()) == set(manifest["provides_hooks"])
    assert set(ctx.tools.keys()) == set(manifest["provides_tools"])

    # Verify each tool schema carries name, description, parameters and uses dedicated toolset
    for tool_name, entry in ctx.tools.items():
        assert entry["toolset"] == "fractal_memory"
        schema = entry["schema"]
        assert schema["name"] == tool_name
        assert isinstance(schema.get("description"), str) and len(schema["description"]) > 10
        assert isinstance(schema.get("parameters"), dict)
        assert schema["parameters"].get("type") == "object"

    # Verify slash commands registered without leading slash
    assert "fractal" in ctx.commands
    assert "remember" in ctx.commands


def test_catalog_entry_schema_compliance() -> None:
    catalog_path = PLUGIN_DIR / "hermes-catalog-entry.yaml"
    assert catalog_path.exists()
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))

    required_keys = {"name", "repo", "sha", "description", "maintainer"}
    known_keys = {
        "name",
        "repo",
        "sha",
        "subdir",
        "description",
        "maintainer",
        "tier",
        "category",
        "requires_hermes",
        "docs_url",
        "version",
        "image",
        "screenshots",
        "readme",
        "platforms",
        "capabilities",
        "title",
        "onboarding",
        "known_issues",
        "attested_binaries",
    }
    capability_keys = {
        "provides_tools",
        "provides_hooks",
        "provides_middleware",
        "requires_env",
    }

    assert required_keys.issubset(data.keys())
    assert set(data.keys()).issubset(known_keys)
    assert set(data["capabilities"].keys()).issubset(capability_keys)
    assert data["name"] == "fractal-memory-engine"
    assert data["maintainer"] == "pCwOrM"
    assert data["category"] == "memory"
    assert data["tier"] == "community"
    assert set(data["capabilities"]["provides_hooks"]) == {
        "pre_llm_call",
        "post_llm_call",
    }
