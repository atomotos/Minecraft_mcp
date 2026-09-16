# High-Level Tool: `navigate_to`

The `navigate_to` tool implements autonomous path planning and movement orchestration. It navigates across uneven terrain, climbs natural 1-block steps, swims through water bodies, and steers around obstacles and hazards without micromanagement from the LLM.

---

## 1. Concept & Rationale

Minecraft movement is treacherous: cliffs cause fall damage, lava is lethal, and 1-block elevation changes require synchronized jump-stepping. Rather than asking the LLM to output individual WASD commands, `navigate_to` executes a local 3D A* path planner on the server and feeds step-wise updates to the Minecraft engine.

```
LLM: "Go to coordinates [140, 65, -210]"
  │
  ▼
navigate_to()
  │
  ├─► Local 3D A* Path Planner (Obstacles, Jump Checks, Water/Lava avoidance)
  ├─► Node Sequence: [N0 -> N1 -> N2 -> ... -> N_dest]
  └─► Execution Loop:
        look_at(N_i) ──► move_to(N_i) ──► jump() if climbing ──► verify
```

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "navigate_to_parameters",
  "type": "object",
  "properties": {
    "destination": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Target destination coordinates [x, y, z]."
    },
    "tolerance": {
      "type": "number",
      "minimum": 0.5,
      "maximum": 5.0,
      "default": 1.5,
      "description": "Acceptable arrival radius around destination in blocks."
    },
    "speed": {
      "type": "string",
      "enum": ["walk", "sprint", "sneak"],
      "default": "sprint",
      "description": "Movement pace."
    },
    "avoid_hazards": {
      "type": "boolean",
      "default": true,
      "description": "Strictly route around lava, fire, cactus, and sweet berry bushes."
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 5,
      "maximum": 120,
      "default": 30,
      "description": "Maximum time allowed to reach destination."
    }
  },
  "required": ["destination"]
}
```

---

## 3. Pathfinding Execution Loop

1. **A\* Waypoint Generation**: Computes a series of valid walking/jumping nodes from current position to `destination`.
2. **Terrain Stepping**:
   - Flat surface: Straight sprint.
   - 1-block elevation increase: Triggers `jump()` precisely 0.5 blocks before collision.
   - Water: Surfaces periodically to prevent drowning.
3. **Stuck Detection**: If progress halts for > 2.0 seconds, recalculates path around dynamic obstacle (e.g., mob or placed block).
4. **Completion Check**: Once Euclidean distance $\le \text{tolerance}$, invokes `stop()` and reports arrival.

---

## 4. Return Value Schema

```json
{
  "status": "reached",
  "success": true,
  "final_position": [140.2, 65.0, -209.8],
  "distance_traversed": 46.8,
  "duration_seconds": 9.4,
  "nodes_completed": 32,
  "hazards_avoided": 1
}
```

---

## 5. LLM Call Example

```json
{
  "name": "navigate_to",
  "arguments": {
    "destination": [140.0, 65.0, -210.0],
    "speed": "sprint",
    "tolerance": 1.5,
    "avoid_hazards": true
  }
}
```

