# Minecraft Java Edition MCP Server 2.0 — 3-Phase Execution & Verification Plan

**Target Environment**: Minecraft Java Edition `26.2` (Fabric Server Engine)  
**Protocol Version**: MCP 2.0 Specification (`mcp>=2.2.0`, Python SDK v2 `MCPServer`, JSON-RPC 2.0 stdio)  
**JVM Toolchain**: OpenJDK 25 | **Gradle**: 9.5.0 | **Python**: 3.14+ (`uv`)  
**Bridge Address**: `http://127.0.0.1:25585/api/v1` | `ws://127.0.0.1:25585/api/v1/ws/player`  
**Current Milestone**: **Phase 1 & Phase 2 Completed & Verified Live** | **Phase 3 (Spatial Intelligence, Architectural Planning & Autonomous Construction)**

---

## 1. Plan Overview & Testing Architecture

The entire project is structured into **3 Core Phases**, strictly adhering to bottom-up vertical slicing. Every phase incorporates the full spectrum of **MCP 2.0 primitives: Tools, Resources, and Prompts**.

No phase is marked complete until it passes **two distinct sets of real-time tests** against a live Minecraft server instance:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Phase Verification Model                        │
├────────────────────────────────────────────────────────────────────────┤
│  Live Minecraft 26.2 Server Running (`./gradlew runServer` on :25585)  │
│                                   │                                    │
│       ┌───────────────────────────┴───────────────────────────┐        │
│       ▼                                                       ▼        │
│  [Test Set A: Python MCP 2.0 Client]                   [Test Set B: Antigravity]
│  - Standalone Python test script                       - Register in Antigravity config
│  - Connects via MCP 2.0 ClientSession over stdio       - Issue natural language prompt
│  - Validates Tools, Resources & Prompts                - Verify agent tool call loop
│  - Automated pass/fail assertions with timeouts        - Inspect visual game changes
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Observation & World State Stack (MCP 2.0)

### 1.1 Goal & Scope
Establish the embedded Netty communication bridge on the Fabric server, thread-safe tick execution, and the complete observation pipeline (vitals, position, inventory, world blocks, entities, and real-time WebSocket push updates). Expose observation via MCP 2.0 Tools, subscribable Resources, and interactive Prompts.

### 1.2 Components Built

#### A. Fabric Mod Bridge (`fabric-mod/src/main/java/com/minecraftmcp/`)
- **Tick Scheduler**: `com.minecraftmcp.bridge.scheduler.TickSchedulerService` queueing tasks onto `ServerTickEvents.END_SERVER_TICK`.
- **Netty HTTP/WS Server**: `com.minecraftmcp.bridge.net.HttpBridgeServer` bound to `127.0.0.1:25585` on `ServerLifecycleEvents.SERVER_STARTED`.
- **Observation Controllers & Services**:
  - `GET /api/v1/status`: Server status, TPS, MSPT, connected players.
  - `GET /api/v1/player/status`: Player health, food, saturation, gamemode, dimension, held item.
  - `GET /api/v1/player/position`: High-speed position (`x, y, z`) and rotation (`yaw, pitch, headYaw`).
  - `GET /api/v1/player/inventory`: Full 36 inventory slots, armor, and offhand.
  - `GET /api/v1/world/block`: Single coordinate block state, properties, and solidity inspection.
  - `POST /api/v1/world/blocks`: Bounded 3D area scan (cuboid max 32,768 blocks).
  - `GET /api/v1/world/entities`: Nearby living entities, players, and items within radius.
  - `GET /api/v1/world/info`: Time of day, weather, dimension limits, world border.
  - `WS /api/v1/ws/player`: WebSocket position & vitals streaming on every server tick (`intervalTicks: 1`).

