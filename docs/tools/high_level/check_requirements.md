# High-Level Tool: `check_requirements`

The `check_requirements` tool inspects a blueprint or architectural objective against the player's current inventory to determine material readiness, deficits, and crafting possibilities.

---

## 1. Architectural Concept

Before commencing construction, an autonomous agent must confirm whether it possesses the necessary materials. `check_requirements` compiles the bill-of-materials from the target blueprint, queries the player inventory via `get_inventory`, identifies shortages, and checks whether raw materials (such as logs) can be crafted into required components (planks, stairs, doors).

---

## 2. Parameter Schema

```json
{
  "name": "check_requirements",
  "description": "Calculate material requirements for a blueprint and compare against player inventory.",
  "parameters": {
    "type": "object",
    "properties": {
      "blueprint": {
        "description": "Blueprint definition or template name (e.g. 'watchtower', 'stone_bridge').",
        "type": "object"
      },
      "player_name": {
        "description": "Player inventory to inspect (defaults to active player).",
        "type": "string"
      }
    },
    "required": ["blueprint"]
  }
}
```

---

## 3. Return Value Schema

```json
{
  "sufficient": true,
  "required": {
    "minecraft:cobblestone": 240,
    "minecraft:oak_planks": 120,
    "minecraft:oak_log": 32,
    "minecraft:oak_stairs": 48
  },
  "available": {
    "minecraft:cobblestone": 300,
    "minecraft:oak_planks": 150,
    "minecraft:oak_log": 64,
    "minecraft:oak_stairs": 64
  },
  "missing": {},
  "can_craft_missing": true,
  "status": "SUFFICIENT"
}
```
