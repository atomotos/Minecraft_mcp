# Minecraft 26.2 MCP Bridge Primitive Specification

**Specification Version**: `1.0.0`  
**Target Environment**: Minecraft Java Edition `26.2` (Fabric)  
**Document Purpose**: Concrete interface, DTO, REST API, and WebSocket contract for the Minecraft MCP Bridge.

---

## 1. Network Contract & Protocol Conventions

- **Default Port**: `25585` (binds to `127.0.0.1`)
- **REST Base Path**: `http://127.0.0.1:25585/api/v1`
- **WebSocket Path**: `ws://127.0.0.1:25585/api/v1/ws/player`
- **Content-Type**: `application/json; charset=utf-8`

### Standard Response Envelope
All REST responses follow this JSON structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "tick": 45120
}
```

When an operation fails:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "OUT_OF_BOUNDS",
    "message": "Coordinates (100, 350, 200) exceed maximum world height (320)"
  },
  "tick": 45120
}
```

### Standard Error Codes
| Code | HTTP Status | Description |
| :--- | :--- | :--- |
| `INVALID_ARGUMENT` | 400 | Request parameters failed validation or malformed JSON |
| `PLAYER_NOT_FOUND` | 404 | Specified player is not currently connected to the server |
| `ENTITY_NOT_FOUND` | 404 | Specified entity ID is dead, removed, or nonexistent |
| `CHUNK_UNLOADED` | 409 | Requested block or coordinate is in an unloaded chunk |
| `OUT_OF_BOUNDS` | 409 | Coordinates are outside world boundaries or world border |
| `INVALID_ACTION` | 422 | Action cannot be performed in the current context |
| `SERVER_ERROR` | 500 | Unhandled internal exception on the server tick thread |

---

## 2. Java Service Interfaces

These Java interfaces define the server-side bridge contract implemented in the Fabric mod.

```java
package com.minecraftmcp.bridge.service;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.function.Supplier;

public interface TickSchedulerService {
    <T> CompletableFuture<T> enqueue(Supplier<T> task);
    CompletableFuture<Void> enqueue(Runnable task);
    long getCurrentTick();
}

public interface ObservationService {
    ServerPlayer resolvePlayer(String nameOrUuid);
    Vec3 getPlayerPosition(ServerPlayer player);
    float[] getPlayerRotation(ServerPlayer player); // [yaw, pitch, headYaw]
    float[] getPlayerVitals(ServerPlayer player);   // [health, maxHealth, food, saturation]
    String getPlayerGameMode(ServerPlayer player);
    List<InventorySlotDto> getInventory(ServerPlayer player);
    BlockState getBlockState(BlockPos pos);
    List<BlockInfoDto> getBlocksInBounds(BlockPos min, BlockPos max);
    List<EntityInfoDto> getNearbyEntities(ServerPlayer player, double radius, String filterType);
    WorldInfoDto getWorldInfo();
}

public interface WorldMutationService {
    StructuredActionResultDto setBlock(BlockPos pos, BlockState state, int flags);
    StructuredActionResultDto breakBlock(BlockPos pos, boolean dropItems, ServerPlayer player);
    StructuredActionResultDto fillRegion(BlockPos min, BlockPos max, BlockState state, Optional<String> replaceFilter);
    StructuredActionResultDto interactWithBlock(ServerPlayer player, BlockPos pos, InteractionHand hand);
    boolean canPlaceBlock(BlockPos pos, BlockState state);
    boolean isChunkLoaded(BlockPos pos);
    boolean isInWorldBounds(BlockPos pos);
}

public interface PlayerActionService {
    boolean teleport(ServerPlayer player, Vec3 targetPos, float yaw, float pitch);
    void setVelocity(ServerPlayer player, Vec3 velocity);
    void setRotation(ServerPlayer player, float yaw, float pitch);
    void setSelectedSlot(ServerPlayer player, int slotIndex);
    boolean equipItem(ServerPlayer player, EquipmentSlot slot, ItemStack stack);
    boolean useItem(ServerPlayer player, InteractionHand hand);
    boolean useItemOnBlock(ServerPlayer player, InteractionHand hand, BlockPos pos, Direction side);
    boolean mineBlock(ServerPlayer player, BlockPos pos);
    boolean dropItem(ServerPlayer player, boolean dropEntireStack);
    void swingHand(ServerPlayer player, InteractionHand hand);
    MovementResultDto moveTowards(ServerPlayer player, Vec3 targetPos, double speed, double tolerance);
    MovementResultDto stopMovement(ServerPlayer player);
}

public interface CombatService {
    boolean attackEntity(ServerPlayer player, int targetEntityId);
    double getAttackRange(ServerPlayer player);
    Optional<Entity> findTarget(ServerPlayer player, double maxRange);
    LivingEntityStatusDto getEntityStatus(int entityId);
}
```