#### B. Python MCP 2.0 Server (`src/minecraft_mcp/`)
- **Transport Client**: Async HTTP & WebSocket client (`BridgeClient`) connecting to `127.0.0.1:25585`.
- **Pydantic Schemas**: Strict models for all player vitals, block positions, entity summaries, and server telemetry.
- **MCP 2.0 Tools (`@server.tool`)**:
  - `get_server_status()`: Gatekeeper health check (connected, TPS, MSPT, player list).
  - `get_player_state(player_name)`: Full player overview.
  - `get_player_position(player_name)`: Lightweight coordinate lookup.
  - `get_inventory(player_name)`: Detailed slot and item breakdown.
  - `get_block(x, y, z)`: Inspect block at coordinates.
  - `inspect_area(center, radius, format)`: Compact terrain summary (`summary`, `ascii`, `sparse`).
  - `get_nearby_entities(radius, entity_type)`: Scans surrounding entities.
  - `get_world_info()`: Time, weather, and world metadata.
- **MCP 2.0 Resources (`@server.resource`)**:
  - `minecraft://player/position`: Real-time streaming position resource.
  - `minecraft://player/inventory`: Inventory state resource.
  - `minecraft://world`: World time, weather, and dimension info resource.
  - `minecraft://entities/nearby`: Nearby entities resource.
- **MCP 2.0 Prompts (`@server.prompt`)**:
  - `explore_area(center, radius)`: Bootstraps LLM for terrain surveying, resource discovery, and cartography.

### 1.3 Real-Time Live Testing

#### Server Preparation
```bash
cd fabric-mod && ./gradlew runServer
# Wait for: [Server thread/INFO]: Done (...)! For help, type "help"
```

#### Test Set A: Python MCP 2.0 Client Script (`scripts/test_phase1_client.py`)
Run automated script connecting via MCP stdio client:
```bash
source .venv/bin/activate
python scripts/test_phase1_client.py
```
**Verification Checks**:
- [ ] Connects to MCP 2.0 server process over stdio and lists tools, resources, and prompts.
- [ ] Calls `get_server_status()` $\rightarrow$ confirms `connected: true`, TPS $\approx 20.0$.
- [ ] Calls `get_player_state()` $\rightarrow$ matches in-game coordinates and health (20.0).
- [ ] Calls `get_inventory()` $\rightarrow$ accurately reports empty or equipped items.
- [ ] Calls `inspect_area()` $\rightarrow$ returns token-efficient terrain digest without token blowout.
- [ ] Reads resources `minecraft://world` and `minecraft://player/position`.
- [ ] Subscribes to `minecraft://player/position` $\rightarrow$ receives live tick updates over WebSocket.

#### Test Set B: Antigravity MCP Integration
1. Configure Antigravity MCP config (`~/.gemini/config/mcp_config.json`):
```json
{
  "mcpServers": {
    "minecraft": {
      "command": "/Users/arhamowais/minecraft-mcp/.venv/bin/python",
      "args": ["-m", "minecraft_mcp.server"],
      "cwd": "/Users/arhamowais/minecraft-mcp"
    }
  }
}
```
2. Prompt Antigravity in chat:
   > *"Check if Minecraft is running, tell me my player's health, position, and summarize the terrain 8 blocks around me."*
3. **Verification Checks**:
   - [ ] Antigravity identifies and calls `get_server_status`.
   - [ ] Antigravity invokes `get_player_state` and `inspect_area`.
   - [ ] Antigravity returns a conversational, accurate summary of live in-game surroundings.

---

## Phase 2: World Mutation, Player Actions & Direct Building (MCP 2.0)

### 2.1 Goal & Scope
Deliver deterministic, verified world manipulation, player physical actions, generic block interactions, and basic waypoint movement. Phase 2 transforms the agent from a passive observer into an active actor while establishing strict safety boundaries, structured action feedback, and an explicit verification loop.

---

### 2.2 Core Architectural Principles for Phase 2

#### A. The Action Verification Pattern (OBSERVE → ACT → VERIFY)
Phase 2 establishes the foundational feedback cycle for all modifying operations:

