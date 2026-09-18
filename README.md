# Minecraft Java Edition MCP Server 2.0

[![MCP Protocol](https://img.shields.io/badge/MCP-2.0-blue.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-green.svg)](https://www.python.org/)
[![Transport](https://img.shields.io/badge/Transport-stdio-orange.svg)](https://py.sdk.modelcontextprotocol.io/)
[![Minecraft](https://img.shields.io/badge/Minecraft-Java%2026.2-red.svg)](https://www.minecraft.net/)
[![Fabric](https://img.shields.io/badge/Fabric-0.18.4%2B-brightgreen.svg)](https://fabricmc.net/)
[![Tests Passing](https://img.shields.io/badge/Tests-68%2F68%20Passing-brightgreen.svg)](scripts/)
[![Token Reduction](https://img.shields.io/badge/Token%20Reduction-99.81%25-blueviolet.svg)](docs/architecture/token-consumption-audit.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous **Model Context Protocol (MCP 2.0)** server for **Minecraft Java Edition 26.2**. Designed for AI agents and LLMs (Google Antigravity, Claude Desktop, custom agentic loops), this server connects standard I/O (`stdio` JSON-RPC 2.0) to an embedded **Fabric Mod Bridge** via high-speed localhost REST and WebSocket protocols (`:25585`).

---

## 💥 The Token Reduction Revolution: Voxel-Batching vs. Procedural Geometry IR

### The Legacy Problem
In legacy Minecraft agent implementations, LLMs were forced to act as **raw voxel coordinate generators**:
```json
[
  {"x": -140, "y": 70, "z": 80, "block": "minecraft:smooth_sandstone"},
  {"x": -140, "y": 70, "z": 81, "block": "minecraft:smooth_sandstone"},
  ...
]
```
This created an exponential **Token Penalty**:
- A single batch of 300 voxels consumed **~5,500 to 7,200 tokens**.
- Constructing a 50,000-block monument required transmitting coordinate arrays totaling **over 1,200,000 tokens**.
- Saturated context windows, caused repeated transcript compactions, degraded reasoning, and led to frequent stream timeouts.

### The Procedural Geometry IR Solution
In Phases 4 & 5, we fundamentally transformed the system into a **Procedural Construction Engine**:
```text
LLM / Lead Architect
      ↓ (Compact Semantic Intent < 150 tokens)
Geometry Intermediate Representation (JSON AST)
      ↓
Terrain-Adaptive Foundation Engine (Solid Underpinning to Bedrock)
      ↓
Composition & CSG Engine (Radial Arrays, Lofts, Parametric Arches/Domes)
      ↓
3D Greedy Cuboid Mesher (153x Compression Ratio)
      ↓ (Slashing Bridge Mutations by 85–98%)
Minecraft Engine Execution (fill_region <= 500 blocks)
      ↓
Compact Verification Digest (< 80 tokens, 0 raw coordinate dumps)
```

### Empirical Token Benchmark: Burj Khalifa Mega-Skyscraper (255 Blocks Tall)

| Construction Metric | Legacy Voxel-Batching (Projected) | Procedural Geometry IR (Actual) | Improvement Factor |
| :--- | :--- | :--- | :--- |
| **Total Blocks Placed** | 113,886 blocks | **113,886 blocks** | Exact 1:1 Scale |
| **MCP Tool Calls** | ~380 sequential batches | **13 MCP tool calls** | **29.2× fewer calls** |
| **Bridge Fill Operations** | 113,886 block calls | **743 greedy cuboid calls** | **153.3× compression** |
| **Total Chat Tokens** | > 1,545,000 tokens | **2,855 tokens total** | **99.81% token reduction** |
| **Verification Context** | ~95,000 tokens (voxel dumps) | **~350 tokens** (compact digests) | **270× reduction** |
| **Build Latency** | ~45–60 minutes | **< 3 minutes** | **20× faster** |
| **Failures / Timeouts** | Context blowout & stream timeouts | **0 errors, 0 truncations** | **100% Reliable** |

*For complete historical data across the Roman Colosseum, Rani ki Vav Stepwell, and Burj Khalifa, see the [Token Consumption Audit](docs/architecture/token-consumption-audit.md).*

---

## 🏛️ Autonomous Architectural Monuments (100% Physically Verified)

| Monument | Location | Total Blocks | Build Strategy | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Burj Khalifa Mega-Skyscraper** | `(-160, 65, 40)` | **113,886** | 255-block tri-axial procedural loft with 26 spiraling setbacks | **100.0% VALID** (2,855 tokens total) |
| **Roman Colosseum Arena & Arcade** | `(-140, 69, 80)` | **13,286** | 2-tier 24-radial arch arcade with 4 cavea seating tiers | **100.0% VALID** (18.77s build time) |
| **The Taj Mahal Mausoleum** | `(-181, 74, 167)` | **3,859** | Octagonal plinth, 4 pishtaq iwans, onion dome & 4 minarets | **100.0% VALID** (0 discrepancies) |
| **Qutub Minar & Iron Pillar** | `(-234, 69, 194)` | **2,592** | 5 tapering tiers, 24 alternating flutings, muqarnas balconies | **100.0% VALID** (0 discrepancies) |

---

## 👥 Phase 5: Multi-Agent Architectural Guild

Phase 5 establishes a cooperative multi-agent construction guild orchestrated through a shared, thread-safe memory blackboard:

```
                          ┌───────────────────────────┐
                          │       Lead Architect      │
                          │ (Antigravity / LLM Agent) │
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────┬───────┴────────────┬────────────────────┐
           ▼                    ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Site Surveyor   │ │ Structural Mason │ │  Artisan Carver  │ │   QA Inspector   │
│ Probes ground &  │ │ Instantiates     │ │ Carves columns,  │ │ Audits volume,   │
│ establishes datum│ │ procedural shell │ │ keystones & lamps│ │ certifies build  │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
           │                    │                    │                    │
           └────────────────────┴─────────┬──────────┴────────────────────┘
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ Shared Blackboard & Collision Guard   │
                      │ minecraft://orchestration/blackboard  │
                      │ minecraft://orchestration/roster      │
                      │ minecraft://inspection/scorecard      │
                      └───────────────────────────────────────┘
```

### Built-in Parameterized Prefabs (`src/minecraft_mcp/procedural/templates_library.py`)
1. `greek_peripteral_temple`: 3-stepped stylobate, 16 Doric columns, cella sanctuary, pediments.
2. `roman_colosseum_complex`: Radial 2-tier Roman arcades, concentric cavea seating, hypogeum arena.
3. `gothic_cathedral_complex`: Pointed rib vaults, clerestory lancets, rose window, twin bell towers with spires.
4. `mughal_monument_complex`: Marble plinth, 4 pishtaq iwans, double onion dome, 4 corner minarets.
5. `medieval_castle_fortress`: Crenellated curtain walls, 4 corner round bastions, portcullis gatehouse, keep.
6. `islamic_fluted_minaret`: Tapered shaft, alternating circular/angular fluting, muqarnas balconies, cupola.

---

## 🛠️ Complete MCP 2.0 Surface

The server exposes **47 Tools**, **17 Dynamic Resources**, and **13 Prompts**:

### Tool Highlights
- **Procedural Engine**: `build_procedural`, `create_geometry_session`, `add_primitive`, `compose_geometry`, `define_template`, `instantiate_template`, `compile_and_build`, `verify_structure_compact`, `rollback_build`.
- **Multi-Agent Orchestration**: `update_blackboard`, `update_subagent_status`, `assign_spatial_zone`, `release_spatial_zone`, `record_progress_milestone`, `update_inspection_scorecard`.
- **Spatial Intelligence**: `find_build_location`, `navigate_to`, `build_structure`, `build_wall`, `build_roof`, `repair_structure`, `check_requirements`.
- **World & Player Primitives**: `place_blocks`, `fill_region`, `break_block`, `interact_with_block`, `get_player_position`, `get_player_state`, `inspect_area`, `teleport`, `move_to`.

### Dynamic Resources (`minecraft://...`)
- `minecraft://orchestration/blackboard`: Real-time inter-agent memory state.
- `minecraft://orchestration/roster`: Subagent lifecycle states (`ASSIGNED`, `WORKING`, `COMPLETED`).
- `minecraft://construction/progress`: Milestone progression percentages.
- `minecraft://inspection/scorecard`: Structural verification scores and certification status.
- `minecraft://geometry/templates`: Catalog of parametric architectural prefabs.
- `minecraft://world/map`: 2D/3D compressed voxel cartography.
- `minecraft://player/position`: Real-time player coordinate updates.

### Prompts
- `orchestrate_architectural_team`: Master prompt for the Lead Architect.
- `build_monument_from_template`: One-shot parametric monument construction.
- `survey_and_prep_site`: Execution instructions for the Site Surveyor.
- `construct_procedural_shell`: Execution instructions for the Structural Mason.
- `detail_and_furnish`: Execution instructions for the Artisan Carver.
- `inspect_and_certify`: Execution instructions for the QA Inspector.

---

## 🚀 Quick Start

### 1. Launch Dedicated Minecraft Fabric Server
Make sure the Fabric Server for **Minecraft Java 26.2** is running with the embedded bridge mod on port 25585:
```bash
cd fabric-mod
./gradlew runServer
```
*Verify bridge health: `curl -s http://127.0.0.1:25585/api/v1/status | jq .`*

### 2. Environment Configuration
```bash
export FABRIC_BRIDGE_URL="http://127.0.0.1:25585"
export FABRIC_WS_URL="ws://127.0.0.1:25585/api/v1/ws/player"
export MINECRAFT_TARGET_PLAYER="AtomOtos"
```

### 3. Run MCP Server in Stdio Mode
```bash
# Using uv
uv run -m minecraft_mcp

# Or using standard python virtual environment
source .venv/bin/activate
python -m minecraft_mcp
```

### 4. Client Integration Configuration

#### Claude Desktop / Antigravity (`mcp_config.json`):
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "/Users/arhamowais/minecraft-mcp/.venv/bin/python",
      "args": ["-m", "minecraft_mcp"],
      "cwd": "/Users/arhamowais/minecraft-mcp",
      "env": {
        "FABRIC_BRIDGE_URL": "http://127.0.0.1:25585",
        "FABRIC_WS_URL": "ws://127.0.0.1:25585/api/v1/ws/player",
        "MINECRAFT_TARGET_PLAYER": "AtomOtos"
      }
    }
  }
}
```

---

## 🧪 Comprehensive Automated Test Suites

The server features 68 automated integration tests across 5 vertical slices:

```bash
# Run full automated regression suite (68 / 68 passing)
python scripts/test_phase1_client.py  # Phase 1: Observation Stack (20/20 PASS)
python scripts/test_phase2_client.py  # Phase 2: Mutation & Locomotion (12/12 PASS)
python scripts/test_phase3_client.py  # Phase 3: Spatial Intelligence (12/12 PASS)
python scripts/test_phase4_client.py  # Phase 4: Procedural Geometry IR (12/12 PASS)
python scripts/test_phase5_client.py  # Phase 5: Multi-Agent Guild (12/12 PASS)
```

---

## 📦 Packaging & Future Distribution Roadmap

As part of our packaging milestones, the project is structured for easy distribution and setup:
1. **PyPI Package (`minecraft-mcp`)**: Build standard wheels via `uv build` for direct installation (`pip install minecraft-mcp` or `uv tool install minecraft-mcp`).
2. **Pre-Compiled Fabric Bridge Releases**: Pre-built `.jar` binaries shipped with GitHub Releases for vanilla/Fabric 26.2 dedicated servers.
3. **One-Command Bootstrap CLI**: Future `minecraft-mcp setup` to automatically provision a local Fabric dedicated server environment.
4. **Containerized Sandbox**: Pre-configured Docker images containing both the headless Minecraft engine and MCP bridge.

---

## 📚 Complete Documentation Portal
- 📖 [Documentation Portal Index](docs/README.md)
- 📊 [Token Consumption Audit](docs/architecture/token-consumption-audit.md)
- ⚙️ [Procedural Construction Engine Specification](docs/architecture/phase4-procedural-engine.md)
- 👥 [Multi-Agent Guild Architecture](docs/architecture/phase5-multi-agent-guild.md)
- 📋 [Implementation Rules](implementation.md)
- 🗺️ [5-Phase Verification Plan](phase.md)

---

## 📄 License
MIT License. Copyright (c) 2026 Antigravity & AtomOtos.
