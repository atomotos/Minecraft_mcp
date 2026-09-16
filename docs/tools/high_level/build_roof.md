# High-Level Tool: `build_roof`

The `build_roof` tool constructs realistic architectural roofs over rectangular footprints, handling block orientations (stairs, slabs, half-blocks) and geometric pitch progression.

---

## 1. Concept & Rationale

Hand-crafting roofs in Minecraft requires precise stair block orientation states (`facing=north`, `half=bottom`, `shape=straight`, etc.) and symmetrical step increases. `build_roof` abstracts this complex mathematics into high-level geometric styles.

### Supported Roof Geometries

1. **Pitched (Gable)**: Traditional A-frame sloping inward along the narrower axis, ending in a central ridge.
2. **Hip**: Four-sided pyramid slope meeting at a central point or short ridge line.
3. **Flat**: Solid flat slab roof surrounded by an aesthetic 1-block parapet.
4. **Dome / Barrel Vault**: Curved arch geometry for halls and sanctuaries.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "build_roof_parameters",
  "type": "object",
  "properties": {
    "origin": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Base corner [x, y, z] of the roof layer (top of perimeter walls)."
    },
    "width": {
      "type": "integer",
      "minimum": 3,
      "maximum": 30,
      "description": "Footprint width along X axis."
    },
    "depth": {
      "type": "integer",
      "minimum": 3,
      "maximum": 30,
      "description": "Footprint depth along Z axis."
    },
    "style": {
      "type": "string",
      "enum": ["pitched", "hip", "flat", "dome"],
      "default": "pitched",
      "description": "Architectural roof type."
    },
    "stair_material": {
      "type": "string",
      "default": "minecraft:oak_stairs",
      "description": "Stair block type for slopes."
    },
    "slab_material": {
      "type": "string",
      "default": "minecraft:oak_slab",
      "description": "Slab block type for ridge capping."
    },
    "overhang": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "default": 1,
      "description": "Blocks extending past the wall perimeter."
    }
  },
  "required": ["origin", "width", "depth"]
}
```

---

## 3. Composed Primitive Sequence

1. **Eaves Expansion**: Calculates outer footprint with `overhang` offset.
2. **Layer Step Generation**:
   - For each vertical step $\Delta y$, places stairs with inward `facing` states along the active slope axes.
   - Places solid plank or log gables on end walls to fill open triangles.
3. **Ridge Capping**: At the apex, places a continuous line of `slab_material`.
4. **Batch Execution**: Bundles all generated blocks into an optimized `place_blocks` invocation.

---

## 4. Return Value Schema

```json
{
  "success": true,
  "style": "pitched",
  "blocks_placed": 118,
  "ridge_height_y": 70,
  "eaves_bounds": {
    "min": [99, 69, 199],
    "max": [109, 73, 207]
  }
}
```

---

## 5. LLM Call Example

```json
{
  "name": "build_roof",
  "arguments": {
    "origin": [100, 69, 200],
    "width": 9,
    "depth": 7,
    "style": "pitched",
    "stair_material": "minecraft:deepslate_tile_stairs",
    "slab_material": "minecraft:deepslate_tile_slab",
    "overhang": 1
  }
}
```