```
    ┌───────────┐
    │  OBSERVE  │  Inspect initial local state (get_block, get_player_position, get_inventory)
    └─────┬─────┘
          ▼
    ┌───────────┐
    │   PLAN    │  Determine required action and validate parameters against safety boundaries
    └─────┬─────┘
          ▼
    ┌───────────┐
    │    ACT    │  Dispatch deterministic mutation/action primitive to Fabric bridge
    └─────┬─────┘
          ▼
    ┌───────────┐
    │  VERIFY   │  Query world state to confirm actual physical change matches expectation
    └─────┬─────┘
          ▼
    ┌───────────┐
    │  OBSERVE  │  Re-evaluate environment and provide structured result to agentReAct loop
    └───────────┘
```

Mutation tools and ReAct loops must **never blindly assume success**:
- `place_block()` $\rightarrow$ call `get_block()` $\rightarrow$ verify target coordinates contain expected block state.
- `break_block()` $\rightarrow$ call `get_block()` $\rightarrow$ verify block transitioned to `minecraft:air` or expected dropped state.
- `move_to()` $\rightarrow$ call `get_player_position()` $\rightarrow$ verify player arrived within specified `tolerance` distance.
- `interact_with_block()` $\rightarrow$ call `get_block()` / `get_inventory()` $\rightarrow$ verify open/closed state or container transaction.

This verification discipline established in Phase 2 guarantees that Phase 3 autonomous agents can detect failures, recover from unexpected obstacles, and avoid corrupting complex construction projects.

#### B. Structured Action Results
Every mutation and player action tool returns a rich, descriptive JSON model rather than a primitive `{"success": true}` boolean. This gives the LLM full visibility into pre- and post-action state:

```json
{
  "success": true,
  "action": "place_block",
  "position": { "x": 10, "y": 64, "z": 20 },
  "block": "minecraft:oak_planks",
  "previous_block": "minecraft:air",
  "verified": true,
  "tick": 1420
}
```

For movement operations:
```json
{
  "success": true,
  "action": "move_to",
  "destination": { "x": 15.0, "y": 64.0, "z": 20.0 },
  "final_position": { "x": 14.88, "y": 64.0, "z": 19.95 },
  "distance_remaining": 0.13,
  "status": "arrived",
  "stuck": false,
  "tick": 1455
}
```

#### C. Lightweight Action State & Cancellation Model
To prevent overlapping, conflicting, or runaway operations, Phase 2 implements a lightweight action state model:
- **States**: `IDLE`, `MOVING`, `BUILDING`, `MINING`, `INTERACTING`, `CANCELLED`, `FAILED`.
- Any active long-running action (such as continuous waypoint stepping or multi-block batch placement) can be immediately aborted via `stop_movement()` or action cancellation signals.
- Exposed via MCP resource `minecraft://action/state` for real-time monitoring by the agent.

#### D. Safety Boundaries vs. LLM Planning
Phase 2 enforces a strict separation between code-level safety boundaries and LLM cognitive planning:
- **MCP Safety & Validation Layer (Deterministic & Non-Bypasable)**:
  - Coordinate bounds check: $Y \in [-64, 320]$, within valid world border.
  - Batch operation limit: $\le 500$ blocks per tool call.
  - Block identifier check: must resolve to valid registered `BuiltInRegistries.BLOCK` namespace.
  - Loaded chunk verification: rejects operations targeting unloaded chunks (`CHUNK_UNLOADED`).
- **LLM Agent Planning (Semantic & Goal-Driven)**:
  - The LLM ReAct agent decides *WHAT* to build, *WHERE* to build, and *WHEN* to interact.
  - The MCP layer deterministically validates and executes requested primitives, returning actionable error codes (`INVALID_ARGUMENT`, `OUT_OF_BOUNDS`, `BLOCK_NOT_FOUND`, `CHUNK_UNLOADED`) if boundaries are violated.