---

## 3. REST API Endpoint Specifications

---

### 3.1 Observation Endpoints

#### `GET /api/v1/player/status`
Returns complete status overview for a player.
- **Query Parameters**:
  - `player` (optional): Username or UUID (defaults to first online player if omitted)
- **Response `data`**:
  ```json
  {
    "uuid": "380df991-f603-344c-a090-369bad2a024a",
    "name": "AgentBot",
    "position": { "x": 124.5, "y": 68.0, "z": -45.5 },
    "blockPosition": { "x": 124, "y": 68, "z": -45 },
    "rotation": { "yaw": 90.0, "pitch": 0.0, "headYaw": 90.0 },
    "health": 20.0,
    "maxHealth": 20.0,
    "food": 20,
    "saturation": 5.0,
    "gameMode": "survival",
    "dimension": "minecraft:overworld",
    "selectedSlot": 0,
    "heldItem": {
      "id": "minecraft:diamond_sword",
      "count": 1,
      "damage": 0
    }
  }
  ```

#### `GET /api/v1/player/position`
High-speed endpoint returning only player position and facing angle.
- **Query Parameters**: `player` (optional)
- **Response `data`**:
  ```json
  {
    "x": 124.5,
    "y": 68.0,
    "z": -45.5,
    "yaw": 90.0,
    "pitch": 0.0
  }
  ```

#### `GET /api/v1/player/inventory`
Lists all 36 inventory slots, plus armor and offhand.
- **Query Parameters**: `player` (optional)
- **Response `data`**:
  ```json
  {
    "selectedSlot": 0,
    "hotbar": [
      { "slot": 0, "id": "minecraft:diamond_sword", "count": 1 },
      { "slot": 1, "id": "minecraft:iron_pickaxe", "count": 1 },
      { "slot": 2, "id": "minecraft:bread", "count": 32 }
    ],
    "main": [
      { "slot": 9, "id": "minecraft:oak_planks", "count": 64 }
    ],
    "armor": {
      "head": { "id": "minecraft:iron_helmet", "count": 1 },
      "chest": null,
      "legs": null,
      "feet": null
    },
    "offhand": null
  }
  ```

#### `GET /api/v1/world/block`
Inspects a single block at given coordinates.
- **Query Parameters**:
  - `x`: integer (required)
  - `y`: integer (required)
  - `z`: integer (required)
- **Response `data`**:
  ```json
  {
    "position": { "x": 124, "y": 67, "z": -45 },
    "blockId": "minecraft:oak_stairs",
    "blockState": "minecraft:oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]",
    "properties": {
      "facing": "north",
      "half": "bottom",
      "shape": "straight",
      "waterlogged": "false"
    },
    "isAir": false,
    "isSolid": true
  }
  ```

#### `POST /api/v1/world/blocks`
Scans a 3D bounding box (max volume: 32,768 blocks).
- **Request Body**:
  ```json
  {
    "min": { "x": 100, "y": 64, "z": 100 },
    "max": { "x": 105, "y": 70, "z": 105 },
    "includeAir": false
  }
  ```
- **Response `data`**:
  ```json
  {
    "count": 12,
    "blocks": [
      {
        "pos": { "x": 100, "y": 64, "z": 100 },
        "id": "minecraft:grass_block"
      }
    ]
  }
  ```

#### `GET /api/v1/world/entities`
Lists nearby entities.
- **Query Parameters**:
  - `radius`: float, max `64.0` (default `16.0`)
  - `type`: string (`all`, `living`, `monster`, `player`, `item`)
- **Response `data`**:
  ```json
  {
    "entities": [
      {
        "id": 142,
        "uuid": "7a40b991-...",
        "type": "minecraft:zombie",
        "position": { "x": 120.2, "y": 68.0, "z": -40.1 },
        "health": 20.0,
        "maxHealth": 20.0,
        "isAlive": true,
        "distance": 6.8
      }
    ]
  }
  ```

