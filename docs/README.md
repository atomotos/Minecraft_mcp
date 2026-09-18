# Minecraft Java Edition MCP Server 2.0 — Documentation Portal

Welcome to the comprehensive documentation for the **Minecraft Java Edition Model Context Protocol (MCP 2.0) Server**. This project connects Large Language Models (LLMs) and autonomous AI agent platforms to **Minecraft Java Edition 26.2** via standard I/O (`stdio` JSON-RPC 2.0), communicating with an embedded **Fabric Mod Bridge** on port `25585`.

---

## 🧭 Documentation Map

| Section | Document | Description |
| :--- | :--- | :--- |
| **System Architecture** | [architecture.md](architecture.md) | High-level system topology, stdio transport, Netty HTTP/WS bridge, thread-safe tick dispatch, and Mojang bytecode integration. |
| **Token Consumption Audit** | [token-consumption-audit.md](architecture/token-consumption-audit.md) | **Empirical Token Reduction Audit**: 99.81% token savings, 153.3× greedy meshing compression, Burj Khalifa & Colosseum benchmarks. |
| **Procedural Engine (Phase 4)** | [phase4-procedural-engine.md](architecture/phase4-procedural-engine.md) | Geometry IR, continuous SDFs, affine transforms, greedy cuboid meshing, adaptive foundations, and compact verification. |
| **Multi-Agent Guild (Phase 5)** | [phase5-multi-agent-guild.md](architecture/phase5-multi-agent-guild.md) | Shared blackboard memory, subagent roster tracking, 3D spatial zoning collision guards, and 6 built-in architectural templates. |
| **Implementation Rules** | [implementation.md](../implementation.md) | The 30 non-negotiable engineering rules, layer separation, zero-guessing policy, and bottom-up phase gates. |
| **5-Phase Execution Plan** | [phase.md](../phase.md) | Complete 5-phase delivery status, automated test results (68/68 passing), and monument verification records. |
| **Autonomous Agents** | [agents.md](agents.md) | Lead Architect, Site Surveyor, Structural Mason, Artisan Carver, and QA Inspector agent workflows. |
| **MCP Resources** | [resources.md](resources.md) | Full specification of 17 dynamic resources (`minecraft://world/map`, `minecraft://orchestration/blackboard`, etc.). |
| **MCP Prompts** | [prompts.md](prompts.md) | Built-in MCP Prompt templates: `/orchestrate_architectural_team`, `/survey_and_prep_site`, `/construct_procedural_shell`, etc. |
| **Primitive Tools** | [primitives.md](tools/primitives.md) | Complete reference manual for all low-level tools: observation, block placement, movement, and inventory. |
| **High-Level Tools** | `docs/tools/high_level/` | Dedicated deep-dive specifications for composite high-level building and spatial intelligence capabilities. |

---

## 🛠️ High-Level Tools Directory

- [build_structure.md](tools/high_level/build_structure.md) — Generic blueprint-driven architectural constructor (towers, bridges, walls, castles, houses).
- [build_wall.md](tools/high_level/build_wall.md) — Wall, curtain barrier, and battlement constructor.
- [build_roof.md](tools/high_level/build_roof.md) — Pitched, hip, flat, and dome roof generator.
- [build_floor.md](tools/high_level/build_floor.md) — Multi-layer flooring tool with bounding box leveling.
- [build_door.md](tools/high_level/build_door.md) — Doorway frame cutter and door installer.
- [build_window.md](tools/high_level/build_window.md) — Window aperture generator and glass pane installer.
- [build_house.md](tools/high_level/build_house.md) — Autonomous residential building orchestrator.
- [find_build_location.md](tools/high_level/find_build_location.md) — Spatial terrain analyzer for flatness, slope, and clearing cost.
- [navigate_to.md](tools/high_level/navigate_to.md) — 3D A* pathfinding and movement orchestration across uneven terrain.
- [repair_structure.md](tools/high_level/repair_structure.md) — Verification-driven structural discrepancy detector and repairer.
- [check_requirements.md](tools/high_level/check_requirements.md) — Blueprint bill-of-materials and inventory deficit analyzer.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.12+ (managed with `uv`)
- OpenJDK 25 (`/opt/homebrew/opt/openjdk@25`)
- Minecraft Java Edition 26.2 Dedicated Server running Fabric Loader 0.18.4+ and Fabric API 0.152.1+26.2
- Embedded Bridge Mod (`fabric-mod/`) running on port `25585`

### 2. Launch Dedicated Minecraft Fabric Server
```bash
cd fabric-mod
./gradlew runServer
```
*The bridge starts an embedded Netty server listening on `http://127.0.0.1:25585` (REST) and `ws://127.0.0.1:25585/api/v1/ws/player` (WebSocket).*

### 3. Environment Configuration
```bash
export FABRIC_BRIDGE_URL="http://127.0.0.1:25585"
export FABRIC_WS_URL="ws://127.0.0.1:25585/api/v1/ws/player"
export MINECRAFT_TARGET_PLAYER="AtomOtos"
```

### 4. Run MCP Server in Stdio Mode
```bash
uv run -m minecraft_mcp
# or with virtualenv activated
python -m minecraft_mcp
```

### 5. Client Integration (e.g. Claude Desktop / Antigravity)
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

## 🧪 Automated Verification Suites

The repository contains 5 comprehensive automated verification suites covering all 68 integration tests:

```bash
python scripts/test_phase1_client.py  # Phase 1: Observation Stack (20/20 PASS)
python scripts/test_phase2_client.py  # Phase 2: Mutation & Locomotion (12/12 PASS)
python scripts/test_phase3_client.py  # Phase 3: Spatial Intelligence (12/12 PASS)
python scripts/test_phase4_client.py  # Phase 4: Procedural Geometry IR (12/12 PASS)
python scripts/test_phase5_client.py  # Phase 5: Multi-Agent Guild (12/12 PASS)
```