#### E. Phase 2 vs. Phase 3 Responsibility Boundary
To maintain engineering rigor, the architectural division between Phase 2 and Phase 3 is strictly defined:

| Capability Area | Phase 2 (Deterministic Execution & Verification) | Phase 3 (Autonomy, Tactics & Complex Planning) |
| :--- | :--- | :--- |
| **World Mutation** | Single & batch block placement/breaking with pre-validation | Procedural architectural generation, structure blueprint compilers |
| **Movement** | Basic waypoint/step movement (`move_to`, `stop_movement`, stuck detection) | Full 3D A* pathfinding, dynamic obstacle avoidance, drop-down jumping |
| **Block Interaction** | Generic interaction primitive (`interact_with_block`) | Multi-step crafting pipelines, automated smelting, container sorting |
| **Architectural Planning** | Single & batch block placement/breaking with pre-validation | Procedural architectural generation, multi-structure blueprint compilers |
| **Agent Autonomy** | Atomic tool execution with verified results | Autonomous long-horizon architectural agents (`build_structure`, `repair_structure`) |

---

### 2.3 Components Built

#### A. Fabric Mod Bridge (`fabric-mod/src/main/java/com/minecraftmcp/`)
- **World Mutation Controllers & Services**:
  - `POST /api/v1/world/set_block`: Thread-safe block placement using `Block.UPDATE_ALL_IMMEDIATE` (`11`). Returns previous and new block state.
  - `POST /api/v1/world/break_block`: Block destruction with optional particle effects and item resource drops.
  - `POST /api/v1/world/check_placement`: Validates whether a given block state can survive at coordinates without placing it.
  - `POST /api/v1/world/interact`: Generic block interaction triggering `player.gameMode.useItemOn()` for containers, crafting tables, furnaces, doors, buttons, and levers.
- **Player Action & Movement Controllers & Services**:
  - `POST /api/v1/player/teleport`: Precise position and orientation updates on server tick.
  - `POST /api/v1/player/rotate`: Head and body orientation adjustments (yaw/pitch).
  - `POST /api/v1/player/select_slot`: Active hotbar slot selection (0–8).
  - `POST /api/v1/player/equip`: Equips items to armor slots (`HEAD`, `CHEST`, `LEGS`, `FEET`) or `OFFHAND`.
  - `POST /api/v1/player/use_item`: Simulates right-click in air or using held item.
  - `POST /api/v1/player/mine`: Simulates progressive or creative block mining with held tool.
  - `POST /api/v1/player/drop`: Drops held item stack or single item.
  - `POST /api/v1/player/swing`: Triggers arm swing animation.
  - `POST /api/v1/player/move`: Basic waypoint step interpolation towards target coordinates with collision checking.
  - `POST /api/v1/player/stop`: Halts active movement, cancels current step loop, and resets action state to `IDLE`.

#### B. Python MCP 2.0 Server (`src/minecraft_mcp/`)
- **Safety Validators & Pipelines**:
  - Validates coordinates, $Y \in [-64, 320]$, batch sizes ($\le 500$), and namespace identifiers before invoking Fabric bridge.
  - Six-stage transactional batch pipeline for `place_blocks` and `fill_region`:
    `Validate Request` $\rightarrow$ `Validate Bounds` $\rightarrow$ `Validate Block IDs` $\rightarrow$ `Validate Batch Size` $\rightarrow$ `Execute` $\rightarrow$ `Verify Result`.
- **Action State Tracker**:
  - Tracks lifecycle state (`IDLE`, `MOVING`, `BUILDING`, etc.) and handles cooperative cancellation.
