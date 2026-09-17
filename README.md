# Minecraft MCP Server 2.0 (Java Edition 26.2)

[![MCP Protocol](https://img.shields.io/badge/MCP-2.0-blue.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-green.svg)](https://www.python.org/)
[![Transport](https://img.shields.io/badge/Transport-stdio-orange.svg)](https://py.sdk.modelcontextprotocol.io/)
[![Minecraft](https://img.shields.io/badge/Minecraft-Java%2026.2-red.svg)](https://www.minecraft.net/)
[![Fabric](https://img.shields.io/badge/Fabric-Server%20Launcher-brightgreen.svg)](https://fabricmc.net/)

An advanced **Model Context Protocol (MCP 2.0)** server designed for autonomous AI agents in **Minecraft Java Edition 26.2**. Running over a standard I/O (`stdio`) transport, this server connects LLMs (such as Claude, Antigravity, or custom agent loops) directly to a server-side **Fabric Mod Bridge** via high-speed **localhost HTTP and WebSocket** protocols.

---

## 💡 Key Design Philosophy

> **Do not expose Minecraft commands as the primary abstraction. Expose capabilities.**

Instead of forcing the LLM to micromanage `/setblock`, `/fill`, or coordinate mathematics directly—or using slow, fragile RCON command parsing—the MCP server provides:
1. **Direct Fabric World & Entity API Integration**: Volumetric batch placement via `ServerWorld.setBlockState()`, real-time entity inspection, and sub-millisecond query responses.
2. **High-Level Structural Operations**: Autonomous house construction, defensive walls, roofs, doors, and site selection.
3. **Compact World Representations**: 2D ASCII slices, statistical terrain digests, and flatness scores that compress spatial data by 90% to preserve LLM context tokens.
4. **Real-Time WebSocket Subscription**: Event-driven player position streaming via `ws://localhost:8080/ws/events` hooked directly into `ServerTickEvents.END_SERVER_TICK`.
5. **Autonomous Agent Loops**: Closed-loop Observe-Reason-Plan-Act-Verify pipelines for building, PvP combat, and perimeter defense.
1. **Direct Fabric World & Entity API Integration**: Volumetric batch placement via Mojang engine APIs, real-time entity inspection, and sub-millisecond query responses.
2. **Generic Architectural Blueprints**: Compilers for towers, bridges, walls, houses, castles, farms, temples, and custom user designs.
3. **Semantic Structural Components**: High-level primitives for walls, battlements, roofs, pillars, foundations, and openings.
4. **Spatial World Modeling & 3D Navigation**: Persistent cartography (`minecraft://world/map`), flatness scoring, and 3D A* voxel pathfinding (`navigate_to`).
5. **Real-Time WebSocket Subscription**: Event-driven player position streaming via `ws://127.0.0.1:25585/api/v1/ws/player` hooked into `ServerTickEvents.END_SERVER_TICK`.
6. **Closed-Loop Construction & Verification**: Observe-Act-Verify cycles with ground-truth verification and automated structure repair (`repair_structure`).

---

## 📚 Complete Documentation

Comprehensive technical documentation is organized in the [`docs/`](docs/README.md) directory:

| Document | Description |
| :--- | :--- |
| 📖 **[Documentation Index](docs/README.md)** | Full portal and navigation map |
| 📋 **[Implementation Rules](implementation.md)** | The 30 non-negotiable rules, layer separation, zero-guessing policy, bottom-up phasing |
| 🏛️ **[System Architecture](docs/architecture.md)** | `stdio` transport, Fabric mod HTTP/WS bridge, WebSocket subscription engine, and Fabric launcher |
| 🤖 **[Autonomous Agents](docs/agents.md)** | Building Agent, Combat/PvP Agent, Sentry Agent, and state resumption |
| 📦 **[MCP Resources](docs/resources.md)** | Subscribable `minecraft://player/position`, world state, and static knowledge |
| 💬 **[MCP Prompts](docs/prompts.md)** | Prompt templates: `/build_house`, `/defend_player`, `/build_and_defend`, etc. |
| 🏛️ **[System Architecture](docs/architecture.md)** | `stdio` transport, Fabric mod HTTP/WS bridge, WebSocket subscription engine, and Netty pipeline |
| 🤖 **[Autonomous Agents](docs/agents.md)** | Architectural Planning Agent, Construction Engine, and state resumption |
| 📦 **[MCP Resources](docs/resources.md)** | Subscribable `minecraft://world/map`, `minecraft://construction/current`, position, inventory, and knowledge |
| 💬 **[MCP Prompts](docs/prompts.md)** | Prompt templates: `/architect_structure`, `/construct_structure`, `/repair_structure`, `/explore_area` |
| 🔧 **[Primitive Tools Manual](docs/tools/primitives.md)** | Comprehensive single reference for all low-level tools |

### High-Level Tools
- 🏡 [build_house](docs/tools/high_level/build_house.md) — Parametric house builder
- 🧱 [build_wall](docs/tools/high_level/build_wall.md) — Wall & battlement constructor
- 🪚 [build_floor](docs/tools/high_level/build_floor.md) — Floor & foundation leveler
### High-Level Architectural Tools
- 🏛️ [build_structure](docs/tools/high_level/build_structure.md) — Generic blueprint-driven architectural constructor
- 🧱 [build_wall](docs/tools/high_level/build_wall.md) — Wall, curtain barrier & battlement constructor
- 🛖 [build_roof](docs/tools/high_level/build_roof.md) — Pitched, hip, flat, and dome roof generator
- 🚪 [build_door](docs/tools/high_level/build_door.md) — Doorway frame cutter & door installer
- 🪟 [build_window](docs/tools/high_level/build_window.md) — Aperture cutter & glass pane installer
- 🧭 [find_build_location](docs/tools/high_level/find_build_location.md) — Terrain slope & clearing cost analyzer
- 🏃 [navigate_to](docs/tools/high_level/navigate_to.md) — 3D pathfinding & movement orchestrator
- ⚔️ [combat_engage](docs/tools/high_level/combat_engage.md) — Tactical PvP combat state machine
- 🛡️ [defend_perimeter](docs/tools/high_level/defend_perimeter.md) — Autonomous sentry & guard patrol
- 🏃 [navigate_to](docs/tools/high_level/navigate_to.md) — 3D voxel pathfinding & locomotion orchestrator
- 🛠️ [repair_structure](docs/tools/high_level/repair_structure.md) — Verification-driven structural discrepancy detector & repairer
- 📋 [check_requirements](docs/tools/high_level/check_requirements.md) — Blueprint bill-of-materials and inventory deficit analyzer

---

## 🚀 Quick Start

### 1. Launch the Fabric Minecraft Server
Make sure the Fabric Server Launcher for **Minecraft Java 26.2** is running with `minecraft-mcp-bridge-1.0.0.jar` in your `mods/` folder:
Make sure the Fabric Server for **Minecraft Java 26.2** is running with the embedded bridge mod on port 25585:
```bash
java -Xmx4G -Xms2G -jar fabric-server-launch.jar nogui
cd fabric-mod && ./gradlew runServer
```
The bridge mod starts an embedded server listening on `http://127.0.0.1:8080`.
The bridge mod starts an embedded server listening on `http://127.0.0.1:25585`.

### 2. Environment Variables
```bash
export FABRIC_BRIDGE_URL="http://127.0.0.1:8080"
export FABRIC_WS_URL="ws://127.0.0.1:8080/ws/events"
export MINECRAFT_TARGET_PLAYER="Steve"
export FABRIC_BRIDGE_URL="http://127.0.0.1:25585"
export FABRIC_WS_URL="ws://127.0.0.1:25585/api/v1/ws/player"
export MINECRAFT_TARGET_PLAYER="AtomOtos"
```

### 3. Run the MCP Server in Stdio Mode
```bash
# Using uv
uv run minecraft-mcp
```

### 4. Connect to an MCP Client
Add the server entry to your client configuration (e.g. Claude Desktop or Antigravity):
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "uv",
      "args": ["--directory", "/path/to/minecraft-mcp", "run", "minecraft-mcp"],
      "command": "/Users/arhamowais/minecraft-mcp/.venv/bin/python",
      "args": ["-m", "minecraft_mcp"],
      "cwd": "/Users/arhamowais/minecraft-mcp",
      "env": {
        "FABRIC_BRIDGE_URL": "http://127.0.0.1:8080",
        "FABRIC_WS_URL": "ws://127.0.0.1:8080/ws/events",
        "MINECRAFT_TARGET_PLAYER": "Steve"
        "FABRIC_BRIDGE_URL": "http://127.0.0.1:25585",
        "FABRIC_WS_URL": "ws://127.0.0.1:25585/api/v1/ws/player",
        "MINECRAFT_TARGET_PLAYER": "AtomOtos"
      }
    }
  }
}
```

---

## 👥 Autonomous Agent Workflows
## 👥 Autonomous Architectural Workflow

### Building Workflow
```
inspect_area ──► find_build_location ──► build_floor ──► build_wall ──► build_door ──► build_window ──► build_roof ──► verify
scan_region / inspect_area
          │
          ▼
  find_build_location (Flatness & Clearing Analysis)
          │
          ▼
  architect_structure / compile_blueprint (Tower, House, Bridge, Custom)
          │
          ▼
  check_requirements (Inventory Diff & Crafting Recovery)
          │
          ▼
  build_structure (Semantic Component Pipeline)
          │
          ▼
  verify_structure (Expected vs Ground Truth)
          │
          ▼
  repair_structure (Autonomous Defect Correction)
          │
          ▼
  Completed Verified Architecture
```

### Combat / PvP Workflow
```
minecraft://players/nearby ──► inspect_player ──► equip_item ──► navigate_to ──► combat_engage ──► loot / retreat
```

---

## 📄 License
MIT License.
