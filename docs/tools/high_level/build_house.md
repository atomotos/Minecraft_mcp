# High-Level Tool: `build_house`

The `build_house` tool is the premier high-level architectural constructor in the Minecraft MCP Server. It enables an LLM to commission and build a complete residential structure with a single tool call, abstracting away thousands of individual block placements.

---

## 1. Concept & Rationale

Instead of forcing the LLM to emit 2,000 individual `/setblock` commands, `build_house` takes a parametric specification or architectural blueprint, compiles it into optimized geometric layers, and dispatches batched operations to the Minecraft engine.

```
LLM Agent
   │
   ▼ calls `build_house(origin, style="oak_cabin", width=9, depth=7, height=5)`
┌─────────────────────────────────────────────────────────────┐
│                    Blueprint Compiler                       │
│                                                             │
│  1. Site Clearance   ──► fill_region(..., block="air")      │
│  2. Foundation Layer ──► build_floor(..., "cobblestone")    │
│  3. Wall Perimeter   ──► build_wall(..., "oak_planks")      │
│  4. Door Openings    ──► build_door(...)                    │
│  5. Window Fixtures  ──► build_window(...)                  │
│  6. Pitched Roof     ──► build_roof(..., "oak_stairs")      │
│  7. Mob-Proofing     ──► place_blocks([torches...])         │
└──────────────────────────────┬──────────────────────────────┘
                               │ Batched Fabric World API (POST /api/world/blocks/place)
                               ▼
               Minecraft Java 26.2 (Fabric Server)
```

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_house_parameters",
  "type": "object",
  "properties": {
    "origin": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "South-West-Bottom corner [x, y, z] of the house foundation."
    },
    "width": {
      "type": "integer",
      "minimum": 5,
      "maximum": 25,
      "default": 9,
      "description": "Footprint width along the X axis (blocks)."
    },
    "depth": {
      "type": "integer",
      "minimum": 5,
      "maximum": 25,
      "default": 7,
      "description": "Footprint depth along the Z axis (blocks)."
    },
    "height": {
      "type": "integer",
      "minimum": 4,
      "maximum": 12,
      "default": 5,
      "description": "Wall height in blocks before roof slope."
    },
    "style": {
      "type": "string",
      "enum": ["oak_cabin", "stone_keep", "spruce_chalet", "desert_adobe", "modern_minimal"],
      "default": "oak_cabin",
      "description": "Preset architectural aesthetic and palette."
    },
    "materials_override": {
      "type": "object",
      "properties": {
        "foundation": {"type": "string"},
        "walls": {"type": "string"},
        "corners": {"type": "string"},
        "roof": {"type": "string"},
        "floor": {"type": "string"},
        "door": {"type": "string"},
        "windows": {"type": "string"}
      },
      "description": "Optional custom block overrides."
    },
    "features": {
      "type": "object",
      "properties": {
        "chimney": {"type": "boolean", "default": true},
        "overhang": {"type": "boolean", "default": true},
        "interior_lighting": {"type": "boolean", "default": true}
      }
    }
  },
  "required": ["origin"]
}
```

---

## 3. Composed Primitive Sequence

When `build_house` executes, it coordinates the following internal pipeline:

1. **Subterranean & Air Clearance**: Calls `fill_region(from, to, "minecraft:air")` to clear vegetation.
2. **Floor & Foundation**: Calls [`build_floor`](build_floor.md) with foundation material (e.g. `minecraft:cobblestone`).
3. **Pillars & Wall Framing**: Calls [`build_wall`](build_wall.md) for each perimeter side, inserting log columns at the four corners.
4. **Doorway Installation**: Calls [`build_door`](build_door.md) at the center of the front facade.
5. **Fenestration**: Calls [`build_window`](build_window.md) to puncture 2-pane glass windows on side walls.
6. **Roof Assembly**: Calls [`build_roof`](build_roof.md) using stair blocks facing inward to create an authentic A-frame gable.
7. **Interior Illumination**: Dispatches `place_blocks` with torches placed at height $y+3$ on interior walls.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "structure_type": "house",
  "style": "oak_cabin",
  "bounding_box": {
    "min": [100, 64, 200],
    "max": [108, 71, 206],
    "volume_blocks": 576
  },
  "blocks_placed": 342,
  "materials_used": {
    "minecraft:cobblestone": 63,
    "minecraft:oak_planks": 144,
    "minecraft:oak_log": 20,
    "minecraft:oak_stairs": 84,
    "minecraft:glass_pane": 8,
    "minecraft:oak_door": 1,
    "minecraft:torch": 4
  },
  "door_position": [104, 65, 200]
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_house",
  "arguments": {
    "origin": [120, 65, -180],
    "width": 9,
    "depth": 7,
    "height": 5,
    "style": "oak_cabin",
    "features": {
      "chimney": false,
      "interior_lighting": true
    }
  }
}
```