- **FastMCP Tools (`@server.tool`)**:
  - `place_block(x, y, z, block_id, properties)`: Places single block with post-placement verification.
  - `place_blocks(blocks)`: Atomic batch block placement with pre-validation checklist and verification report.
  - `break_block(x, y, z, drop_items)`: Destroys block with air verification.
  - `fill_region(from_pos, to_pos, block_id)`: Fills bounded volume with validation.
  - `interact_with_block(x, y, z, hand)`: **Generic block interaction primitive** for chests, crafting tables, furnaces, doors/trapdoors, buttons, and levers.
  - `move_to(destination, speed, tolerance)`: Basic movement primitive with arrival verification and stuck detection.
  - `stop_movement()`: Cancels current movement operation and resets velocity.
  - `teleport_player(x, y, z, yaw, pitch)`: Direct coordinate relocation.
  - `look_at(target_pos)`: Adjusts player pitch and yaw to face target coordinates.
  - `select_slot(slot)`: Selects active hotbar slot index (0–8).
  - `equip_item(slot, item_id)`: Equips specified item to designated armor or offhand slot.
  - `use_item(hand)`: Triggers right-click with active hand.
  - `drop_item(entire_stack)`: Drops item from active hotbar slot.
  - `swing_arm(hand)`: Triggers client-visible hand animation.
- **MCP 2.0 Resources (`@server.resource`)**:
  - `minecraft://action/state`: Current player action state and movement progress.
  - `minecraft://knowledge/blocks`: Block state metadata, properties, and valid namespace IDs.
  - `minecraft://knowledge/items`: Equipment and item definitions.

---

### 2.4 Real-Time Live Testing

#### Server Preparation
```bash
cd fabric-mod && ./gradlew runServer
```

#### Test Set A: Python MCP 2.0 Client Script (`scripts/test_phase2_client.py`)
Run automated script connecting via MCP stdio ClientSession:
```bash
source .venv/bin/activate
python scripts/test_phase2_client.py
```
**Verification Checks (12 Core Tests)**:
- [ ] **1. Place Block**: Calls `place_block()` at target coordinate.
- [ ] **2. Verify Placed Block**: Calls `get_block()` to confirm block state matches placed block.
- [ ] **3. Break Block**: Calls `break_block()` at specified coordinate.
- [ ] **4. Verify Broken Block**: Calls `get_block()` to confirm block transitioned to `minecraft:air`.
- [ ] **5. Batch Placement**: Calls `place_blocks()` with a 3x3 platform payload.
- [ ] **6. Verify Batch Placement**: Confirms all 9 coordinates match the requested material.
- [ ] **7. Basic Movement**: Calls `move_to()` towards a reachable coordinate 3 blocks away.
- [ ] **8. Verify Final Position**: Calls `get_player_position()` to confirm arrival within `tolerance`.
- [ ] **9. Stop / Cancellation**: Calls `move_to()` towards distant coordinate, then immediately fires `stop_movement()`; confirms action state returns to `IDLE` and movement halts.
- [ ] **10. Generic Block Interaction**: Calls `interact_with_block()` on a test door/trapdoor or lever; verifies toggle state.
- [ ] **11. Structured Action Result**: Validates that all action responses return rich descriptive models (`action`, `position`, `previous_block`, `verified`).
- [ ] **12. Safety Rejection**: Calls `place_block()` with $Y=350$ and with invalid ID `minecraft:fake_block_xyz`; confirms both requests are deterministically rejected with structured errors before modifying the world.

#### Test Set B: Antigravity MCP Integration (Observe → Act → Verify Loop)
1. Ensure MCP server configuration is active in Antigravity (`~/.gemini/config/mcp_config.json`).
2. Prompt Antigravity in chat:
   > *"Inspect the blocks around me, place a 3x3 platform of oak planks in front of me, verify that the platform exists, then break the center block and verify the opening."*
