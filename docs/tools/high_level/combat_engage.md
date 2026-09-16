# High-Level Tool: `combat_engage`

The `combat_engage` tool runs an autonomous tactical combat sequence against a designated player or hostile mob. It manages weapon cooldowns, defensive shielding, circle strafing, and health-based emergency retreats.

---

## 1. Concept & Rationale

Effective Minecraft PvP/PvE cannot be achieved by firing single attack commands randomly. In Java Edition:
- Attacks have a recharge delay (1.6 attack speed for diamond swords = 0.625s cooldown); spamming attacks deals only 20% damage.
- Opponent shields must be disabled using axes.
- Critical hits occur when striking while falling down from a jump.
- Health drops below critical levels require immediate disengagement and food/potion consumption.

`combat_engage` encapsulates this entire real-time combat state machine.

---

## 2. Parameter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "combat_engage_parameters",
  "type": "object",
  "properties": {
    "target_selector": {
      "type": "string",
      "description": "Target entity name, UUID, or selector (e.g., 'Alex', '@e[type=skeleton,sort=nearest,limit=1]')."
    },
    "mode": {
      "type": "string",
      "enum": ["aggressive", "defensive", "skirmish"],
      "default": "aggressive",
      "description": "Aggressive = relentless melee; Defensive = shield-focused counterattacks; Skirmish = hit-and-run."
    },
    "weapon_preference": {
      "type": "string",
      "enum": ["best_sword", "best_axe", "ranged_bow", "auto"],
      "default": "auto",
      "description": "Preferred weapon selection from inventory."
    },
    "retreat_health_threshold": {
      "type": "number",
      "minimum": 2.0,
      "maximum": 14.0,
      "default": 6.0,
      "description": "Health (HP) level at which the agent aborts and retreats to safety."
    },
    "max_duration_seconds": {
      "type": "integer",
      "minimum": 5,
      "maximum": 60,
      "default": 20,
      "description": "Combat engagement timeout."
    }
  },
  "required": ["target_selector"]
}
```

---

## 3. Tactical Sequence Execution

1. **Pre-Combat Equipment Prep**:
   - Equips strongest armor from inventory.
   - Equips weapon in mainhand and shield in offhand.
2. **Approach & Interception**:
   - Tracks target location using [`navigate_to`](navigate_to.md).
   - Locks head orientation using `look_at`.
3. **Engagement Loop (Ticks @ 20Hz)**:
   - When distance $\le 3.5$ blocks:
     - Check attack meter. If 100% recharged: strike with `attack_entity`.
     - Jump-strike timing to trigger critical damage.
   - If target is blocking with shield: switch to axe to disable shield for 5 seconds.
   - Strafe left/right to evade incoming arrows or counterattacks.
4. **Health Threshold Check**:
   - If agent health $\le \text{retreat\_health\_threshold}$:
     - Calls `retreat(distance=15.0)`.
     - Equips golden apple or cooked food and triggers `use_item()`.
     - Returns status `"retreated"`.
5. **Victory Condition**:
   - Target despawns or health hits 0 $\rightarrow$ status `"target_defeated"`.

---

## 4. Return Value Schema

```json
{
  "status": "target_defeated",
  "target": "Alex",
  "success": true,
  "duration_seconds": 8.2,
  "hits_landed": 5,
  "critical_hits": 2,
  "damage_dealt": 28.5,
  "damage_taken": 6.0,
  "agent_final_health": 14.0,
  "loot_available": true
}
```

---

## 5. LLM Call Example

```json
{
  "name": "combat_engage",
  "arguments": {
    "target_selector": "Alex",
    "mode": "aggressive",
    "weapon_preference": "best_sword",
    "retreat_health_threshold": 6.0,
    "max_duration_seconds": 25
  }
}
```

