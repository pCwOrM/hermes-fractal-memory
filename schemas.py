"""
JSON Schemas for Hermes Fractal Memory Engine tools.
Compliant with Nous Research Hermes Plugin v2 specifications.
"""

FRACTAL_REMEMBER_SCHEMA = {
    "type": "object",
    "properties": {
        "key": {
            "type": "string",
            "description": "Unique identifier, topical anchor, or title for the memory item.",
        },
        "content": {
            "type": "string",
            "description": "Factual knowledge, user preference, instruction, or episodic memory to retain.",
        },
        "ring": {
            "type": "string",
            "enum": ["auto", "sensory", "task", "invariant"],
            "default": "auto",
            "description": (
                "Target memory ring: 'sensory' (short-term ephemeral buffer), "
                "'task' (mid-term active episodic context), 'invariant' (permanent core truth, zero decay), "
                "or 'auto' (determined dynamically via salience & tags)."
            ),
        },
        "salience": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.75,
            "description": "Initial salience weight. High salience (>=0.85) anchors closer to the invariant boundary.",
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Optional thematic keywords for resonant retrieval.",
        },
    },
    "required": ["key", "content"],
}

FRACTAL_RECALL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Natural language query, question, or keyword string to search across the memory manifold.",
        },
        "ring": {
            "type": "string",
            "enum": ["all", "sensory", "task", "invariant"],
            "default": "all",
            "description": "Restrict recall search to a specific ring, or search 'all' rings.",
        },
        "min_resonance": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.25,
            "description": "Minimum semantic and coordinate resonance threshold (0.0 to 1.0) to filter irrelevant items.",
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 20,
            "default": 5,
            "description": "Maximum number of most resonant memory items to return.",
        },
    },
    "required": ["query"],
}

FRACTAL_CONSOLIDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "retention_threshold": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 0.35,
            "description": "Items with salience below this threshold are pruned from sensory and task rings.",
        },
        "promote_threshold": {
            "type": "number",
            "minimum": 0.5,
            "maximum": 1.0,
            "default": 0.80,
            "description": "Frequently recalled task items with salience above this threshold are promoted to invariant.",
        },
        "prune_decayed": {
            "type": "boolean",
            "default": True,
            "description": "Whether to actively eliminate decayed low-resonance ephemeral entries.",
        },
    },
}

FRACTAL_MEMORY_INSPECT_SCHEMA = {
    "type": "object",
    "properties": {
        "detailed": {
            "type": "boolean",
            "default": False,
            "description": "If true, returns complete itemized entries per ring; if false, returns statistical telemetry and state seal.",
        },
        "ring": {
            "type": "string",
            "enum": ["all", "sensory", "task", "invariant"],
            "default": "all",
            "description": "Ring to inspect.",
        },
    },
}

FRACTAL_MEMORY_WIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "target_ring": {
            "type": "string",
            "enum": ["sensory", "task", "all_non_invariant", "full_factory_reset"],
            "default": "sensory",
            "description": (
                "Ring to clear: 'sensory' clears short-term buffer; 'task' clears active task context; "
                "'all_non_invariant' keeps invariants intact; 'full_factory_reset' clears everything."
            ),
        },
        "confirm": {
            "type": "boolean",
            "description": "Safety confirmation flag. Must be explicitly True to execute wipe.",
        },
    },
    "required": ["confirm"],
}