#### `GET /api/v1/world/info`
Returns global world state.
- **Response `data`**:
  ```json
  {
    "dimension": "minecraft:overworld",
    "timeOfDay": 6000,
    "gameTime": 142800,
    "isDay": true,
    "isRaining": false,
    "isThundering": false,
    "minY": -64,
    "height": 384
  }
  ```

---

### 3.2 World Mutation Endpoints

#### `POST /api/v1/world/set_block`
Sets a block at specific coordinates.
- **Request Body**:
  ```json
  {
    "x": 124,
    "y": 68,
    "z": -45,
    "blockState": "minecraft:oak_planks",
    "flags": 11
  }
  ```
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "place_block",
    "position": { "x": 124, "y": 68, "z": -45 },
    "block": "minecraft:oak_planks",
    "previous_block": "minecraft:air",
    "verified": true,
    "tick": 12500
  }
  ```

#### `POST /api/v1/world/break_block`
Destroys a block at given coordinates.
- **Request Body**:
  ```json
  {
    "x": 124,
    "y": 68,
    "z": -45,
    "dropResources": true
  }
  ```
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "break_block",
    "position": { "x": 124, "y": 68, "z": -45 },
    "previous_block": "minecraft:stone",
    "current_block": "minecraft:air",
    "verified": true,
    "dropped_items": true,
    "tick": 12505
  }
  ```

#### `POST /api/v1/world/fill`
Fills a bounding box region with a specified block.
- **Request Body**:
  ```json
  {
    "from": { "x": 100, "y": 64, "z": 100 },
    "to": { "x": 102, "y": 64, "z": 102 },
    "blockState": "minecraft:stone",
    "replaceFilter": null
  }
  ```
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "fill_region",
    "from": { "x": 100, "y": 64, "z": 100 },
    "to": { "x": 102, "y": 64, "z": 102 },
    "block": "minecraft:stone",
    "volume": 9,
    "placed_count": 9,
    "failed_count": 0,
    "verified": true,
    "tick": 12510
  }
  ```

#### `POST /api/v1/world/interact`
Simulates player interaction with a block (chest, crafting table, furnace, door, button, lever).
- **Request Body**:
  ```json
  {
    "x": 124,
    "y": 68,
    "z": -45,
    "hand": "MAIN_HAND"
  }
  ```
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "interact_with_block",
    "position": { "x": 124, "y": 68, "z": -45 },
    "target_block": "minecraft:oak_door[open=true]",
    "interaction_type": "door_toggle",
    "state_changed": true,
    "verified": true,
    "tick": 12515
  }
  ```

#### `POST /api/v1/world/check_placement`
Tests if a block state can survive at coordinates without placing it.
- **Request Body**:
  ```json
  {
    "x": 124,
    "y": 68,
    "z": -45,
    "blockState": "minecraft:wall_torch[facing=north]"
  }
  ```
- **Response `data`**:
  ```json
  {
    "canSurvive": true
  }
  ```

---

### 3.3 Player Action Endpoints

