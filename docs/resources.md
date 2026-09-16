# MCP Resources & Subscriptions Specification

In the Model Context Protocol (MCP 2.0), **Resources** provide real-time and static context data to the LLM. Rather than invoking active tools to fetch passive information, the client reads or subscribes to standard resource URIs.

With the **Fabric Mod Bridge (Option 2)**, resources are sourced directly from Minecraft internal server data structures via localhost REST and WebSocket streams, providing sub-millisecond data retrieval.

---

## 1. Resource Catalog Overview

| URI | Subscribable | Source / Fabric API | Update Rate |
| :--- | :---: | :--- | :---: |
| `minecraft://player` | Yes | `GET /api/player/{name}` (`ServerPlayerEntity`) | 2 Hz |
| `minecraft://player/position` | **Yes** | `WS /ws/events` (`player_position_changed`) | Real-time (Event-driven) |
| `minecraft://player/inventory` | Yes | `GET /api/player/{name}/inventory` (`PlayerInventory`) | On Change / WS Push |
| `minecraft://player/equipment` | Yes | `GET /api/player/{name}` (`equipment` slots) | On Change |
| `minecraft://player/effects` | Yes | `GET /api/player/{name}` (`getStatusEffects()`) | On Change |
| `minecraft://world` | No | `GET /api/status` (`MinecraftServer`, `ServerWorld`) | On Read |
| `minecraft://world/time` | Yes | `GET /api/status` (`getTimeOfDay()`) | 0.1 Hz |
| `minecraft://world/weather` | Yes | `GET /api/status` (`isRaining()`, `isThundering()`) | On Change |
| `minecraft://world/biome` | No | `GET /api/world/biome` (`getBiome()`) | On Read |
| `minecraft://world/nearby_blocks` | No | `POST /api/world/inspect` (`getBlockState()`) | On Read |
| `minecraft://entities/nearby` | Yes | `GET /api/entities/nearby` (`getOtherEntities()`) | 1 Hz |
| `minecraft://players/nearby` | Yes | `GET /api/entities/nearby?type=player` | 2 Hz |
| `minecraft://mobs/nearby` | Yes | `GET /api/entities/nearby?type=mob` | 2 Hz |
| `minecraft://knowledge/blocks` | No | Local static knowledge cache | Static |
| `minecraft://knowledge/items` | No | Local static knowledge cache | Static |
| `minecraft://knowledge/recipes` | No | Local static knowledge cache | Static |
| `minecraft://knowledge/building` | No | Local static knowledge cache | Static |
| `minecraft://knowledge/combat` | No | Local static knowledge cache | Static |
| `minecraft://agent/current_plan` | Yes | Memory state cache in Python MCP server | On Update |

---

## 2. Real-Time Subscription: `minecraft://player/position`

The MCP server exposes player position as an event-driven resource subscription. Clients subscribe once, and the server pushes JSON-RPC notifications whenever the player moves significantly ($\Delta \text{distance} \ge 0.5$ blocks).

### Subscription Flow over WebSocket

```
Minecraft Java 26.2 (Fabric)
    │
    │ ServerTickEvents.END_SERVER_TICK (Delta >= 0.5m)
    ▼
Fabric Mod Bridge (/ws/events)
    │
    │ WebSocket JSON frame: {"event": "player_position_changed", ...}
    ▼
Python MCP Server
    │
    │ MCP 2.0 Notification over stdio
    ▼
LLM Client: notifications/resources/updated {"uri": "minecraft://player/position"}
```

### Client Subscription Request
```json
{
  "jsonrpc": "2.0",
  "id": 101,
  "method": "resources/subscribe",
  "params": {
    "uri": "minecraft://player/position"
  }
}
```

### Server Notification Event
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/updated",
  "params": {
    "uri": "minecraft://player/position"
  }
}
```

### Resource Content Payload Schema
When read via `resources/read`:
```json
{
  "uri": "minecraft://player/position",
  "mimeType": "application/json",
  "text": {
    "player": "Steve",
    "dimension": "minecraft:overworld",
    "x": 128.45,
    "y": 64.0,
    "z": -210.12,
    "block_x": 128,
    "block_y": 64,
    "block_z": -210,
    "yaw": -90.0,
    "pitch": 5.2,
    "on_ground": true,
    "in_water": false,
    "timestamp": 1773789123.45
  }
}
```

---

## 3. Player State Resources

### `minecraft://player`
Extracted directly from `GET /api/player/Steve`:
```json
{
  "name": "Steve",
  "health": 18.5,
  "max_health": 20.0,
  "food_level": 17,
  "saturation": 5.0,
  "air": 300,
  "level": 24,
  "experience_progress": 0.42,
  "gamemode": "survival",
  "score": 1240
}
```

