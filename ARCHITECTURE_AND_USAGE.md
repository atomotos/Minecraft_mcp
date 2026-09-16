# Minecraft Java MCP Server 2.0 — Architecture, Codebase Walkthrough & Usage Guide

**Target Environment**: Minecraft Java Edition `26.2`  
**Protocol Version**: MCP 2.0 (`mcp>=2.2.0`, Python SDK v2 `MCPServer`, JSON-RPC 2.0 over stdio)  
**JVM Toolchain**: OpenJDK 25 (`/opt/homebrew/opt/openjdk@25`) | Gradle 9.5.0  
**Python Toolchain**: Python 3.12+ (`uv`)  
**Ports**:
- **Minecraft Game Server**: `localhost:25566`
- **Fabric Embedded Netty Bridge**: `http://127.0.0.1:25585` (REST) | `ws://127.0.0.1:25585/api/v1/ws/player` (WebSocket)

---

## 1. System Architecture

The project integrates Large Language Models (LLMs) and AI agents (such as Google Antigravity or Claude) directly into a running Minecraft Java Edition 26.2 server. Rather than relying on fragile chat-based Brigadier commands (`/setblock`, `/tp`), it employs a high-performance **two-tier architecture**:

1. **Fabric Server-Side Mod (Java 25 / Netty)**: Runs embedded inside the dedicated Minecraft server engine, exposing direct Mojang engine bytecode calls over HTTP and WebSocket.
2. **Python MCP 2.0 Server (`minecraft_mcp`)**: Runs as a subprocess of the AI agent client, exposing high-level MCP 2.0 **Tools**, **Resources**, and **Prompts** over stdio JSON-RPC 2.0.

### 1.1 Architectural Stack Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AI Agent / Client (Antigravity / Claude)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ JSON-RPC 2.0 (stdio)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             Python MCP 2.0 Server (`src/minecraft_mcp`)                │
│  - MCP Tools (22): Observation, Mutation, Locomotion, Player Actions   │
│  - MCP Resources (5): Real-time positions, world, inventory, actions   │
│  - MCP Prompts (1): Structured workflows (e.g. `explore_area`)         │
│  - Safety & Boundary Layer: Coordinate ($Y \in [-64, 320]$) & volume   │
│  - Action Lifecycle Tracker: State machine (`IDLE`, `MOVING`, etc.)    │
│  - Async Bridge Client: `httpx` (REST) & `websockets` (WS Stream)      │
└───────────────────┬────────────────────────────────▲───────────────────┘
               HTTP │ REST (Commands & Queries)      │ WebSocket (Stream)
                    ▼                                │
┌────────────────────────────────────────────────────────────────────────┐
│             Fabric Server-Side Mod (`fabric-mod/` on :25585)           │
│  - Embedded Netty Server Pipeline (HTTP REST Dispatcher + WS Server)   │
│  - Tick Scheduler Service: Thread-safe queue on `END_SERVER_TICK`      │
│  - World Mutation Service: setBlock, breakBlock, fill, interact        │
│  - Player Action Service: moveTowards, teleport, useItem, slotSelect   │
│  - Observation Service: vitals, inventory, chunk auto-loader, scan     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Direct JVM Bytecode Calls
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Minecraft Java 26.2 Dedicated Server Engine              │
│       (`ServerPlayer`, `ServerLevel`, `BlockPos`, `DataComponents`)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Core Architectural Principles

#### A. Thread Safety & Tick Synchronization
Minecraft is fundamentally **single-threaded** for world state and entity ticks. Netty HTTP worker threads run asynchronously on separate thread pools.
- **Rule**: Netty threads **never** call `level.setBlock()` or `player.teleportTo()` directly. Doing so causes race conditions and JVM crashes.
- **Solution**: The [`TickSchedulerService`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/scheduler/TickSchedulerService.java) accepts tasks from Netty worker threads and queues them onto the main Minecraft server thread via `ServerTickEvents.END_SERVER_TICK` or `server.execute()`. A `CompletableFuture` synchronizes the result back to Netty to return HTTP responses.

