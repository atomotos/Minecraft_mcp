# Minecraft Java Edition MCP Server 2.0 — Documentation Portal

Welcome to the comprehensive documentation for the **Minecraft Java Edition Model Context Protocol (MCP) Server**. This server bridges Large Language Models (LLMs) to Minecraft Java Edition servers via the **MCP 2.0 specification** over a **standard I/O (`stdio`) transport**, using a **server-side Fabric Mod bridge** over **localhost HTTP / WebSocket** on the **Fabric Server Launcher** for **Minecraft Java 26.2**.

---

## 🧭 Documentation Map

| Section | Document | Description |
| :--- | :--- | :--- |
| **System Architecture** | [architecture.md](architecture.md) | System topology, stdio transport, Fabric mod HTTP/WS bridge, WebSocket subscription engine, and compact world representation. |
| **Implementation Rules** | [implementation.md](implementation.md) | The 30 non-negotiable rules, layer separation, zero-guessing policy, bottom-up phasing, and V1 Definition of Done. |
| **Autonomous Agents** | [agents.md](agents.md) | Autonomous agent loops (Observe-Reason-Plan-Act-Verify), Architectural Planning Agent, Structural Restoration Agent, and state recovery. |
| **MCP Resources** | [resources.md](resources.md) | Full specification of subscribable resources (`minecraft://world/map`, `minecraft://construction/current`, position, inventory, knowledge). |
| **MCP Prompts** | [prompts.md](prompts.md) | Built-in MCP Prompt templates: `/architect_structure`, `/construct_structure`, `/resume_construction`, `/repair_structure`, `/explore_area`. |
| **Primitive Tools** | [primitives.md](tools/primitives.md) | Single reference manual for all low-level tools: observation, block manipulation, movement, inventory, and spatial primitives. |
| **High-Level Tools** | `docs/tools/high_level/` | Dedicated deep-dive specifications for each composite high-level capability. |

---

## 🛠️ High-Level Tools Directory

Each high-level tool orchestrates multiple primitives to execute complex agent goals:

- [build_structure.md](tools/high_level/build_structure.md) — Generic blueprint-driven architectural constructor (towers, bridges, walls, castles, farms, houses, custom).
- [build_wall.md](tools/high_level/build_wall.md) — Wall generator with customizable dimensions, thickness, and crenellations.
- [build_floor.md](tools/high_level/build_floor.md) — Multi-layer flooring tool with bounding box, patterns, and subfloor leveling.
- [build_roof.md](tools/high_level/build_roof.md) — Roof generator supporting pitched gable, hip, flat, and dome styles.
- [build_door.md](tools/high_level/build_door.md) — Doorway frame cutter and door installation tool.
- [build_window.md](tools/high_level/build_window.md) — Window aperture generator and glass pane installer.
- [find_build_location.md](tools/high_level/find_build_location.md) — Spatial terrain analyzer for flatness, slope, clearance, and clearing cost.
- [navigate_to.md](tools/high_level/navigate_to.md) — Multi-node 3D A* pathfinding and movement orchestration across uneven terrain.
- [repair_structure.md](tools/high_level/repair_structure.md) — Closed-loop physical verification and autonomous restoration tool.
- [check_requirements.md](tools/high_level/check_requirements.md) — Blueprint bill-of-materials and inventory deficit analyzer.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.12+ (or 3.14)
- Minecraft Java Edition 26.2 Dedicated Server running Fabric Server Launcher
- Fabric Mod: `minecraft-mcp-bridge` loaded in server
- Package manager: `uv` (recommended) or `pip`

### 2. Fabric Server Setup
Launch the Minecraft Java 26.2 Fabric server:
```bash
cd fabric-mod && ./gradlew runServer
```
The bridge mod starts an embedded HTTP/WebSocket server listening on `http://127.0.0.1:25585`.

### 3. Environment Setup
```bash
export FABRIC_BRIDGE_URL="http://127.0.0.1:25585"
export FABRIC_WS_URL="ws://127.0.0.1:25585/api/v1/ws/player"
export MINECRAFT_TARGET_PLAYER="AtomOtos"
```

### 4. Running the MCP Server in Stdio Mode
```bash
source .venv/bin/activate
python -m minecraft_mcp
```

### 5. Client Integration (e.g. Claude Desktop / Antigravity)
Add the server to your MCP client configuration (`claude_desktop_config.json` or Antigravity MCP settings):
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "/Users/arhamowais/minecraft-mcp/.venv/bin/python",
      "args": [
        "-m",
        "minecraft_mcp"
      ],
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
