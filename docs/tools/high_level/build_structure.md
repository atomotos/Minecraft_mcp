# High-Level Tool: `build_structure`

The `build_structure` tool is the premier generic architectural constructor in the Minecraft MCP 2.0 Server. It compiles and constructs any structured architectural blueprint (towers, bridges, walls, houses, castles, farms, temples, monuments, or custom designs) across layered stages, delegating atomic block placements to Phase 2 primitives.

---

## 1. Architectural Concept

Rather than hard-coding structures or expecting the LLM to emit hundreds of low-level commands, `build_structure` accepts a structured blueprint definition (or blueprint ID referencing a template), validates bounds and safety limits, sequences components from foundation to roof, checks resources, and constructs the structure while updating progress.

```
LLM Agent
   │
   ▼ calls `build_structure(blueprint, location, orientation, materials_override)`
┌─────────────────────────────────────────────────────────────┐
│                    Blueprint Compiler                       │
│                                                             │
│  1. Bounds & Envelope Clearance                             │
│  2. Foundation / Ground Layer                               │
│  3. Structural Framing & Pillars                            │
│  4. Enclosing Walls & Openings                              │
│  5. Roof / Battlements / Slabs                              │
│  6. Interior Fixtures & Illumination                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Batched Phase 2 Operations (<= 500 blocks/batch)
                               ▼
                Minecraft Java 26.2 (Fabric Server)
```

---

## 2. Parameter Schema

```json
{
  "name": "build_structure",
  "description": "Construct an architectural structure from a blueprint or template at the specified location.",
  "parameters": {
    "type": "object",
    "properties": {
      "blueprint": {
        "description": "Blueprint definition object or pre-registered template name (e.g. 'watchtower', 'stone_bridge', 'oak_cabin', 'curtain_wall', 'wheat_farm').",
        "type": "object"
      },
      "location": {
        "description": "Anchor [x, y, z] coordinate array for the South-West-Bottom corner of the structure.",
        "type": "array",
        "items": {"type": "integer"},
        "minItems": 3,
        "maxItems": 3
      },
      "orientation": {
        "description": "Facing direction for the structure entrance/front ('north', 'south', 'east', 'west'). Defaults to 'north'.",
        "type": "string",
        "enum": ["north", "south", "east", "west"],
        "default": "north"
      },
      "materials_override": {
        "description": "Optional mapping of semantic palette roles to specific block states (e.g. {'wall': 'minecraft:deepslate_bricks'}).",
        "type": "object"
      },
      "clear_envelope": {
        "description": "Whether to clear vegetation and obstacles in the bounding box airspace before building.",
        "type": "boolean",
        "default": true
      }
    },
    "required": ["blueprint", "location"]
  }
}
```

---

## 3. Return Value Schema

```json
{
  "success": true,
  "project_id": "proj_watchtower_1726531200",
  "structure_type": "tower",
  "bounds": {
    "min": {"x": -240, "y": 64, "z": 140},
    "max": {"x": -234, "y": 80, "z": 146}
  },
  "planned_blocks": 482,
  "placed_blocks": 482,
  "failed_blocks": 0,
  "verified": true,
  "status": "COMPLETED"
}
```