#### B. The Closed-Loop Feedback Pattern (`OBSERVE` $\rightarrow$ `ACT` $\rightarrow$ `VERIFY`)
The agent never assumes an action succeeded simply because a packet was sent. Every mutating primitive verifies the outcome against ground truth:
1. **Observe**: Inspect initial state (`get_block`, `get_player_position`).
2. **Act**: Dispatch the operation to the Fabric bridge.
3. **Verify**: Query the world state immediately post-execution and populate the `verified` boolean in the structured return model.

#### C. Deterministic Safety Boundaries
Safety validation is deterministic, non-bypassable code in Python:
- Coordinate check: $Y \in [-64, 320]$.
- Max batch size: $\le 500$ blocks per call.
- Valid namespace: Must be a legitimate `minecraft:...` identifier.
- Chunk loading: The mod automatically requests and loads target chunks so off-screen queries do not return stale/null data.

---

## 2. Codebase Walkthrough

```
minecraft-mcp/
├── fabric-mod/                    # Java 25 Fabric Server-Side Mod
│   ├── src/main/java/com/minecraftmcp/
│   │   ├── MinecraftMcpMod.java  # Mod entrypoint & lifecycle hooks
│   │   ├── command/               # In-game console commands
│   │   │   └── McpPingCommand.java
│   │   └── bridge/
│   │       ├── dto/               # Data Transfer Objects
│   │       │   └── ApiResponse.java
│   │       ├── net/               # Netty HTTP & WebSocket transport
│   │       │   ├── HttpBridgeServer.java
│   │       │   ├── RestDispatcherHandler.java
│   │       │   └── PlayerStreamWebSocketHandler.java
│   │       ├── scheduler/         # Server tick synchronization
│   │       │   └── TickSchedulerService.java
│   │       └── service/           # Direct Mojang engine operations
│   │           ├── ObservationService.java
│   │           ├── WorldMutationService.java
│   │           └── PlayerActionService.java
│   ├── build.gradle               # Loom build script (non-obfuscated)
│   └── gradle.properties          # Minecraft 26.2, Fabric 0.152.1
├── src/minecraft_mcp/             # Python MCP 2.0 Server
│   ├── __main__.py                # CLI entrypoint (`python -m minecraft_mcp`)
│   ├── server.py                  # MCPServer: Tools, Resources, Prompts
│   ├── safety.py                  # 6-stage validation pipeline
│   ├── tracker.py                 # ActionStateTracker state machine
│   ├── client/
│   │   └── bridge.py              # Async HTTP & WebSocket client
│   └── models/                    # Pydantic v2 schemas
│       ├── status.py              # Server TPS, MSPT, connection
│       ├── player.py              # Vitals, position, inventory
│       ├── world.py               # Block state, area blocks, info
│       ├── entity.py              # Living entities, mobs
│       └── actions.py             # StructuredActionResult, MovementResult
├── scripts/
│   ├── test_phase1_client.py      # Automated Phase 1 verification
│   └── test_phase2_client.py      # Automated Phase 2 verification (12 tests)
└── pyproject.toml                 # uv package configuration
```

---

### 2.1 The Fabric Mod Layer (`fabric-mod/`)

#### 1. Mod Entrypoint: [`MinecraftMcpMod.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/MinecraftMcpMod.java)
- Implements `ModInitializer`.
- Registers the in-game command `/mcp ping`.
- Hooks `ServerLifecycleEvents.SERVER_STARTED` to initialize `TickSchedulerService` and launch `HttpBridgeServer` on `127.0.0.1:25585`.
- Hooks `ServerLifecycleEvents.SERVER_STOPPING` to shut down Netty event loop groups cleanly.
- Hooks `ServerTickEvents.END_SERVER_TICK` to drain scheduled tasks and broadcast WebSocket telemetry.

