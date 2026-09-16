# High-Level Tool: `build_floor`

The `build_floor` tool levels terrain and constructs single- or multi-material floor slabs across a rectangular region. It supports decorative border patterns and checkered tiling.

---

## 1. Concept & Rationale

Floors must not only place top-surface blocks but also fill empty cavities underneath (subfloor stabilization) so the structure does not float over uneven terrain, ravines, or ponds. `build_floor` handles leveling and floor aesthetics simultaneously.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_floor_parameters",
  "type": "object",
  "properties": {
    "from_pos": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "First corner coordinate [x1, y1, z1]."
    },
    "to_pos": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Opposite corner coordinate [x2, y1, z2] (Y is aligned)."
    },
    "material": {
      "type": "string",
      "default": "minecraft:oak_planks",
      "description": "Primary flooring material."
    },
    "pattern": {
      "type": "string",
      "enum": ["solid", "checkered", "border"],
      "default": "solid",
      "description": "Decorative floor pattern."
    },
    "secondary_material": {
      "type": "string",
      "description": "Secondary material required for 'checkered' or 'border' patterns."
    },
    "foundation_depth": {
      "type": "integer",
      "minimum": 0,
      "maximum": 5,
      "default": 1,
      "description": "Number of subterranean layers to fill underneath to secure uneven terrain."
    }
  },
  "required": ["from_pos", "to_pos"]
}
```

---

## 3. Composed Primitive Sequence

1. **Subfloor Bedding**: If `foundation_depth > 0`, calls `fill_region(from_y - foundation_depth, to_y - 1, block="minecraft:cobblestone")` to eliminate air pockets.
2. **Surface Generation**:
   - **Solid**: Dispatches a single `fill_region` call.
   - **Border**: Calls `fill_region` for outer perimeter with `secondary_material`, and inner region with `material`.
   - **Checkered**: Synthesizes a coordinate map where $(x + z) \pmod 2 == 0 \implies \text{material}$, else $\text{secondary\_material}$, dispatched via `place_blocks`.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "area_square_blocks": 63,
  "dimensions": {"width": 9, "depth": 7},
  "total_blocks_placed": 126,
  "subfloor_fill_layers": 1,
  "primary_material": "minecraft:spruce_planks",
  "secondary_material": "minecraft:dark_oak_planks"
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_floor",
  "arguments": {
    "from_pos": [100, 64, 200],
    "to_pos": [108, 64, 206],
    "material": "minecraft:spruce_planks",
    "pattern": "border",
    "secondary_material": "minecraft:dark_oak_planks",
    "foundation_depth": 1
  }
}
```

