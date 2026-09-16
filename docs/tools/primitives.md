# Primitive Tools Reference Manual

This document provides the complete, authoritative specification for all **Primitive MCP Tools** in the Minecraft Java Edition MCP Server 2.0.

Primitive tools are the atomic, low-level building blocks exposed to the LLM. High-level composite tools (`build_structure`, `build_wall`, etc.) orchestrate these primitives to accomplish autonomous goals.

Under the hood, all primitive tools interact with the **Fabric Server-Side Mod Bridge** (`http://127.0.0.1:25585`) rather than slow, text-based RCON commands, enabling direct access to Minecraft World and Entity APIs.

---

## Tool Category Index

1. [Observation Primitives](#1-observation-primitives)
   - [`inspect_area`](#inspect_area)
   - [`get_block`](#get_block)
   - [`get_blocks`](#get_blocks)
   - [`get_player_state`](#get_player_state)
   - [`get_inventory`](#get_inventory)
   - [`get_entities`](#get_entities)
   - [`get_nearby_players`](#get_nearby_players)
2. [Building & World Manipulation Primitives](#2-building--world-manipulation-primitives)
   - [`place_block`](#place_block)
   - [`place_blocks`](#place_blocks)
   - [`break_block`](#break_block)
   - [`break_blocks`](#break_blocks)
   - [`fill_region`](#fill_region)
3. [Movement & Orientation Primitives](#3-movement--orientation-primitives)
   - [`move_to`](#move_to)
   - [`look_at`](#look_at)
   - [`jump`](#jump)
   - [`stop`](#stop)
4. [Inventory & Equipment Primitives](#4-inventory--equipment-primitives)
   - [`equip_item`](#equip_item)
   - [`use_item`](#use_item)
   - [`drop_item`](#drop_item)
   - [`craft_item`](#craft_item)
5. [Spatial & Verification Primitives](#5-spatial--verification-primitives)
   - [`scan_region`](#scan_region)
   - [`mark_location`](#mark_location)
   - [`get_landmarks`](#get_landmarks)
   - [`check_requirements`](#check_requirements)
   - [`repair_structure`](#repair_structure)
6. [Server & Bridge Primitives](#6-server--bridge-primitives)
   - [`execute_command`](#execute_command)

---

## 1. Observation Primitives

### `inspect_area`
Inspects a 3D block volume around a center coordinate and returns a compact, token-efficient representation directly from Fabric's `ServerWorld.getBlockState()`.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `center` | `[number, number, number]` | Yes | — | Center coordinates `[x, y, z]`. |
| `radius` | `integer` | No | `8` | Cuboid half-width (1 to 16 blocks). |
| `format` | `string` | No | `"summary"` | Output representation: `"summary"`, `"ascii"`, `"sparse"`, or `"detailed"`. |
| `filter` | `string` | No | `null` | Optional block category filter (e.g. `"solid"`, `"hazards"`, `"ores"`). |

#### Return Schema
```json
{
  "center": [100, 64, 200],
  "radius": 8,
  "format": "summary",
  "terrain": {
    "flatness": 0.94,
    "min_y": 63,
    "max_y": 65,
    "surface_material": "minecraft:grass_block"
  },
  "materials": {
    "minecraft:grass_block": 112,
    "minecraft:dirt": 64,
    "minecraft:stone": 30,
    "minecraft:oak_log": 8
  },
  "hazards": []
}
```

#### Under the Hood (Fabric Mod Bridge)
Dispatches an HTTP request:
```http
POST /api/world/inspect
Content-Type: application/json

{"center": [100, 64, 200], "radius": 8, "format": "summary"}
```
The Fabric mod iterates over `BlockPos` in the loaded chunk memory, compiles summary statistics, and returns JSON in $< 2\text{ms}$.

---

### `get_block`
Inspects a single block at specified coordinates.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `x` | `integer` | Yes | — | Block X coordinate. |
| `y` | `integer` | Yes | — | Block Y coordinate. |
| `z` | `integer` | Yes | — | Block Z coordinate. |

#### Return Schema
```json
{
  "pos": [100, 64, 200],
  "block": "minecraft:chest",
  "properties": {
    "facing": "north",
    "type": "single",
    "waterlogged": "false"
  },
  "is_solid": true,
  "is_transparent": false
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `GET /api/world/block?x=100&y=64&z=200`, querying `world.getBlockState(new BlockPos(x, y, z))`.

---

### `get_blocks`
Inspects a targeted cuboid bounding box.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `from_pos` | `[integer, integer, integer]` | Yes | — | Starting corner `[x, y, z]`. |
| `to_pos` | `[integer, integer, integer]` | Yes | — | Opposite corner `[x, y, z]`. |
| `omit_air` | `boolean` | No | `true` | Exclude air blocks from payload. |

---

### `get_player_state`
Queries the live vital statistics and status of a player directly from `ServerPlayerEntity`.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `player_name` | `string` | No | Target Player | Username of player. |

#### Return Schema
```json
{
  "player": "Steve",
  "health": 19.0,
  "food_level": 18,
  "saturation": 4.5,
  "position": [102.4, 64.0, 198.7],
  "dimension": "minecraft:overworld",
  "gamemode": "survival",
  "effects": [
    {"effect": "minecraft:speed", "amplifier": 1, "duration_seconds": 45}
  ]
}
```

#### Under the Hood (Fabric Mod Bridge)
Queries `GET /api/player/Steve`. The Fabric mod reads `player.getHealth()`, `player.getHungerManager().getFoodLevel()`, and `player.getStatusEffects()`.

---

### `get_inventory`
Inspects inventory items, stack counts, and free capacity directly from `PlayerInventory`.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `player_name` | `string` | No | Target Player | Username of player. |

#### Return Schema
```json
{
  "totals": {
    "minecraft:oak_planks": 64,
    "minecraft:cobblestone": 128,
    "minecraft:iron_sword": 1
  },
  "free_slots": 22,
  "held_item": "minecraft:iron_sword"
}
```

#### Under the Hood (Fabric Mod Bridge)
Queries `GET /api/player/Steve/inventory`.

---

### `get_entities`
Scans entities within range via `ServerWorld.getOtherEntities()`.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `radius` | `number` | No | `16.0` | Search radius in blocks. |
| `type_filter` | `string` | No | `null` | Filter: `"all"`, `"players"`, `"hostile"`, `"passive"`. |

---

### `get_nearby_players`
Dedicated player detection tool for PvP and team tracking.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `radius` | `number` | No | `32.0` | Search radius in blocks. |

#### Return Schema
```json
[
  {
    "name": "Alex",
    "distance": 8.4,
    "health": 16.0,
    "position": [108.2, 64.0, 201.5],
    "holding": "minecraft:bow"
  }
]
```

#### Under the Hood (Fabric Mod Bridge)
Queries `GET /api/entities/nearby?type=player&radius=32`.

---

## 2. Building & World Manipulation Primitives

### `place_block`
Places a single block at exact coordinates using `ServerWorld.setBlockState()`.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `x` | `integer` | Yes | — | Target X. |
| `y` | `integer` | Yes | — | Target Y. |
| `z` | `integer` | Yes | — | Target Z. |
| `block` | `string` | Yes | — | Block ID with optional state, e.g. `"minecraft:oak_stairs[facing=north]"`. |

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "place_block",
  "position": {"x": 100, "y": 64, "z": 200},
  "block": "minecraft:oak_stairs[facing=north]",
  "previous_block": "minecraft:air",
  "verified": true,
  "tick": 12500
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/world/set_block` with coordinates and state, followed by internal verification.

---

### `place_blocks`
Batch placement of multiple blocks in a single tool call. **This is the primary building primitive for the LLM.**

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `blocks` | `array[object]` | Yes | — | Array of `{x, y, z, block}` objects. |

#### Example Call
```json
{
  "blocks": [
    {"x": 100, "y": 65, "z": 200, "block": "minecraft:oak_planks"},
    {"x": 101, "y": 65, "z": 200, "block": "minecraft:oak_planks"},
    {"x": 102, "y": 65, "z": 200, "block": "minecraft:oak_planks"}
  ]
}
```

#### Under the Hood (Fabric Mod Bridge)
```http
POST /api/world/blocks/place
Content-Type: application/json

```json
{
  "blocks": [
    {"x": 100, "y": 65, "z": 200, "block": "minecraft:oak_planks"},
    {"x": 101, "y": 65, "z": 200, "block": "minecraft:oak_planks"}
  ],
  "update_neighbors": true
}
```

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "place_blocks",
  "requested_count": 2,
  "placed_count": 2,
  "failed_count": 0,
  "verified": true,
  "bounds": {
    "min": {"x": 100, "y": 65, "z": 200},
    "max": {"x": 101, "y": 65, "z": 200}
  },
  "tick": 12502
}
```
The Fabric mod executes `world.setBlockState(pos, state, Block.UPDATE_ALL_IMMEDIATE)` across the chunk section and verifies placements.

---

### `break_block`
Breaks a block at coordinate with optional drop particles and physics.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `x` | `integer` | Yes | — | Target X. |
| `y` | `integer` | Yes | — | Target Y. |
| `z` | `integer` | Yes | — | Target Z. |
| `drop_loot` | `boolean` | No | `true` | Whether to drop block as an item. |

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "break_block",
  "position": {"x": 100, "y": 64, "z": 200},
  "previous_block": "minecraft:stone",
  "current_block": "minecraft:air",
  "verified": true,
  "dropped_items": true,
  "tick": 12505
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/world/break_block` executing `world.breakBlock(pos, dropLoot)` on the server thread.

---

### `break_blocks`
Batch block destruction.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `blocks` | `array[[int, int, int]]` | Yes | — | List of `[x, y, z]` coordinates to break. |

---

### `fill_region`
Fills a cuboid volume from corner 1 to corner 2 with a specific block. Enforces Phase 2 safety boundaries ($Y \in [-64, 320]$, $\le 500$ blocks maximum).

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `from_pos` | `[integer, integer, integer]` | Yes | — | First corner coordinates `[x1, y1, z1]`. |
| `to_pos` | `[integer, integer, integer]` | Yes | — | Second corner coordinates `[x2, y2, z2]`. |
| `block` | `string` | Yes | — | Block ID to fill with. |
| `replace_filter` | `string` | No | `null` | Optional block to selectively replace (e.g. `"minecraft:water"`). |

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "fill_region",
  "from": {"x": 100, "y": 64, "z": 200},
  "to": {"x": 102, "y": 64, "z": 202},
  "block": "minecraft:stone",
  "volume": 9,
  "placed_count": 9,
  "failed_count": 0,
  "verified": true,
  "tick": 12510
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/world/fill` executing chunk section writes with `Block.UPDATE_ALL_IMMEDIATE` (`11`) on the server thread, with sampled verification (corners + center).

---

### `interact_with_block`
Generic block interaction primitive covering containers, crafting stations, doors, buttons, and levers.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `x` | `integer` | Yes | — | Target block X coordinate. |
| `y` | `integer` | Yes | — | Target block Y coordinate. |
| `z` | `integer` | Yes | — | Target block Z coordinate. |
| `hand` | `string` | No | `"main_hand"` | Hand to interact with (`"main_hand"` or `"off_hand"`). |

#### Representative Supported Interactions
- **Chest / Container**: Opens container menu / triggers container interaction.
- **Crafting Table**: Opens 3x3 crafting screen.
- **Furnace**: Opens furnace interface.
- **Door / Trapdoor**: Toggles open/closed state.
- **Button**: Presses button (activates for button duration).
- **Lever**: Toggles lever power state.

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "interact_with_block",
  "position": {"x": 100, "y": 64, "z": 200},
  "target_block": "minecraft:oak_door[open=true]",
  "interaction_type": "door_toggle",
  "state_changed": true,
  "verified": true,
  "tick": 12515
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/world/interact`. The Fabric mod simulates block interaction via `player.gameMode.useItemOn(...)` or block state interaction on the server thread and verifies state change.

---

## 3. Movement & Orientation Primitives

### `move_to`
Directs the controlled player to perform basic movement towards destination coordinates (waypoint-based / step-wise locomotion, NOT full 3D A* pathfinding which is Phase 3). Includes stuck detection and tolerance thresholds.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `x` | `number` | Yes | — | Destination X coordinate. |
| `y` | `number` | Yes | — | Destination Y coordinate. |
| `z` | `number` | Yes | — | Destination Z coordinate. |
| `speed` | `number` | No | `1.0` | Movement speed multiplier (0.5 to 2.0). |
| `tolerance` | `number` | No | `1.0` | Distance in blocks to consider destination reached. |

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "move_to",
  "start_position": {"x": 100.0, "y": 64.0, "z": 200.0},
  "current_position": {"x": 105.0, "y": 64.0, "z": 200.0},
  "target_position": {"x": 105.0, "y": 64.0, "z": 200.0},
  "status": "reached",
  "distance_remaining": 0.0,
  "tick": 12520
}
```
*Note: If path is obstructed and forward progress halts, `status` returns `"stuck"` with `success: false` and the current position.*

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/player/move`. The mod executes step-based movement across server ticks, updating position and checking for collisions.

---

### `stop_movement`
Halts active player movement immediately, clearing any scheduled navigation steps.

#### Parameters
*None.*

#### Return Schema (Structured Action Result)
```json
{
  "success": true,
  "action": "stop_movement",
  "final_position": {"x": 102.5, "y": 64.0, "z": 200.0},
  "status": "cancelled",
  "tick": 12522
}
```

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/v1/player/stop` to abort the active movement task on the server thread.

---

## 4. Inventory & Equipment Primitives

### `equip_item`
Moves an item from inventory to an active equipment slot.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `item` | `string` | Yes | — | Item identifier (e.g. `"minecraft:diamond_sword"`). |
| `slot` | `string` | No | `"mainhand"` | Target slot: `"mainhand"`, `"offhand"`, `"head"`, `"chest"`, `"legs"`, `"feet"`. |

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/player/{name}/equip` interacting directly with `player.equipStack(EquipmentSlot, itemStack)`.

---

### `use_item`
Simulates right-clicking / consuming held item via `POST /api/action/use`.

---

### `drop_item`
Drops specified items onto the ground via `POST /api/action/drop`.

---

### `craft_item`
Synthesizes a crafted item recipe via `POST /api/action/craft`.

---

## 5. Spatial & Verification Primitives

### `scan_region`
Scans a volume around a center coordinate and incorporates results into the persistent spatial world model (`minecraft://world/map`).

### `mark_location`
Records a point-of-interest or landmark in the spatial world model with category (`base`, `site`, `quarry`, `hazard`) and tags.

### `get_landmarks`
Queries all user or agent registered landmarks from the spatial world model.

### `check_requirements`
Calculates required block quantities for an architectural blueprint and checks against player inventory.

### `repair_structure`
Performs ground-truth physical verification on a constructed structure, detects missing or broken blocks, and executes targeted repairs.

---

## 6. Server & Bridge Primitives

### `execute_command`
Direct fallback bridge to execute a Minecraft Brigadier command directly through Fabric's `CommandDispatcher`.

> [!WARNING]
> Use high-level and domain-specific primitive tools whenever possible. `execute_command` is reserved for administrative tasks or capabilities not yet mapped to tools.

#### Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `command` | `string` | Yes | — | Raw command without leading `/` (e.g. `"time set day"`, `"weather clear"`). |

#### Under the Hood (Fabric Mod Bridge)
Calls `POST /api/server/command` passing the command string directly to `server.getCommandManager().executeWithPrefix(source, command)`.