#### 2. Netty Pipeline: [`HttpBridgeServer.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/net/HttpBridgeServer.java)
- Configures Netty's `NioEventLoopGroup` (boss and worker threads).
- Sets up an HTTP pipeline (`HttpServerCodec`, `HttpObjectAggregator` up to 64MB, `WebSocketServerProtocolHandler`).
- Routes requests:
  - HTTP REST (`/api/v1/*`) $\rightarrow$ [`RestDispatcherHandler`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/net/RestDispatcherHandler.java).
  - WebSocket (`/api/v1/ws/player`) $\rightarrow$ [`PlayerStreamWebSocketHandler`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/net/PlayerStreamWebSocketHandler.java).

#### 3. Request Routing: [`RestDispatcherHandler.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/net/RestDispatcherHandler.java)
- Extracts JSON payloads safely using null-safe helper `getJsonString()`.
- Routes endpoints to underlying services:
  - **Status & Observation**: `/api/v1/status`, `/api/v1/player/status`, `/api/v1/player/position`, `/api/v1/player/inventory`, `/api/v1/world/block`, `/api/v1/world/blocks`, `/api/v1/world/entities`, `/api/v1/world/info`.
  - **Mutation & Interaction**: `/api/v1/world/set_block`, `/api/v1/world/break_block`, `/api/v1/world/fill`, `/api/v1/world/interact`.
  - **Player Actions**: `/api/v1/player/move`, `/api/v1/player/stop`, `/api/v1/player/teleport`, `/api/v1/player/rotate`, `/api/v1/player/select_slot`, `/api/v1/player/use_item`, `/api/v1/player/drop`, `/api/v1/player/swing`, `/api/v1/player/gamemode`.
- Formats every response using standard envelope: `{ "success": boolean, "data": ..., "error": ..., "tick": long }`.

#### 4. Thread Synchronization: [`TickSchedulerService.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/scheduler/TickSchedulerService.java)
- Implements `execute(Supplier<T>) -> CompletableFuture<T>`.
- Offloads tasks onto the main server loop using `server.execute()` or queues them for the tick boundary.

#### 5. World Mutation Engine: [`WorldMutationService.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/service/WorldMutationService.java)
- `setBlock`: Resolves `BlockState` from string (e.g. `minecraft:stone`) and applies flags `Block.UPDATE_ALL_IMMEDIATE` (`11`).
- `breakBlock`: Destroys target block with loot drops and returns previous state.
- `fillRegion`: Fills 3D cuboid with optional `replaceBlock` mask.
- `interactWithBlock`: Generic interaction primitive. Detects block type at coordinates, calls `player.gameMode.useItemOn(...)` or `state.useWithoutItem(...)`, and returns whether state changed (e.g. door opened, lever flipped).
- `ensureLoaded`: Auto-loads chunk via `level.getChunk(x >> 4, z >> 4, ChunkStatus.FULL, true)` before reading or mutating.

#### 6. Player Control Engine: [`PlayerActionService.java`](file:///Users/arhamowais/minecraft-mcp/fabric-mod/src/main/java/com/minecraftmcp/bridge/service/PlayerActionService.java)
- `moveTowards`: Calculates distance, checks for obstruction/stuck conditions, and steps player towards waypoint.
- `stopMovement`: Immediately halts active movement steps and resets velocity.
- `teleport` & `setRotation`: Moves position and adjusts yaw/pitch.
- `selectSlot`: Sets hotbar index (0–8).
- `useItem`, `dropItem`, `swingHand`: Simulates player interactions.

---

### 2.2 The Python MCP 2.0 Server Layer (`src/minecraft_mcp/`)

#### 1. Server Definition: [`server.py`](file:///Users/arhamowais/minecraft-mcp/src/minecraft_mcp/server.py)
Uses the modern MCP 2.0 SDK (`mcp.server.mcpserver.MCPServer`):
- **Tools (`@server.tool`)**:
  - Observation: `get_server_status`, `get_player_state`, `switch_game_mode`, `get_player_position`, `get_inventory`, `get_block`, `inspect_area`, `get_nearby_entities`, `get_world_info`.
  - World Mutation: `place_block`, `place_blocks`, `break_block`, `fill_region`, `interact_with_block`.
  - Player Actions: `move_to`, `stop_movement`, `teleport`, `look_at`, `select_slot`, `use_item`, `drop_item`, `swing_arm`.
