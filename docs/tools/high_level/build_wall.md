# High-Level Tool: `build_wall`

The `build_wall` tool constructs continuous linear or fortified barriers between two points or along a cardinal direction, with options for thickness, materials, and defensive battlements (crenellations).

---

## 1. Concept & Rationale

Building walls is one of the most common structural tasks for perimeter defense and enclosure. The `build_wall` tool calculates the 3D Bresenham or coordinate axis spans, automatically adjusts for terrain step changes, and optionally caps the structure with alternating crenellations and parapets.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_wall_parameters",
  "type": "object",
  "properties": {
    "start_pos": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Starting position [x, y, z] of the wall base."
    },
    "end_pos": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Optional explicit end position [x, y, z]. If omitted, length and direction are required."
    },
    "length": {
      "type": "integer",
      "minimum": 2,
      "maximum": 64,
      "description": "Length of the wall in blocks (used if end_pos is omitted)."
    },
    "direction": {
      "type": "string",
      "enum": ["north", "south", "east", "west"],
      "description": "Cardinal direction from start_pos (used if end_pos is omitted)."
    },
    "height": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "default": 4,
      "description": "Vertical height of the wall in blocks."
    },
    "thickness": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4,
      "default": 1,
      "description": "Wall thickness in blocks."
    },
    "material": {
      "type": "string",
      "default": "minecraft:stone_bricks",
      "description": "Block identifier for the main wall body."
    },
    "crenellations": {
      "type": "boolean",
      "default": false,
      "description": "Add alternating 1-block battlements and gaps along the top layer."
    },
    "walkway": {
      "type": "boolean",
      "default": false,
      "description": "Adds a 1-block inner walkway with slabs and guardrails."
    }
  },
  "required": ["start_pos"]
}
```

---

## 3. Composed Primitive Sequence

1. **Vector & Coordinate Calculation**: Computes cuboid coordinates $(x_1, y_1, z_1)$ to $(x_2, y_2, z_2)$.
2. **Main Body Placement**: Invokes `fill_region(from_pos, to_pos, block=material)`.
3. **Crenellation Pass** *(if enabled)*: Generates a list of top-layer coordinates at $y = y_{\text{top}} + 1$ with alternating blocks and dispatches via `place_blocks`.
4. **Walkway Placement** *(if enabled)*: Attaches interior wooden/stone slabs along the inner face.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "start_pos": [100, 64, 200],
  "end_pos": [115, 67, 200],
  "length": 16,
  "height": 4,
  "thickness": 1,
  "material": "minecraft:stone_bricks",
  "blocks_placed": 72,
  "crenellations_count": 8
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_wall",
  "arguments": {
    "start_pos": [100, 64, 200],
    "direction": "east",
    "length": 15,
    "height": 4,
    "material": "minecraft:stone_bricks",
    "crenellations": true
  }
}
```

