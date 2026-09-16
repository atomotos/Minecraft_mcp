# High-Level Tool: `build_door`

The `build_door` tool carves a doorway through a wall, installs single or double wooden/iron doors with valid Minecraft 2-block state properties, and optionally places lintel framing and interior pressure plates.

---

## 1. Concept & Rationale

In Minecraft, doors consist of two linked block states: `half=lower` and `half=upper`. Manually placing these states via raw commands often results in half-doors, missing textures, or broken physics. `build_door` automates the cutout, pair synchronization, and state alignment.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_door_parameters",
  "type": "object",
  "properties": {
    "position": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Base block coordinate [x, y, z] of the door threshold."
    },
    "facing": {
      "type": "string",
      "enum": ["north", "south", "east", "west"],
      "description": "Direction the door faces when closed."
    },
    "door_type": {
      "type": "string",
      "default": "minecraft:oak_door",
      "description": "Door block ID."
    },
    "double_door": {
      "type": "boolean",
      "default": false,
      "description": "Places two mirrored adjacent doors."
    },
    "frame_material": {
      "type": "string",
      "description": "Optional block type for surrounding jamb and lintel."
    },
    "interior_pressure_plate": {
      "type": "boolean",
      "default": true,
      "description": "Places a pressure plate on the interior side for automated exit."
    }
  },
  "required": ["position", "facing"]
}
```

---

## 3. Composed Primitive Sequence

1. **Aperture Clearance**: Calls `break_blocks` for the $1 \times 2$ (or $2 \times 2$) doorway cavity.
2. **Door Half Placement**:
   - Bottom block: `place_block(x, y, z, "{door_type}[facing={facing},half=lower,hinge=left]")`
   - Top block: `place_block(x, y+1, z, "{door_type}[facing={facing},half=upper,hinge=left]")`
3. **Double Door Mirroring** *(if enabled)*: Places the right door with `hinge=right`.
4. **Convenience Plates**: If enabled, places an `oak_pressure_plate` on the inner side block.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "door_type": "minecraft:oak_door",
  "position": [104, 65, 200],
  "facing": "north",
  "double_door": false,
  "blocks_modified": 3
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_door",
  "arguments": {
    "position": [104, 65, 200],
    "facing": "north",
    "door_type": "minecraft:spruce_door",
    "double_door": true,
    "interior_pressure_plate": true
  }
}
```