- **Resources (`@server.resource`)**:
  - `minecraft://action/state`: Current agent action state (`IDLE`, `MOVING`, etc.).
  - `minecraft://player/position`: Live coordinates.
  - `minecraft://player/inventory`: Inventory snapshot.
  - `minecraft://world`: Time of day, weather, dimensions.
  - `minecraft://entities/nearby`: Surrounding mobs.
- **Prompts (`@server.prompt`)**:
  - `explore_area`: Surveying and terrain scouting workflow.

#### 2. Safety Layer: [`safety.py`](file:///Users/arhamowais/minecraft-mcp/src/minecraft_mcp/safety.py)
- Enforces $Y \in [-64, 320]$.
- Enforces batch volume limits ($\le 500$ blocks).
- Validates block identifier namespace (rejects invalid block names before network call).

#### 3. Action State Tracker: [`tracker.py`](file:///Users/arhamowais/minecraft-mcp/src/minecraft_mcp/tracker.py)
- Singleton managing `ActionStateEnum` (`IDLE`, `MOVING`, `BUILDING`, `MINING`, `INTERACTING`, `CANCELLED`, `FAILED`).
- Supports cooperative cancellation when `stop_movement` or emergency stops are triggered.

#### 4. Bridge Client: [`client/bridge.py`](file:///Users/arhamowais/minecraft-mcp/src/minecraft_mcp/client/bridge.py)
- Async HTTP client (`httpx.AsyncClient`) with connection pooling and timeouts.
- Excludes `None` fields during JSON serialization to prevent Java `JsonNull` parsing errors.
- Maps HTTP status and error envelopes into typed `BridgeError` exceptions.

---

## 3. How to Run Manually (Step-by-Step Guide)

### Prerequisites

1. **Java 25**: Installed at `/opt/homebrew/opt/openjdk@25` (configured in `gradle.properties`).
2. **Python Virtual Environment**: Activated `.venv` with `mcp>=2.2.0`, `httpx`, `websockets`, `pydantic`.
3. **Minecraft Java Edition 26.2 Client**: (Optional, if you want to visually see your character in the world).

---

### Step 1: Start the Fabric Minecraft Dedicated Server

In terminal #1:
```bash
cd /Users/arhamowais/minecraft-mcp/fabric-mod
./gradlew runServer
```

Wait until you see the confirmation lines in the console:
```text
[Server thread/INFO] (minecraft-mcp-bridge) [Minecraft MCP] Starting embedded Netty Bridge Server on 127.0.0.1:25585...
[Server thread/INFO] (minecraft-mcp-bridge) [Minecraft MCP] Netty Bridge Server successfully listening on http://127.0.0.1:25585
[Server thread/INFO] (Minecraft) Done (...s)! For help, type "help"
```

> **Note**: The Minecraft server runs on port **`25566`** (with `online-mode=false`), and the Netty bridge runs on port **`25585`**.

---

### Step 2: (Optional) Connect Your Player Client

1. Launch Minecraft Java Edition **26.2**.
2. Go to **Multiplayer** $\rightarrow$ **Direct Connection** (or Add Server).
3. Enter Server Address:
   ```text
   localhost:25566
   ```
4. Click **Join Server**. Your player will spawn into the world.

---

### Step 3: Run the MCP Server Manually

You have **four distinct ways** to run and interact with the MCP server:

#### Option A: Run via MCP Inspector (Recommended for Visual UI & Manual Debugging)
The MCP Inspector provides an interactive web interface to inspect tools, enter parameters, view dynamic resources, and test prompts.

In terminal #2:
```bash
cd /Users/arhamowais/minecraft-mcp
npx @modelcontextprotocol/inspector .venv/bin/python -m minecraft_mcp
```

