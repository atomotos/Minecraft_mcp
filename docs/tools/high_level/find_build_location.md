# High-Level Tool: `find_build_location`

The `find_build_location` tool performs spatial terrain intelligence across a designated radius. It evaluates ground topography, slope gradients, elevation variance, and hazard proximity to locate ideal, flat construction sites.

---

## 1. Concept & Rationale

Before building any structure, an autonomous agent needs to know *where* to place it. Placing a house on a cliff edge, underwater, or in dense jungle creates broken geometry. `find_build_location` runs a 2D/3D convolution filter over Minecraft heightmap data to find the smoothest, hazard-free parcel of land.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "find_build_location_parameters",
  "type": "object",
  "properties": {
    "search_center": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Center point [x, y, z] from which to radiate the search."
    },
    "search_radius": {
      "type": "integer",
      "minimum": 10,
      "maximum": 64,
      "default": 32,
      "description": "Search radius around center."
    },
    "width": {
      "type": "integer",
      "minimum": 5,
      "maximum": 30,
      "description": "Desired footprint width along X axis."
    },
    "depth": {
      "type": "integer",
      "minimum": 5,
      "maximum": 30,
      "description": "Desired footprint depth along Z axis."
    },
    "max_slope": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "default": 0.15,
      "description": "Maximum tolerated slope/gradient (0.0 = completely flat)."
    },
    "avoid_water": {
      "type": "boolean",
      "default": true,
      "description": "Exclude candidates with surface water or rivers."
    },
    "avoid_dense_forest": {
      "type": "boolean",
      "default": false,
      "description": "Penalize sites with heavy tree coverage to minimize deforestation."
    }
  },
  "required": ["search_center", "width", "depth"]
}
```

---

## 3. Evaluation Algorithm

1. **Heightmap Sampling**: Samples surface coordinates directly via `POST /api/world/inspect` (Fabric World API chunk heightmaps).
2. **Convolution Window**: Slides a bounding box of size $W \times D$ across the grid in 2-block strides.
3. **Fitness Scoring**:
   $$\text{Fitness} = w_1 \cdot (1 - \text{Slope}) + w_2 \cdot (1 - \Delta Y_{\text{variance}}) - w_3 \cdot \text{Hazards} - w_4 \cdot \text{Distance}$$
4. **Clearing Estimation**: Counts foliage blocks requiring excavation.

---

## 4. Return Value Schema

```json
{
  "best_location": [112, 65, 185],
  "fitness_score": 0.94,
  "topography": {
    "base_y": 65,
    "min_y": 64,
    "max_y": 65,
    "slope": 0.06,
    "surface_block": "minecraft:grass_block"
  },
  "clearing_cost": {
    "blocks_to_excavate": 4,
    "blocks_to_fill": 2,
    "trees_to_fell": 0
  },
  "alternative_candidates": [
    {
      "location": [94, 66, 220],
      "fitness_score": 0.88,
      "base_y": 66
    }
  ]
}
```

---

## 5. LLM Call Example

```json
{
  "name": "find_build_location",
  "arguments": {
    "search_center": [100, 64, 200],
    "search_radius": 30,
    "width": 11,
    "depth": 9,
    "max_slope": 0.12,
    "avoid_water": true
  }
}
```