3. **Verification Checks**:
   - [ ] Antigravity queries local area using `inspect_area` or `get_block` (OBSERVE).
   - [ ] Antigravity calls `place_blocks` to construct the platform (ACT).
   - [ ] Antigravity calls `get_block` on the placed coordinates to confirm placement (VERIFY).
   - [ ] Antigravity calls `break_block` on the center coordinate (ACT).
   - [ ] Antigravity calls `get_block` on the center coordinate to confirm it is air (VERIFY).
   - [ ] Antigravity explains its observations and confirmations based on actual tool return data rather than assuming success.

---

## Phase 3: Spatial Intelligence, Architectural Planning & Autonomous Construction (MCP 2.0)

### 3.1 Goal & Scope
Transform the MCP server into an autonomous architectural agent capable of understanding, compiling, resourcing, constructing, verifying, and repairing large-scale structures across diverse typologies (houses, towers, bridges, walls, castles, roads, farms, monuments, temples, compounds, and custom user blueprints).

Combat, enemy attacks, and weapon mechanics are strictly removed from Phase 3. The foundational abstraction is:
$$\text{Architecture} \longrightarrow \text{Blueprint} \longrightarrow \text{Construction Plan} \longrightarrow \text{Resource Plan} \longrightarrow \text{Construction} \longrightarrow \text{Verification} \longrightarrow \text{Recovery / Repair} \longrightarrow \text{Completed Structure}$$

---

### 3.2 Architectural System Components

#### A. Spatial World Model (`minecraft://world/map`)
- In-memory structured representation of the known Minecraft world.
- Tracks player location, surveyed regions, explored bounding boxes, user landmarks, active/completed structures, resource deposits, and obstacles.
- Tools: `find_build_location`, `scan_region`, `mark_location`, `get_landmarks`.

#### B. Generic Architectural Blueprint System
- Structured data describing architecture (not hard-coded Python classes).
- Schema: identifier, name, structure type, 3D dimensions, palette mapping, ordered components (`foundation`, `floor`, `walls`, `pillars`, `roof`, `openings`, `interior`), constraints, and clearance specifications.
- Predefined templates: `tower`, `bridge`, `wall`, `house`, `farm`, `temple`, `monument`, `road`, and arbitrary `custom` structures.
- Blueprint compiler translates blueprints into deterministic `ConstructionPlan` steps.

#### C. Semantic Component Layer & Construction Engine
- High-level construction primitives compiling down to Phase 2 deterministic batch operations:
  - `build_foundation`, `build_floor`, `build_wall`, `build_pillar`, `build_roof`, `build_doorway`, `build_window`, `build_room`.
  - Generic `build_structure(blueprint, location, orientation, materials_override)`.
- Enforces batch limits ($\le 500$ blocks) and chunk availability before dispatching to Fabric bridge.

#### D. Construction State & Progress Tracker (`minecraft://construction/current`)
- Real-time lifecycle state: `PLANNED`, `VALIDATING`, `WAITING_FOR_RESOURCES`, `BUILDING`, `VERIFYING`, `RECOVERING`, `PAUSED`, `COMPLETED`, `FAILED`, `CANCELLED`.
- Progress metrics: `completed_blocks`, `planned_blocks`, `percentage`, active component, failure logs, and verification history.

#### E. Resource Manager & Acquisition Recovery
- Requirement calculation: compares blueprint bill-of-materials against player inventory (`get_inventory`).
- Computes missing resource deficits and evaluates crafting recipes (e.g. logs $\rightarrow$ planks $\rightarrow$ stairs/slabs/doors).
- If resources are unavailable, transitions to `WAITING_FOR_RESOURCES` with actionable reporting rather than failing silently.

#### F. 3D Navigation & Path Planning (`navigate_to`)
- Internal 3D A* voxel pathfinder navigating uneven terrain, 1-block steps, jump traversals, 3-block safe drops, and dynamic obstacle replanning.
- Dispatches locomotion through Phase 2 `move_to` / `teleport`.

