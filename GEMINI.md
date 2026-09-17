# GEMINI.md — Minecraft Java MCP Server & Fabric Bridge

**Project**: Autonomous Minecraft Java Edition MCP Server  
**Target Environment**: Minecraft Java Edition `26.2`  
**Current Status**: **Phase 1, Phase 2 & Phase 3 Completed & Verified Live** (44/44 Tests Passing) | **Taj Mahal & Qutub Minar Monuments Fully Constructed (100% Physical Verification)**  
**Last Updated**: September 2026

---

## 1. Project Overview & Architecture

This project builds an autonomous Model Context Protocol (MCP) server for Minecraft Java Edition. It exposes high-level agent capabilities (autonomous construction, combat, spatial observation, and navigation) rather than merely wrapping low-level Brigadier commands.

### Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│                 MCP Client (Claude / AI Agent)              │
└──────────────────────────────┬──────────────────────────────┘
                               │ stdio (JSON-RPC v2)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Python MCP Server (src/minecraft_mcp)           │
│  - MCP Tools: High-level primitives (build, fight, inspect) │
│  - MCP Resources: Real-time position & world observations   │
│  - Python Client: Spatial planning, A* search, blueprints   │
└──────────────┬──────────────────────────────▲───────────────┘
          HTTP │ REST (Commands)              │ WebSocket (Position Stream)
               ▼                              │
┌─────────────────────────────────────────────────────────────┐
│       Fabric Server-Side Mod (fabric-mod/ / :25585)         │
│  - Embedded Netty Server (:25585) (REST + WebSocket)        │
│  - Tick Synchronizer: Concurrent queue on ServerTickEvents  │
│  - Direct Mojang Engine APIs (zero command overhead)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Direct bytecode calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│         Minecraft Java 26.2 Dedicated Server Engine         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Environment & Verified Toolchain

- **Minecraft Version**: `26.2` (Unobfuscated vanilla JAR distribution)
- **Fabric Loader**: `0.18.4`
- **Fabric API**: `0.152.1+26.2`
- **Fabric Loom**: `1.17.20` (`fabric.loom.disableObfuscation=true`)
- **JDK**: OpenJDK 25 (`/opt/homebrew/opt/openjdk@25`)
- **Gradle**: `9.5.0` (`fabric-mod/gradlew`)
- **Python**: Python 3.12+ managed with `uv` (`.venv`)
- **Bundled JVM Libraries** (Already on runtime classpath — **no shading needed**):
  - `io.netty:netty-codec-http:4.2.15.Final` (REST + WebSocket support)
  - `com.google.code.gson:gson:2.14.0` (JSON serialization)

---

## 3. Milestones & Work Completed

### Milestone 1: Mod Baseline & Build System (COMPLETED)
- Upgraded Gradle wrapper to 9.5.0 on JDK 25.
- Fixed non-obfuscated Loom build configuration: switched dependencies to standard `implementation` / `compileOnly`.
- Implemented `/mcp ping` command in `com.minecraftmcp.MinecraftMcpMod`.
- Verified live server launch with `./gradlew runServer`: mod loads cleanly and replies to `/mcp ping`.

### Task 1: Version-Locked API Research & Specification (COMPLETED)
- Conducted an exhaustive, bytecode-verified API research pass against `minecraft-merged-deobf-26.2.jar` and `fabric-api 0.152.1+26.2`.
- Produced authoritative reference documents: `docs/fabric/api-research-26.2.md` and `docs/implementation/primitive-spec-26.2.md`.

### Phase 1: Observation & World State Stack (COMPLETED & VERIFIED)
- Embedded Netty HTTP and WebSocket server on `127.0.0.1:25585`.
- Thread-safe tick dispatch via `TickSchedulerService` and `ServerTickEvents.END_SERVER_TICK`.
- 9 Observation tools, 4 dynamic resources (`minecraft://...`), and `explore_area` prompt.
- Verified 20/20 tests passing in `scripts/test_phase1_client.py`.

### Phase 2: World Mutation, Player Actions & Direct Building (COMPLETED & VERIFIED)
- Closed-loop `OBSERVE` -> `ACT` -> `VERIFY` mutation pattern with structured action results.
- Generic block interaction primitive `interact_with_block` (doors, levers, buttons, chests, containers).
- 6-stage safe batch pipeline (`place_blocks`, `fill_region`) with strict boundaries ($Y \in [-64, 320]$, $\le 500$ blocks).
- Waypoint locomotion (`move_to`) with stuck detection and immediate cancellation (`stop_movement`).
- Dynamic action state tracker exposed at `minecraft://action/state`.
- Verified 12/12 tests passing in `scripts/test_phase2_client.py` (100% pass rate).

---

## 4. Critical Rules & Technical Traps (READ BEFORE CODING)

1. **Never Guess APIs**:
   - Production Minecraft 26.2 bytecode uses Mojang names (`ServerPlayer`, `ServerLevel`, `BlockPos`), **NOT** legacy Yarn names (`ServerWorld`, `PlayerEntity`).
   - Consult `docs/fabric/api-research-26.2.md` for exact method signatures before calling any Minecraft API.

2. **Strict Thread Safety**:
   - Minecraft world mutation and entity manipulation **must happen on the Server Thread**.
   - Netty HTTP worker threads must **never** call `level.setBlock()` or `player.teleportTo()` directly.
   - All tasks must be scheduled via `TickSchedulerService` (executing inside `ServerTickEvents.END_SERVER_TICK`).

