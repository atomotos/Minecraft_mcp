# High-Level Tool: `repair_structure`

The `repair_structure` tool provides closed-loop discrepancy detection and autonomous repair for active or completed construction projects.

---

## 1. Architectural Concept

During or after construction, external factors (creeper explosions, water flow, falling gravel, player mining) can damage structures. `repair_structure` inspects the physical world at all coordinates associated with the project's construction plan, identifies missing or corrupted blocks, generates an isolated repair patch, and applies it through Phase 2 batch primitives.

```
Expected Voxel Grid (Construction Plan)
                   vs.
Actual World State (Fabric get_blocks inspection)
                   │
                   ▼
       Discrepancy Identification
    (Missing blocks, corrupted states)
                   │
                   ▼
         Targeted Patch Dispatch
          (place_blocks / break)
                   │
                   ▼
            Re-Verification
```

---

## 2. Parameter Schema

```json
{
  "name": "repair_structure",
  "description": "Inspect an existing construction project, detect missing or corrupted blocks, and autonomously restore structural integrity.",
  "parameters": {
    "type": "object",
    "properties": {
      "project_id": {
        "description": "Unique identifier of the construction project to inspect and repair. If omitted, targets the most recent active or completed project.",
        "type": "string"
      }
    }
  }
}
```

---

## 3. Return Value Schema

```json
{
  "success": true,
  "project_id": "proj_watchtower_1726531200",
  "total_checked": 482,
  "missing_blocks_found": 3,
  "blocks_repaired": 3,
  "failed_repairs": 0,
  "verified": true,
  "status": "COMPLETED"
}
```

