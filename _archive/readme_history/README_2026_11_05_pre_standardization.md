# 🌀 Hermes Fractal Memory Engine

> **Hierarchical Zero-Storage Episodic Memory, Procedural Attractor Clustering, and $O(1)$ Coordinate Anchoring for [Hermes Agent](https://hermes-agent.nousresearch.com) (Nous Research).**

[![Hermes Agent Plugin v2](https://img.shields.io/badge/Hermes%20Plugin-v2%20Compliant-blue.svg)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 15 Passed](https://img.shields.io/badge/Tests-15%2F15%20Passed-brightgreen.svg)](#testing)
[![Category: Memory](https://img.shields.io/badge/Category-Memory%20Layer-purple.svg)](plugin.yaml)
[![Hackathon: Nous Research](https://img.shields.io/badge/Nous%20Research-Plugin%20Hackathon%202026-orange.svg)](https://x.com/NousResearch)

> **Official Submission for The Hermes Agent Plugin Hackathon by Nous Research (Nov 2026)**  
> *Developed solo by [@pCwOrM](https://github.com/pCwOrM) / Volkan Dağlı.*

---

## ⚡ The Memory Wall Problem in Autonomous Agents

Autonomous AI agents face a crippling architectural bottleneck when running complex, multi-turn, real-world tasks:
1. **The Vector Database Bloat ($O(N)$ Spatial Explosion):** Storing millions of dense embedding vectors in RAM or local vector databases (Chroma, FAISS) causes linear latency growth, disk bloat, and heavy memory footprints on edge/desktop machines.
2. **Context Dilution & Forgetting:** Dumping conversational history or raw RAG chunks into the prompt saturates the context window, triggers attention degradation, and leads to hallucinations.
3. **No Organic Memory Consolidation:** Existing agents treat yesterday's transient API error with the same weight as permanent user preferences or foundational system invariants.

The **Hermes Fractal Memory Engine** (`fractal-memory-engine`) solves this fundamentally. Instead of maintaining static gigabytes of vector tables, memories are projected onto a **compact, continuous coordinate manifold** ($c \in \mathbb{C}$) and governed by a **3-Ring Orbital Resonance Hierarchy** with polynomial escape-time decay.

---

## 🏛️ 3-Tier Orbital Memory Architecture

Inspired by biological memory consolidation and procedural dynamical systems, memory is organized into 3 concentric orbit rings:

```
                          [ INCOMING USER PROMPT / AGENT EVENT ]
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
               [pre_agent_step Hook]                    [post_agent_step Hook]
               • Queries Resonant Attractors            • Intercepts New Facts
               • Injects [FRACTAL-ACTIVE-MEMORY]        • Applies Orbital Decay
               • Zero Context Dilution (<150 tokens)    • Auto-Consolidates at 75%
                        │                                         │
                        ▼                                         ▼
   ╔═════════════════════════════════════════════════════════════════════════════╗
   ║                   THE 3-TIER FRACTAL MEMORY MANIFOLD                        ║
   ║                                                                             ║
   ║   ┌─────────────────────────────────────────────────────────────────────┐   ║
   ║   │ Ring 1: Sensory Ephemeral Buffer (0.60x Zoom)                       │   ║
   ║   │ • Short-term conversational scratchpad (Capacity: 64 items)         │   ║
   ║   │ • Rapid half-life decay (γ = 0.82 / turn)                           │   ║
   ║   │ • Transient noise pruned automatically upon consolidation           │   ║
   ║   └──────────────────────────────────┬──────────────────────────────────┘   ║
   ║                                      │ (Hebbian Reinforcement: ≥2 hits)     ║
   ║                                      ▼                                      ║
   ║   ┌─────────────────────────────────────────────────────────────────────┐   ║
   ║   │ Ring 2: Contextual Task Memory (1.00x Zoom)                         │   ║
   ║   │ • Active task goals, intermediate tool outputs, active constraints  │   ║
   ║   │ • Gentle half-life decay (γ = 0.96 / turn)                          │   ║
   ║   │ • Promoted from Ring 1 when repeatedly referenced                   │   ║
   ║   └──────────────────────────────────┬──────────────────────────────────┘   ║
   ║                                      │ (High Salience Promotion: ≥0.80)     ║
   ║                                      ▼                                      ║
   ║   ┌─────────────────────────────────────────────────────────────────────┐   ║
   ║   │ Ring 3: Invariant Core Memory (1.60x Zoom - Invariant Attractor)   │   ║
   ║   │ • Permanent facts, user preferences, mathematical laws, identities  │   ║
   ║   │ • STRICT ZERO DECAY (γ = 1.00) — Inviolable ground truths           │   ║
   ║   │ • Governed by Boundary Dynamics (Polynomial Escape Resistance)      │   ║
   ║   └─────────────────────────────────────────────────────────────────────┘   ║
   ║                                                                             ║
   ║   [CRYPTOGRAPHIC STATE INTEGRITY SEAL: sha256 -> FRACTAL-MEM-SEAL:xxxx]     ║
   ╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## 🛠️ Provided Tools

### 1. `fractal_remember`
Stores or updates a memory atom on the manifold with automatic or explicit ring assignment.
* **Input Schema:**
  ```json
  {
    "key": "user_preferences",
    "content": "User prefers concise Python code and strictly forbids hallucinating library versions.",
    "ring": "invariant",
    "salience": 0.95,
    "tags": ["coding_rules", "python"]
  }
  ```
* **Output:**
  ```json
  {
    "status": "stored",
    "key": "user_preferences",
    "ring": "invariant",
    "salience": 0.95,
    "cx": -0.7436,
    "cy": 0.1318,
    "escape_time": 24,
    "state_seal": "[FRACTAL-MEM-SEAL:d41d8cd98f00b204]"
  }
  ```

### 2. `fractal_recall`
Retrieves top-$K$ resonant memories matching a natural language prompt via composite lexical and coordinate proximity scoring:
$$R(q, m) = \big(0.55 \cdot S_{\text{lex}}(q, m) + 0.45 \cdot S_{\text{geom}}(q, m)\big) \times m.\text{salience} \times \text{Stability} \times W_{\text{ring}}$$
* **Input:** `query: "What are the user's coding constraints?", "limit": 3`
* **Output:** Sorted memories with computed resonance coefficients and automatic Hebbian access tracking.

### 3. `fractal_consolidate`
Mimics biological slow-wave sleep memory consolidation:
* Promotes frequently accessed task memories ($S \ge 0.80$, accesses $\ge 3$) into the Invariant Core.
* Prunes decayed ephemeral noise ($S < 0.35$) from Ring 1 & Ring 2.

### 4. `fractal_memory_inspect`
Inspects real-time ring occupancy, decay telemetry, total items, and cryptographic state seals.

### 5. `fractal_memory_wipe`
Protected memory reset tool with safety confirmation flag (`confirm: true`), supporting selective wiping of sensory, task, or full reset.

---

## ⚡ Lifecycle Hooks

Hermes Agent executes autonomous loops. This plugin hooks into the agent lifecycle to make memory invisible, autonomous, and zero-effort:

1. **`pre_agent_step` (`fractal_pre_step_injector`):**
   * Intercepts the user message before tool execution.
   * Pulls the most resonant invariants and task memories ($R \ge 0.30$).
   * Injects a compact `<150 token` context block (`[FRACTAL-ACTIVE-MEMORY]`) directly into the agent's context.
2. **`post_agent_step` (`fractal_post_step_decay`):**
   * Advances the turn counter.
   * Applies orbital decay across Ring 1 ($\times 0.82$) and Ring 2 ($\times 0.96$).
   * Triggers automatic consolidation when the sensory buffer reaches 75% capacity.

---

## ⌨️ CLI Slash Commands

* **/memory:** Displays a rich ASCII telemetry dashboard showing ring capacities, decay factors, and state seals:
  ```text
  🌀 Hermes Fractal Memory Telemetry 🌀
  ========================================
  State Seal: [FRACTAL-MEM-SEAL:e8b420261105af71]
  Turn Count: 14 | Total Items: 28
  ----------------------------------------
  • Ring 1 (Sensory 0.60x) : 8/64 items (Decay: 0.82)
  • Ring 2 (Task 1.00x)    : 14/128 items (Decay: 0.96)
  • Ring 3 (Invariant 1.60x: 6/1024 items (Decay: 1.00)
  ========================================
  Tip: Use /remember <key> <content> to pin an invariant rule directly.
  ```
* **/remember `<key>` `<content>`:** Instant shortcut to anchor a permanent invariant directly into Ring 3.

---

## 🧪 Testing

The repository ships with an exhaustive automated test suite covering Plugin Doctor manifest validation, mathematical coordinate projection, Hebbian promotion, orbital decay, and tool handlers:

```bash
# Run the test suite
python -m pytest tests/ -v
```

```text
============================= test session starts =============================
collected 15 items

tests/test_doctor.py::test_manifest_structure PASSED                     [  6%]
tests/test_doctor.py::test_register_context_wiring PASSED                 [ 13%]
tests/test_hooks.py::test_pre_step_injection PASSED                       [ 20%]
tests/test_hooks.py::test_post_step_decay PASSED                          [ 26%]
tests/test_memory_core.py::test_coordinate_projection_bounds PASSED     [ 33%]
tests/test_memory_core.py::test_three_ring_auto_assignment PASSED        [ 40%]
tests/test_memory_core.py::test_recall_and_hebbian_promotion PASSED     [ 46%]
tests/test_memory_core.py::test_orbital_decay_and_consolidation PASSED   [ 53%]
tests/test_memory_core.py::test_cryptographic_state_seal PASSED          [ 60%]
tests/test_tools.py::test_fractal_remember_tool PASSED                    [ 66%]
tests/test_tools.py::test_fractal_recall_tool PASSED                      [ 73%]
tests/test_tools.py::test_fractal_memory_inspect_tool PASSED              [ 80%]
tests/test_tools.py::test_fractal_consolidate_tool PASSED                 [ 86%]
tests/test_tools.py::test_fractal_memory_wipe_protection PASSED          [ 93%]
tests/test_tools.py::test_cli_slash_commands PASSED                       [100%]

============================= 15 passed in 0.26s ==============================
```

---

## 📦 Installation & Submission to Hermes Catalog

1. Install into your local Hermes Agent environment:
   ```bash
   hermes plugins install pCwOrM/hermes-fractal-memory
   cd hermes-fractal-memory
   hermes plugins enable fractal-memory-engine
   ```
2. Validate with the Hermes Plugin CLI:
   ```bash
   hermes plugins validate .
   ```
3. Catalog Entry (`plugin-catalog/fractal-memory-engine.yaml`):
   ```yaml
   name: fractal-memory-engine
   repo: https://github.com/pCwOrM/hermes-fractal-memory
   sha: <LATEST_COMMIT_SHA>
   tier: community
   description: >-
     Hierarchical zero-storage episodic memory, procedural attractor clustering,
     and O(1) coordinate anchoring for Hermes Agent. Eliminates vector database bloat
     and context dilution via 3-ring orbital resonance decay.
   category: memory
   maintainer: pCwOrM
   capabilities:
     provides_tools:
       - fractal_remember
       - fractal_recall
       - fractal_consolidate
       - fractal_memory_inspect
       - fractal_memory_wipe
     provides_hooks:
       - pre_agent_step
       - post_agent_step
   requires_env: []
   ```

---

## 📜 License & Citations

Licensed under the **MIT License**. Created by **Volkan Dağlı ([@pCwOrM](https://github.com/pCwOrM))**.  
Part of the open-source **Fractal Neural Synthesis (FNS)** and **WERR Canonical Research Corpus**.