3. **Loom Non-Obfuscated Rules**:
   - `fabric.loom.disableObfuscation=true` is enabled in `gradle.properties`.
   - **DO NOT** use `modImplementation`, `modCompileOnly`, or `loom.officialMojangMappings()`. Use standard Gradle `implementation` / `compileOnly`.

4. **Minecraft 26.x Data Components Shift**:
   - `ItemStack.getTag()` and `getOrCreateTag()` **do not exist**.
   - Item metadata uses Data Components: `stack.get(DataComponents.CUSTOM_NAME)`, `stack.get(DataComponents.DAMAGE)`.

5. **Player Navigation**:
   - `ServerPlayer` does **not** have `Mob.getNavigation()`.
   - Player movement must be executed via waypoint step interpolation or `teleportTo(x, y, z)`.

6. **Block Placement Flags**:
   - When placing blocks, use `Block.UPDATE_ALL_IMMEDIATE` (`11` = `UPDATE_NEIGHBORS | UPDATE_CLIENTS | UPDATE_IMMEDIATE`) to ensure clients update immediately and block physics (sand, redstone, water) trigger properly.

---

## 5. Next Phase: Phase 3 Roadmap (Combat, 3D Navigation & Autonomous Construction)
## 5. Phase 3: Spatial Intelligence, Architectural Planning & Autonomous Construction (COMPLETED & VERIFIED)

The next session will implement **Phase 3: Tactical Combat, 3D A* Navigation & Autonomous Blueprints**:
- **Tactical Combat**: Melee attack primitives respecting weapon cooldowns (0.625s), reach checks ($\le 3.5$), and retreat thresholds ($< 6.0$ HP).
- **3D A\* Navigation**: Voxel pathfinding engine navigating slopes, stair stepping, jump traversals, and dynamic obstacles.
- **Autonomous Construction**: Layer-by-layer architectural blueprint compiler (`build_house`, `build_wall`, `build_roof`, `find_build_location`).
- **Autonomous Workflows**: Agent prompt templates `build_house`, `defend_player`, `build_and_defend`.
Phase 3 transforms the server into an autonomous architectural construction system:
- **Generic Architectural Blueprints**: Multi-structure blueprint compiler (`build_structure`) supporting towers, bridges, walls, houses, castles, farms, temples, and custom designs.
- **Semantic Structural Primitives**: High-level building primitives (`build_wall`, `build_roof`, `build_foundation`, `build_pillar`).
- **Resource Management & Acquisition**: Inventory bill-of-materials calculation, deficit tracking, crafting recipe resolution, and `WAITING_FOR_RESOURCES` recovery.
- **Spatial World Model & 3D Navigation**: Persistent cartography (`minecraft://world/map`), terrain flatness analyzer (`find_build_location`), and 3D A* pathfinding (`navigate_to`).
- **Closed-Loop Structure Verification & Repair**: Deep physical inspection comparing planned vs. actual voxels, automated defect remediation (`repair_structure`).
- **Event-Driven Aggregator**: Ticks filtered into high-level agent events to minimize LLM cognitive churn.
- **Verification**: Verified 12/12 tests passing in `scripts/test_phase3_client.py` (100% pass rate). Total project tests: 44/44 passing.

### Autonomous Architectural Monuments (COMPLETED & VERIFIED)
- **The Taj Mahal** at `(-181, 74, 167)`:
  - 3,859 blocks placed, 100.0% physical ground-truth verification (0 discrepancies).
  - Elevated plinth, 4 minarets, central octagonal mausoleum, 4 pishtaq iwans with lapis/gold inlays, central onion dome with gold finial, and Charbagh reflecting pool.
- **The Qutub Minar & Iron Pillar of Delhi** at `(-234, 69, 194)`:
  - 2,592 blocks placed, 100.0% physical ground-truth verification (0 discrepancies).
  - 5 tapering storeys rising 48 blocks to $Y=117$, 24 alternating circular and angular flutings, 4 muqarnas corbel balconies with iron railings, contrasting white marble upper tiers, observation cupola, internal spiral staircase, courtyard plinth, and ancient rustless Iron Pillar of Delhi (`anvil` + `polished_blackstone_wall`).

---

## 6. Helpful Commands Quick-Reference

```bash
# Build the Fabric mod JAR
cd fabric-mod && ./gradlew build

# Run dedicated Minecraft server with mod loaded
cd fabric-mod && ./gradlew runServer

# Query bridge health/info once started (Phase 2)
curl -s http://127.0.0.1:25585/api/v1/world/info | jq .

# Decompile or inspect any 26.2 class bytecode
/opt/homebrew/opt/openjdk@25/bin/javap -cp ~/.gradle/caches/fabric-loom/minecraftMaven/net/minecraft/minecraft-merged-deobf/26.2/minecraft-merged-deobf-26.2.jar <full.class.Name>

# Python virtual environment activation
source .venv/bin/activate
```

---

## 7. Key Documentation Links
- Implementation Rules: [`implementation.md`](file:///Users/arhamowais/minecraft-mcp/implementation.md)
- 26.2 API Research Pass: [`docs/fabric/api-research-26.2.md`](file:///Users/arhamowais/minecraft-mcp/docs/fabric/api-research-26.2.md)
- 26.2 Primitive Specification: [`docs/implementation/primitive-spec-26.2.md`](file:///Users/arhamowais/minecraft-mcp/docs/implementation/primitive-spec-26.2.md)

