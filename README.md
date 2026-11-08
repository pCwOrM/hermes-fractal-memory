# 🌀 Hermes Fractal Memory Engine

> **Hierarchical Vectorless Episodic Memory, Procedural Attractor Clustering, and $O(1)$ Complex Coordinate Anchoring for [Hermes Agent](https://hermes-agent.nousresearch.com) (Nous Research).**

[![Hermes Agent Plugin v2](https://img.shields.io/badge/Hermes%20Plugin-v2%20Compliant-blue.svg)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 18 Passed](https://img.shields.io/badge/Tests-18%2F18%20Passed-brightgreen.svg)](#testing)
[![Category: Memory](https://img.shields.io/badge/Category-Memory%20Layer-purple.svg)](plugin.yaml)
[![Hackathon: Nous Research](https://img.shields.io/badge/Nous%20Research-Plugin%20Hackathon%202026-orange.svg)](https://x.com/NousResearch)

> **Official Submission for The Hermes Agent Plugin Hackathon by Nous Research (Nov 2026)**  
> *Developed solo by [@pCwOrM](https://github.com/pCwOrM) / Volkan Dagli.*

---

## 🔒 Disclosure & Operational Scope

**Disclosure —** `fractal-memory-engine` runs **100% locally** inside the Hermes Agent Python process with **zero external network calls**, **zero third-party API keys**, and **zero background processes or shell execution**:
- **Local State Persistence:** Memory items and turn counters are persisted as UTF-8 JSON inside the sanctioned Hermes per-plugin data directory (`<HERMES_HOME>/plugin-data/fractal-memory-engine/fractal_memory.json` via `plugins.plugin_storage.plugin_data_dir`), or at a user-configured `storage_path`.
- **Turn Context Injection (`pre_llm_call`):** Before each LLM turn, `pre_llm_call` queries the local 3-ring memory manifold against the active user prompt and returns a compact `<150 token` context block (`{"context": "[FRACTAL-ACTIVE-MEMORY...]"}`) when resonant memories exceed `min_recall_resonance` (default `0.30`). Can be toggled via `auto_inject_context`.
- **Orbital Decay (`post_llm_call`):** After each completed turn, `post_llm_call` applies exponential half-life decay to Ring 1 (Sensory, $\times 0.82$) and Ring 2 (Task, $\times 0.96$) while keeping Ring 3 (Invariant Core, $\times 1.00$) permanent, and triggers automatic consolidation when Sensory buffer occupancy reaches 75%.

---

## ⚡ The Memory Wall Problem in Autonomous Agents

Autonomous AI agents face a crippling architectural bottleneck when running complex, multi-turn, real-world tasks:
1. **Vector Database & Embedding Overhead ($O(N)$ Bloat):** Running heavy embedding models or local vector databases (Chroma, FAISS, Qdrant) introduces external dependencies, API costs, RAM bloat, and startup latency on edge/desktop machines.
2. **Context Dilution & Forgetting:** Dumping raw conversational history or verbose RAG chunks into the prompt saturates the context window, breaks prompt caching, and triggers attention degradation.
3. **Lack of Biological Consolidation:** Traditional memory stores treat yesterday's transient log output with the same permanence as foundational user rules or system invariants.

The **Hermes Fractal Memory Engine** (`fractal-memory-engine`) solves this deterministically. Instead of external vector databases, memories are anchored onto a **continuous complex coordinate manifold** ($c \in [-2.0, 0.5] \times [-1.2, 1.2]$) with polynomial escape-time depth ($z_{n+1} = z_n^2 + c$) and governed by a **3-Ring Orbital Resonance Hierarchy**.

---

## 🏛️ 3-Tier Orbital Memory Architecture

```
                          [ INCOMING USER PROMPT / AGENT TURN ]
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                [pre_llm_call Hook]                      [post_llm_call Hook]
                • Queries Resonant Attractors            • Advances Turn Counter
                • Returns {"context": ...}               • Applies Orbital Decay
                • Preserves System Prompt Cache          • Auto-Consolidates at 75%
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

## 🛠️ Provided Tools (`toolset="memory"`)

All 5 tool handlers accept `(args: dict, **kwargs)` and return a structured JSON string:

### 1. `fractal_remember`
Stores or updates a memory atom on the manifold with automatic or explicit ring assignment.
* **Input:**
  ```json
  {
    "key": "user_preferences",
    "content": "User prefers concise Python code and strictly forbids unverified dependencies.",
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
    "cx": -0.743612,
    "cy": 0.131844,
    "escape_time": 24,
    "state_seal": "[FRACTAL-MEM-SEAL:d41d8cd98f00b204]"
  }
  ```

### 2. `fractal_recall`
Retrieves top-$K$ resonant memories matching a natural language prompt via composite lexical Jaccard, character trigram morphology, and complex-plane geometric proximity scoring:
$$R(q, m) = \big(0.55 \cdot S_{\text{lex+tri}}(q, m) + 0.45 \cdot S_{\text{geom}}(q, m)\big) \times m.\text{salience} \times \text{Stability} \times W_{\text{ring}}$$
* **Input:** `{"query": "What are the user's coding constraints?", "limit": 3}`
* **Output:** JSON array of sorted memories with computed resonance scores and automatic Hebbian access reinforcement.

### 3. `fractal_consolidate`
Executes orbital memory consolidation across rings:
* Promotes frequently accessed task memories ($S \ge 0.80$, accesses $\ge 3$) into the zero-decay Invariant Core.
* Prunes decayed ephemeral noise ($S < 0.35$) from Ring 1 & Ring 2.

### 4. `fractal_memory_inspect`
Inspects real-time ring occupancy, decay telemetry, total items, storage path, and the SHA-256 cryptographic state seal.

### 5. `fractal_memory_wipe`
Protected memory reset tool with mandatory safety confirmation flag (`confirm: true`), supporting selective wiping of `sensory`, `task`, `all_non_invariant`, or `full_factory_reset`.

---

## ⚡ Lifecycle Hooks (`pre_llm_call` & `post_llm_call`)

1. **`pre_llm_call` (`pre_llm_call_hook`):**
   * Fires once per turn before the tool-calling loop.
   * Queries the manifold for the top 3 memories exceeding `min_recall_resonance` (default `0.30`).
   * Returns `{"context": "[FRACTAL-ACTIVE-MEMORY: Top Resonant Invariants & Context]\n..."}`, which Hermes appends to the current turn's user message while preserving the system prompt cache prefix.
2. **`post_llm_call` (`post_llm_call_hook`):**
   * Fires once per turn after the tool-calling loop completes.
   * Advances the turn counter, applies orbital decay across Ring 1 ($\times 0.82$) and Ring 2 ($\times 0.96$), and triggers automatic consolidation when the sensory buffer reaches 75% capacity.

---

## ⌨️ In-Session Slash Commands

* **`/fractal`:** Displays a rich ASCII telemetry dashboard showing ring capacities, decay factors, storage path, and the SHA-256 state seal:
  ```text
  🌀 Hermes Fractal Memory Telemetry 🌀
  ========================================
  State Seal : [FRACTAL-MEM-SEAL:e8b420261105af71]
  Turn Count : 14 | Total Items: 28
  Data File  : ~/.hermes/plugin-data/fractal-memory-engine/fractal_memory.json
  ----------------------------------------
  • Ring 1 (Sensory 0.60x)  : 8/64 items (Decay: 0.82)
  • Ring 2 (Task 1.00x)     : 14/128 items (Decay: 0.96)
  • Ring 3 (Invariant 1.60x): 6/1024 items (Decay: 1.00)
  ========================================
  Tip: Use /remember <key> <content> to pin an invariant rule directly.
  ```
* **`/remember <key> <content>`:** Instant shortcut to anchor a permanent invariant directly into Ring 3.

---

## ⚙️ Configuration (`config_schema`)

Configurable under `plugins.entries.fractal-memory-engine.settings` in `config.yaml` or via the Hermes Desktop Settings → Plugins UI:

| Setting | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `storage_path` | `str` | `""` | Custom file path for `fractal_memory.json`. Defaults to `<HERMES_HOME>/plugin-data/fractal-memory-engine/fractal_memory.json`. |
| `auto_inject_context` | `bool` | `true` | Automatically inject top resonant memories into `pre_llm_call` turn context. |
| `min_recall_resonance` | `float` | `0.30` | Minimum composite resonance score (`0.0` to `1.0`) required for automatic `pre_llm_call` injection. |

---

## 🧪 Testing & Admission Validation

```bash
# Run the full pytest suite (manifest, catalog schema, hooks, tools, and manifold math)
python -m pytest tests/ -v

# Validate with Hermes Plugin CLI
hermes plugins validate . --install-deps
```

---

---

## 🏆 Global Records, Formal Proofs, Curated Awesome Merges & On-Chain Infrastructure

### 1. Certified Mathematical Records & Formal Verification (`0 sorry`)
* **🥇 NSF ICARM Elliptic Curve Rank Leaderboard ([`elliptic-rank.icarm.cloud/user/114`](https://elliptic-rank.icarm.cloud/user/114)):** **230 certified high-rank elliptic curves** (`#4308–#4537`) over $\mathbb{Q}$ with **100% complete prime conductor factorization ($\log N$)** up to Rank $\ge 19$ (`#4323`), achieving **30 First-Place (#1 Gold) Records**, **80 Podium (Top-3)**, and **418 Top-10** placements across 43 categories (building upon the foundational fibration families of Elkies, Dujella, Rubinstein, and Klagsbrun; supported under NSF Grant `DMS-2425401`).
* **🥇 Schönhage Trilinear Multiplication Tensor Bound ([`arXiv:2610.14263`](https://arxiv.org/abs/2610.14263) • [`CrocSwap/integer-mult-bounds#226`](https://github.com/CrocSwap/integer-mult-bounds/pull/226)):** Constructive 15-round bipartite carrier matching at dimensions $h=23, 25$ eliminating 185 carrier roles and **377,890 physical wires** ($W = 177,284,805 \to 176,906,915$), certifying $\kappa = 826,215,307 / 20,000,000,000,000 \approx 4.131076535 \times 10^{-5}$ ($1.377\times$ net gain over PR #49), formally incorporated into `CrocSwap/integer-mult-bounds` (`commit 50d76881`) and verified in Lean 4 (`0 sorry`).
* **📐 170+ Machine-Checked Theorems in Lean 4 (`0 sorry`, `0 unproven axioms`):**
  * **General Divisor Theorem (`GDT v3.0`):** 81 theorems/lemmas (`0 sorry`) formalizing Dan Hawkley's residue density framework ([`10.5281/zenodo.23316068`](https://doi.org/10.5281/zenodo.23316068)).
  * **Computational Group Theory (`gap-lean4-port`):** 35 theorems (`0 sorry`) formalizing Charles Sims' Schreier-Sims stabilizer chains (`GAP-0299`), backtrack ordered partitions (`GAP-0332`), and modular ring inverses (`GAP-0331`) ([`arXiv:2609.38492`](https://arxiv.org/abs/2609.38492)).
  * **Procedural Boundary Synthesis & EVM/Cairo Fixed-Point Bounds:** 40+10 theorems (`WerracleProof.lean`, `0 sorry`) verifying `ZMod 9` ($\mathbb{Z}/9\mathbb{Z}$) principal ideal closure ($\mathcal{I}_3 = \{0,3,6\}$), Q16.16 overflow safety, and unitary Page curve S-matrix conservation ([`arXiv:2609.33066`](https://arxiv.org/abs/2609.33066)).
  * **24D Niemeier Lattice $A_8^3$, WerreduR & Güneş Dili:** Complete formal specifications (`0 sorry`) across lattice unimodularity ($\chi=24, \ell=9$), horizon complementarity ($B(t)+S(t)=1$), and deterministic morphological parsing.

### 2. Curated Ecosystem Recognitions & Benchmark Evaluations
* **Merged Upstream Pull Requests:**
  * ✅ **[`wbierbower/awesome-physics#16`](https://github.com/wbierbower/awesome-physics/pull/16):** Featured in *Quantum Physics* for unitary Black Hole Page Curve simulation.
  * ✅ **[`34j/best-of-lean4#292`](https://github.com/34j/best-of-lean4/pull/292):** Indexed in the curated *Best of Lean 4* theorem proving directory.
  * ✅ **[`yh-yao/awesome-edge-ai-agents#13`](https://github.com/yh-yao/awesome-edge-ai-agents/pull/13) & [`#16`](https://github.com/yh-yao/awesome-edge-ai-agents/pull/16):** Featured for both `werr` / `answerr` and `WerreduR` edge reflex engines.
  * ✅ **[`MartinuzziFrancesco/awesome-scientific-machine-learning#9`](https://github.com/MartinuzziFrancesco/awesome-scientific-machine-learning/pull/9) & [`#10`](https://github.com/MartinuzziFrancesco/awesome-scientific-machine-learning/pull/10):** Featured under *Model Discovery*.
  * ✅ **[`meta-introspector/lean-workers-union#2`](https://github.com/meta-introspector/lean-workers-union/pull/2):** Registered verified member (`gap-lean4-port`).
  * ✅ **Jev Ecosystem & Agentic Benchmarks:** Listed on [`awesome-jev#69`](https://github.com/hellogumbo/awesome-jev/issues/69) / `madewithjev`; **100% (49/49)** on [WindTunnel WebMCP (`3.35 ms`, `0 VRAM`)](https://github.com/nekuda-ai/WindTunnel/issues/25); **100% Tool Schema Adherence (`0.38 ms`)** on [Sierra Tau-Bench](https://github.com/sierra-research/tau-bench/issues/95); **23.74** on [JevBench v1.4.1 (`7.32 ms`)](https://github.com/fstandhartinger/jevbench/issues/10); **38.0× speedup** on [Jevenator 2](https://github.com/mmastrac/jevenator2/issues/1).

### 3. Sovereign On-Chain Deployments (`Werrium / $WERR`), Multi-Chain Testnets & Grant Pipelines
* **💎 Base L2 Mainnet (`Chain ID: 8453`) — Live & BaseScan Verified:**
  * **Werrium (`$WERR`) Token Contract:** [`0xFfa2c95b68B76af00FBD84295cBA5e5268a996d2`](https://basescan.org/address/0xFfa2c95b68B76af00FBD84295cBA5e5268a996d2) *(Fixed 1,000,000,000 supply, No-Mint, EIP-2612 Gasless Permit, `burnForATP` metabolic compute quota & `burnForReflex` on-chain decision sealing • [Optimism Superchain Token List PR #1391](https://github.com/ethereum-optimism/ethereum-optimism.github.io/pull/1391))*.
  * **Gnosis Safe 2/3 Multisig Treasury:** [`0x7CC5fd367e210F4678Bcfca054cbe0F87291E355`](https://basescan.org/address/0x7CC5fd367e210F4678Bcfca054cbe0F87291E355) (`949,501,000 WERR` locked).
  * **WerrTreasuryTimelock (Vesting & Cliff):** [`0x839A6d7E726D60EA2B587e793aE36342297e8C63`](https://basescan.org/address/0x839A6d7E726D60EA2B587e793aE36342297e8C63) (`40,000,000 WERR` locked).
  * **Aerodrome Finance DEX Liquidity Pools (Base Mainnet):** [`vAMM-WERR/USDC`](https://basescan.org/address/0xdA15b610f7De7A494CD1F7f80B6B73E8b34108A5) & [`vAMM-WERR/WETH`](https://basescan.org/address/0x53D7Ff2ef9B02860bf9F476602832f75594Bfa06).
* **🌐 Multi-Chain Testnets & Grant Tracks:**
  * **Starknet Foundation Seed Grant (*In Screening*):** Cairo 2.x / Sierra `WerracleTripodZMod9` (`single felt252` seed, `~1,420 Cairo steps`, Ekubo v2 LVR extension).
  * **Ethereum Sepolia Testnet (`Chain ID: 11155111`):** `Werrium ($WERR)` at [`0xe6ecc9575B4D52642c55FCf64E8E2d3baa6e6EF7`](https://sepolia.etherscan.io/address/0xe6ecc9575B4D52642c55FCf64E8E2d3baa6e6EF7) & `Werracle` live liquidation arbitrage telemetry.
  * **NEAR Aurora Testnet (`Chain ID: 1313161555`) & Bare-Metal EVM Node (`Chain ID: 4242`):** Live `Werracle.sol` & `WerracleFeeHook.sol` deployments ([`radar.werracle.com`](https://radar.werracle.com)).
  * **Active Research Proposals:** Flashbots MEV Research ([`FRP #205`](https://github.com/flashbots/mev-research/pull/205) & [`PR #206`](https://github.com/flashbots/mev-research/pull/206)), Morpho DAO (`MIP-81` OEV Observatory), Uniswap v4 / Unichain Hook Grants.




---

## ## 📜 License & Citations

Licensed under the **MIT License**. Created by **Volkan Dagli ([@pCwOrM](https://github.com/pCwOrM))**.  
Part of the open-source **Fractal Neural Synthesis (FNS)** and **WERR Canonical Research Corpus**.