1. Open the URL shown in the terminal (usually `http://localhost:5173`).
2. Click **Connect**.
3. Under the **Tools** tab, you will see all 22 tools (`get_server_status`, `place_block`, `move_to`, etc.).
4. Select a tool, fill in parameters, and click **Run Tool** to observe live in-game execution.

---

#### Option B: Run the Automated Test Suites
Run the verified automated test scripts to execute real-time tests against the running server:

In terminal #2:
```bash
cd /Users/arhamowais/minecraft-mcp
source .venv/bin/activate

# Run Phase 1 Tests (Observation, Vitals, Inventory, World Info)
python scripts/test_phase1_client.py

# Run Phase 2 Tests (12 Mutation, Interaction, Movement & Safety Tests)
python scripts/test_phase2_client.py
```

---

#### Option C: Run Direct Stdio Command (For Agent Integration)
To run the server as a raw stdio JSON-RPC process:

```bash
cd /Users/arhamowais/minecraft-mcp
source .venv/bin/activate
python -m minecraft_mcp
```
*The process will wait on `stdin` for JSON-RPC 2.0 messages (e.g. `initialize`, `tools/list`, `tools/call`). Press `Ctrl+C` to stop.*

To connect it to **Google Antigravity** or **Claude Desktop**, register it in your config:
- **Antigravity config**: `~/.gemini/config/mcp_config.json`
- **Claude Desktop config**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "minecraft": {
      "command": "/Users/arhamowais/minecraft-mcp/.venv/bin/python",
      "args": ["-m", "minecraft_mcp"],
      "cwd": "/Users/arhamowais/minecraft-mcp",
      "env": {
        "FABRIC_BRIDGE_URL": "http://127.0.0.1:25585",
        "FABRIC_WS_URL": "ws://127.0.0.1:25585/api/v1/ws/player"
      }
    }
  }
}
```

---

#### Option D: Query the Fabric Bridge Directly via `curl`
Since the Fabric Netty bridge runs a standard HTTP REST API, you can query or trigger actions directly from the shell without MCP:

```bash
# Check Server Status & TPS
curl -s http://127.0.0.1:25585/api/v1/status | jq .

# Get World Info
curl -s http://127.0.0.1:25585/api/v1/world/info | jq .

# Inspect Block at (0, 64, 0)
curl -s "http://127.0.0.1:25585/api/v1/world/block?x=0&y=64&z=0" | jq .

# Place a Stone Block at (0, 64, 0)
curl -s -X POST http://127.0.0.1:25585/api/v1/world/set_block \
  -H "Content-Type: application/json" \
  -d '{"x": 0, "y": 64, "z": 0, "block": "minecraft:stone"}' | jq .
```

---

## 4. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FABRIC_BRIDGE_URL` | `http://127.0.0.1:25585` | URL of the Fabric Netty HTTP REST bridge. |
| `FABRIC_WS_URL` | `ws://127.0.0.1:25585/api/v1/ws/player` | URL for the real-time WebSocket player telemetry stream. |

---

## 5. Troubleshooting Common Issues

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `Could not connect to Fabric Bridge at http://127.0.0.1:25585` | Dedicated server is not running. | Run `./gradlew runServer` in `fabric-mod/` and wait for "Done!". |
| `No player found matching '...'` | No player has logged into the server. | Connect a Minecraft 26.2 client to `localhost:25566`. |
| `SAFETY_VIOLATION: Y coordinate out of bounds` | Requested coordinate outside $[-64, 320]$. | Check $Y$ coordinates; Minecraft 26.2 world range is $[-64, 320]$. |
| `Address already in use: bind` | Port 25566 or 25585 is occupied by an old process. | Kill stale processes: `lsof -ti:25585,25566 \| xargs kill -9`. |
| `java: command not found` or Gradle build error | Missing OpenJDK 25. | Ensure OpenJDK 25 is installed at `/opt/homebrew/opt/openjdk@25`. |