#### `POST /api/v1/player/move`
Executes basic waypoint-based player movement with stuck detection.
- **Request Body**:
  ```json
  {
    "x": 125.0,
    "y": 68.0,
    "z": -40.0,
    "speed": 1.0,
    "tolerance": 1.0
  }
  ```
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "move_to",
    "start_position": { "x": 120.0, "y": 68.0, "z": -40.0 },
    "current_position": { "x": 125.0, "y": 68.0, "z": -40.0 },
    "target_position": { "x": 125.0, "y": 68.0, "z": -40.0 },
    "status": "reached",
    "distance_remaining": 0.0,
    "tick": 12520
  }
  ```

#### `POST /api/v1/player/stop`
Immediately cancels active player movement.
- **Request Body**: `{}`
- **Response `data` (Structured Action Result)**:
  ```json
  {
    "action": "stop_movement",
    "final_position": { "x": 122.5, "y": 68.0, "z": -40.0 },
    "status": "cancelled",
    "tick": 12522
  }
  ```

#### `POST /api/v1/player/teleport`
Moves the player to target coordinates.
- **Request Body**:
  ```json
  {
    "x": 125.0,
    "y": 68.0,
    "z": -44.0,
    "yaw": 90.0,
    "pitch": 0.0
  }
  ```
- **Response `data`**:
  ```json
  {
    "teleported": true,
    "position": { "x": 125.0, "y": 68.0, "z": -44.0 }
  }
  ```

#### `POST /api/v1/player/rotate`
Rotates player head/body angles without moving position.
- **Request Body**:
  ```json
  {
    "yaw": 180.0,
    "pitch": -15.0
  }
  ```
- **Response `data`**:
  ```json
  {
    "yaw": 180.0,
    "pitch": -15.0
  }
  ```

#### `POST /api/v1/player/select_slot`
Switches active hotbar slot.
- **Request Body**:
  ```json
  {
    "slot": 2
  }
  ```
- **Response `data`**:
  ```json
  {
    "selectedSlot": 2,
    "item": { "id": "minecraft:bread", "count": 32 }
  }
  ```

#### `POST /api/v1/player/equip`
Places an item into an equipment slot.
- **Request Body**:
  ```json
  {
    "slot": "HEAD",
    "item": "minecraft:diamond_helmet",
    "count": 1
  }
  ```
- **Response `data`**:
  ```json
  {
    "slot": "HEAD",
    "equipped": true
  }
  ```

#### `POST /api/v1/player/use_item`
Simulates right-click (in air or on target block).
- **Request Body**:
  ```json
  {
    "hand": "MAIN_HAND",
    "targetBlock": { "x": 124, "y": 67, "z": -45 },
    "direction": "UP"
  }
  ```
- **Response `data`**:
  ```json
  {
    "result": "SUCCESS"
  }
  ```

#### `POST /api/v1/player/mine`
Simulates player mining a block using held tool.
- **Request Body**:
  ```json
  {
    "x": 124,
    "y": 68,
    "z": -45
  }
  ```
- **Response `data`**:
  ```json
  {
    "mined": true
  }
  ```

#### `POST /api/v1/player/drop`
Drops item from selected hotbar slot.
- **Request Body**:
  ```json
  {
    "entireStack": false
  }
  ```
- **Response `data`**:
  ```json
  {
    "dropped": true
  }
  ```

#### `POST /api/v1/player/swing`
Plays arm swing animation.
- **Request Body**:
  ```json
  {
    "hand": "MAIN_HAND"
  }
  ```
- **Response `data`**:
  ```json
  {
    "swung": true
  }
  ```

---

### 3.4 Combat Endpoints

#### `POST /api/v1/combat/attack`
Executes melee attack against target entity ID.
- **Request Body**:
  ```json
  {
    "targetEntityId": 142
  }
  ```
- **Response `data`**:
  ```json
  {
    "attacked": true,
    "targetEntityId": 142,
    "targetAlive": true,
    "targetRemainingHealth": 12.5
  }
  ```

#### `GET /api/v1/combat/target`
Finds optimal hostile target within player line-of-sight and reach.
- **Query Parameters**:
  - `maxRange`: float (default `3.0`)
- **Response `data`**:
  ```json
  {
    "target": {
      "id": 142,
      "type": "minecraft:zombie",
      "distance": 2.4,
      "health": 20.0
    }
  }
  ```

---

## 4. WebSocket Real-Time Position Stream Specification

### 4.1 Connection Lifecycle
- **URL**: `ws://127.0.0.1:25585/api/v1/ws/player`
- **Protocol**: Standard WebSocket (RFC 6455) using Netty `WebSocketServerProtocolHandler`
- **Heartbeat**: Ping/Pong frame every 15 seconds.

### 4.2 Subscription Message (Client → Server)
Upon connecting, the MCP client sends:
```json
{
  "action": "subscribe",
  "player": "AgentBot",
  "intervalTicks": 1
}
```

### 4.3 Tick Stream Event (Server → Client)
Broadcasted every `intervalTicks` during `ServerTickEvents.END_SERVER_TICK`:
```json
{
  "event": "player_tick",
  "tick": 45121,
  "player": "AgentBot",
  "pos": {
    "x": 124.52,
    "y": 68.0,
    "z": -45.48
  },
  "rot": {
    "yaw": 92.4,
    "pitch": 2.1
  },
  "health": 20.0,
  "food": 20
}
```

### 4.4 Unsubscribe Message (Client → Server)
```json
{
  "action": "unsubscribe"
}
```