#### G. Structure Verification & Autonomous Repair (`repair_structure`)
- Closed-loop physical inspection: queries actual placed blocks against expected blueprint coordinates.
- Discrepancy detection: pinpoints missing blocks, wrong materials, and intruding obstacles.
- `repair_structure`: automatically generates targeted corrective operations to restore structural integrity.

#### H. Event-Driven State Aggregation
- State aggregator filters high-speed server ticks from WebSocket stream into discrete `AgentEvent`s (`ConstructionCompleted`, `ResourceShortage`, `PlayerStuck`, etc.).
- LLM is only invoked on meaningful decision or replanning points.

---

### 3.3 Real-Time Live Testing

#### Server Preparation
```bash
cd fabric-mod && ./gradlew runServer
```

#### Test Set A: Python MCP 2.0 Client Script (`scripts/test_phase3_client.py`)
```bash
source .venv/bin/activate
python scripts/test_phase3_client.py
```
**Verification Checks (12 Core Tests)**:
- [ ] **1. Blueprint Compilation**: Validates and compiles multiple structure types (tower, bridge, wall, house, custom).
- [ ] **2. Plan Generation**: Sequences ordered construction steps with coordinate offsets and block states.
- [ ] **3. Resource Calculation**: Computes accurate bill-of-materials and identifies inventory deficits.
- [ ] **4. Crafting Recovery**: Resolves craftable items from basic raw materials.
- [ ] **5. Spatial Site Selection**: Calls `find_build_location` and scores terrain flatness.
- [ ] **6. Spatial World Model**: Inspects `minecraft://world/map`, marks landmarks, and records structures.
- [ ] **7. Semantic Component Building**: Executes `build_wall` with battlements and `build_roof`.
- [ ] **8. Generic Construction**: Invokes `build_structure` to build an authentic structure from a generic blueprint.
- [ ] **9. Real-Time Progress Tracking**: Subscribes to `minecraft://construction/current` and monitors percentage completion.
- [ ] **10. Structure Verification**: Compares physical world against blueprint plan, reporting 100% match.
- [ ] **11. Fault Injection & Repair**: Breaks structure blocks, calls `repair_structure`, and verifies restoration.
- [ ] **12. Regression Safety**: Confirms all Phase 1 (20 tests) and Phase 2 (12 tests) continue to pass.

#### Test Set B: Antigravity MCP Integration
1. Ensure MCP server configuration is active in Antigravity.
2. Prompt Antigravity in chat:
   > *"Find a flat spot nearby, navigate there, plan and build a watchtower with battlements and an oak doorway, verify the structure, and report progress."*
3. **Verification Checks**:
   - [ ] Antigravity executes `find_build_location` and selects a construction site.
   - [ ] Antigravity checks resource requirements against inventory.
   - [ ] Antigravity compiles the blueprint and calls `build_structure`.
   - [ ] Antigravity verifies completed blocks and confirms structural integrity.

---

## 2. Summary of Phase Gates

| Phase | Core Deliverables (MCP 2.0) | Test Set A (Python Client) | Test Set B (Antigravity Integration) |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Netty Bridge, Observation Tools, Dynamic Resources (`minecraft://...`), Prompt (`explore_area`) | `scripts/test_phase1_client.py` (Vitals, inventory, blocks, WS) | Prompt: Inspect player state & survey terrain |
| **Phase 2** | World Mutation, Player Actions, Generic Block Interaction, Basic Movement & Action Verification | `scripts/test_phase2_client.py` (12-point suite: place, break, batch, movement, stop, interact, structured results, verification, safety) | Prompt: Observe → Act → Verify (place 3x3 platform, verify, break center, verify opening) |
| **Phase 3** | Blueprints, Construction Engine, Resource Manager, 3D Navigation, Verification & Repair | `scripts/test_phase3_client.py` (12-point suite: blueprints, planning, resources, site search, build, verify, repair) | Prompt: Autonomous site finding, generic structure build, verification & progress report |