### `minecraft://player/inventory`
Extracted directly from `GET /api/player/Steve/inventory`:
```json
{
  "hotbar": [
    {"slot": 0, "id": "minecraft:diamond_sword", "count": 1, "damage": 0},
    {"slot": 1, "id": "minecraft:diamond_pickaxe", "count": 1, "damage": 42},
    {"slot": 2, "id": "minecraft:golden_apple", "count": 12},
    {"slot": 3, "id": "minecraft:oak_planks", "count": 64},
    {"slot": 4, "id": "minecraft:oak_planks", "count": 60},
    {"slot": 5, "id": "minecraft:torch", "count": 32}
  ],
  "totals": {
    "minecraft:oak_planks": 124,
    "minecraft:cobblestone": 87,
    "minecraft:glass": 32,
    "minecraft:iron_ingot": 14,
    "minecraft:golden_apple": 12,
    "minecraft:diamond": 3
  },
  "free_slots": 24
}
```

### `minecraft://player/equipment`
Active gear slots:
```json
{
  "mainhand": {"id": "minecraft:diamond_sword", "count": 1, "damage": 7.0},
  "offhand": {"id": "minecraft:shield", "durability": 310},
  "head": {"id": "minecraft:iron_helmet", "armor": 2},
  "chest": {"id": "minecraft:diamond_chestplate", "armor": 8},
  "legs": {"id": "minecraft:iron_leggings", "armor": 5},
  "feet": {"id": "minecraft:iron_boots", "armor": 2}
}
```

---

## 4. World & Environment Resources

### `minecraft://world`
Extracted from `GET /api/status`:
```json
{
  "name": "world",
  "minecraft_version": "26.2",
  "time_of_day": 6000,
  "phase": "day",
  "day_count": 14,
  "weather": "clear",
  "difficulty": "normal",
  "spawn": [100, 64, 200]
}
```

### `minecraft://world/time`
```json
{
  "game_time": 348210,
  "day_time": 6000,
  "is_day": true,
  "is_night": false,
  "can_sleep": false,
  "light_level": 15
}
```

---

## 5. Entity Resources

### `minecraft://entities/nearby`
Extracted from `GET /api/entities/nearby`:
```json
[
  {
    "id": "entity-1248",
    "type": "player",
    "name": "Alex",
    "distance": 12.4,
    "health": 14.0,
    "position": [140.8, 64.0, -215.2],
    "is_hostile": false
  },
  {
    "id": "entity-1302",
    "type": "zombie",
    "name": "Zombie",
    "distance": 7.8,
    "health": 20.0,
    "position": [135.2, 63.0, -205.5],
    "is_hostile": true
  }
]
```

---

## 6. Static Knowledge Base Resources

Static resources prevent the LLM from hallucinating crafting recipes, item values, or block traits. They are cached locally in memory and returned instantly.

### `minecraft://knowledge/blocks`
```json
{
  "minecraft:oak_planks": {
    "hardness": 2.0,
    "flammable": true,
    "requires_tool": false,
    "preferred_tool": "axe",
    "transparent": false
  },
  "minecraft:stone": {
    "hardness": 1.5,
    "flammable": false,
    "requires_tool": true,
    "preferred_tool": "pickaxe",
    "drops": "minecraft:cobblestone"
  },
  "minecraft:glass": {
    "hardness": 0.3,
    "flammable": false,
    "requires_tool": false,
    "transparent": true,
    "drops_self": false
  }
}
```

### `minecraft://knowledge/combat`
```json
{
  "attack_cooldowns": {
    "minecraft:diamond_sword": 0.625,
    "minecraft:iron_sword": 0.625,
    "minecraft:diamond_axe": 1.0,
    "minecraft:iron_axe": 1.11
  },
  "reach_distance": 3.0,
  "critical_hit_multiplier": 1.5,
  "shield_disable_seconds": 5.0
}
```

---

## 7. Dynamic Agent Memory: `minecraft://agent/current_plan`

Maintains the active cognitive plan across tool calls:
```json
{
  "task": "build_oak_house",
  "status": "in_progress",
  "origin": [100, 65, 200],
  "dimensions": {"width": 9, "depth": 7, "height": 5},
  "materials": {
    "foundation": "minecraft:cobblestone",
    "walls": "minecraft:oak_planks",
    "roof": "minecraft:oak_stairs"
  },
  "completed": ["site_survey", "foundation", "floor"],
  "current_stage": "walls",
  "remaining": ["doors_and_windows", "roof", "lighting"]
}
```
Client agents can update this resource using the internal state engine during task execution.
