# High-Level Tool: `build_window`

The `build_window` tool carves aperture openings into existing wall sections, inserts glass blocks or thin glass panes, and optionally installs exterior window sills and trapdoor shutters.

---

## 1. Concept & Rationale

Glass panes add architectural depth and exterior illumination to structures. However, punching openings into existing walls without breaking neighboring blocks or roof supports requires accurate bounding calculations. `build_window` automates aperture cutting and glass insertion cleanly.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_window_parameters",
  "type": "object",
  "properties": {
    "position": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Bottom-left corner [x, y, z] of the window aperture."
    },
    "width": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4,
      "default": 2,
      "description": "Horizontal span of the window in blocks."
    },
    "height": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3,
      "default": 2,
      "description": "Vertical span of the window in blocks."
    },
    "axis": {
      "type": "string",
      "enum": ["x", "z"],
      "description": "Coordinate axis along which the wall runs."
    },
    "glass_type": {
      "type": "string",
      "default": "minecraft:glass_pane",
      "description": "Block type: glass pane, tinted glass, stained glass."
    },
    "sill_material": {
      "type": "string",
      "description": "Optional slab or inverted stair block for an exterior sill."
    },
    "shutters": {
      "type": "boolean",
      "default": false,
      "description": "Adds exterior wooden trapdoors flanking the window."
    }
  },
  "required": ["position", "axis"]
}
```

---

## 3. Composed Primitive Sequence

1. **Aperture Punching**: Calls `break_blocks` across the $W \times H$ volume.
2. **Glass Insertion**: Dispatches `place_blocks` filled with `glass_type`.
3. **Sill Attachment** *(if specified)*: Places inverted stairs underneath the window base.
4. **Shutter Placement** *(if enabled)*: Places open trapdoors along the exterior edges.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "glass_type": "minecraft:glass_pane",
  "panes_installed": 4,
  "aperture_bounds": {
    "from": [102, 66, 200],
    "to": [103, 67, 200]
  },
  "shutters_placed": 4
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_window",
  "arguments": {
    "position": [102, 66, 200],
    "width": 2,
    "height": 2,
    "axis": "x",
    "glass_type": "minecraft:glass_pane",
    "shutters": true
  }
}
```

