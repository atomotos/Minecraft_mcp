# Minecraft Java Edition MCP Server 2.0 — Documentation Portal

Welcome to the comprehensive documentation for the **Minecraft Java Edition Model Context Protocol (MCP) Server**. This server bridges Large Language Models (LLMs) to Minecraft Java Edition servers via the **MCP 2.0 specification** over a **standard I/O (`stdio`) transport**, using a **server-side Fabric Mod bridge** over **localhost HTTP / WebSocket** on the **Fabric Server Launcher** for **Minecraft Java 26.2**.

---

## 🧭 Documentation Map

| Section | Document | Description |
| :--- | :--- | :--- |
| **System Architecture** | [architecture.md](architecture.md) | System topology, stdio transport, Fabric mod HTTP/WS bridge, WebSocket subscription engine, and compact world representation. |
| **Implementation Rules** | [implementation.md](implementation.md) | The 30 non-negotiable rules, layer separation, zero-guessing policy, bottom-up phasing, and V1 Definition of Done. |
| **Autonomous Agents** | [agents.md](agents.md) | Autonomous agent loops (Observe-Reason-Plan-Act-Verify), Building Agent, Combat/PvP Agent, Perimeter Defense Agent, and state recovery. |
| **MCP Resources** | [resources.md](resources.md) | Full specification of subscribable resources (`minecraft://player/position`), world state, inventory, nearby entities, and static knowledge bases. |
| **MCP Prompts** | [prompts.md](prompts.md) | Built-in MCP Prompt templates: `/build_house`, `/defend_player`, `/build_and_defend`, `/hunt_player`, and `/explore_area`. |
| **Primitive Tools** | [primitives.md](tools/primitives.md) | Single reference manual for all low-level tools: observation, block manipulation, movement, inventory, combat, and command fallback. |
| **High-Level Tools** | `docs/tools/high_level/` | Dedicated deep-dive specifications for each composite high-level capability. |

---

## 🛠️ High-Level Tools Directory

Each high-level tool orchestrates multiple primitives to execute complex agent goals:

- [build_house.md](tools/high_level/build_house.md) — Autonomous residential building from style, dimensions, or blueprint.
- [build_wall.md](tools/high_level/build_wall.md) — Wall generator with customizable dimensions, thickness, and crenellations.
- [build_floor.md](tools/high_level/build_floor.md) — Multi-layer flooring tool with bounding box, patterns, and subfloor leveling.
- [build_roof.md](tools/high_level/build_roof.md) — Roof generator supporting pitched gable, hip, flat, and dome styles.
- [build_door.md](tools/high_level/build_door.md) — Doorway frame cutter and door installation tool.
- [build_window.md](tools/high_level/build_window.md) — Window aperture generator and glass pane installer.
- [find_build_location.md](tools/high_level/find_build_location.md) — Spatial terrain analyzer for flatness, slope, clearance, and clearing cost.
- [navigate_to.md](tools/high_level/navigate_to.md) — Multi-node pathfinding and movement orchestration across uneven terrain.
- [combat_engage.md](tools/high_level/combat_engage.md) — Tactical PvP combat sequence managing distance, weapon cooldown, and retreat.
- [defend_perimeter.md](tools/high_level/defend_perimeter.md) — Guard sentry routine reacting to player and mob proximity triggers.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.12+ (or 3.14)
- Minecraft Java Edition 26.2 Dedicated Server running Fabric Server Launcher
- Fabric Mod: `minecraft-mcp-bridge-1.0.0.jar` placed in server `mods/` directory
- Package manager: `uv` (recommended) or `pip`

### 2. Fabric Server Launcher Setup
Download and launch the Minecraft Java 26.2 Fabric server:
```bash
# Launch server with bridge mod installed
java -Xmx4G -Xms2G -jar fabric-server-launch.jar nogui
```
The bridge mod starts an embedded HTTP/WebSocket server listening on `http://127.0.0.1:8080`.

### 3. Environment Setup
Create a `.env` file or export environment variables:
```bash
export FABRIC_BRIDGE_URL="http://127.0.0.1:8080"
export FABRIC_WS_URL="ws://127.0.0.1:8080/ws/events"
export MINECRAFT_TARGET_PLAYER="Steve" # Default player tracked/controlled
```

### 4. Running the MCP Server in Stdio Mode
```bash
uv run minecraft-mcp
```

### 5. Client Integration (e.g. Claude Desktop / Antigravity)
Add the server to your MCP client configuration (`claude_desktop_config.json` or Antigravity MCP settings):
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/minecraft-mcp",
        "run",
        "minecraft-mcp"
      ],
      "env": {
        "FABRIC_BRIDGE_URL": "http://127.0.0.1:8080",
        "FABRIC_WS_URL": "ws://127.0.0.1:8080/ws/events",
        "MINECRAFT_TARGET_PLAYER": "Steve"
      }
    }
  }
}
```
