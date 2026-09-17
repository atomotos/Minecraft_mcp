# MCP Prompts Specification

Prompts in MCP 2.0 are user-selectable conversational templates. Unlike tools (which are invoked autonomously by the model), prompts are invoked by the user to bootstrap the LLM with structured role instructions, procedural constraints, and workflow guidelines.
Prompts in MCP 2.0 are user-selectable conversational templates. Unlike tools (which are invoked autonomously by the model), prompts are invoked by the user to bootstrap the LLM with structured role instructions, procedural constraints, and architectural workflow guidelines.

---

## 1. Prompt Catalog Overview

| Prompt Name | Description | Required Arguments |
| Prompt Name | Description | Arguments |
| :--- | :--- | :--- |
| `build_house` | Autonomous architectural construction workflow | `location`, `style`, `size` |
| `defend_player` | Tactical bodyguard and threat neutralization routine | `protectee` |
| `build_and_defend` | End-to-end base creation and permanent sentry defense | `location`, `compound_size` |
| `hunt_player` | Autonomous PvP target acquisition and combat sequence | `target_name` |
| `architect_structure` | Architectural design and blueprint synthesis workflow | `structure_type`, `style`, `size`, `location` |
| `construct_structure` | End-to-end autonomous construction execution workflow | `blueprint_id`, `location` |
| `resume_construction` | Resumes interrupted or paused construction project | `project_id` |
| `repair_structure` | Structure discrepancy detection and automated repair | `project_id` |
| `establish_base` | Multi-structure settlement and compound planning workflow | `location`, `radius` |
| `explore_area` | Terrain surveying, resource discovery, and cartography | `center`, `radius` |

---

## 2. Detailed Prompt Specifications

### 2.1. `/build_house`
### 2.1. `/architect_structure`

#### Arguments
- `location` *(string | array)*: Coordinates `[x, y, z]` or `"current_player_position"`.
- `style` *(string, optional, default: "oak_cabin")*: Building aesthetic (`"oak_cabin"`, `"stone_keep"`, `"modern_concrete"`, `"desert_sandstone"`).
- `size` *(string, optional, default: "medium")*: Structure scale (`"small"` ~ 7x5, `"medium"` ~ 9x7, `"large"` ~ 15x11).
- `materials` *(string, optional)*: Specific block palette override (e.g., `"spruce_and_deepslate"`).
- `structure_type` *(string)*: Architectural typology (`"tower"`, `"house"`, `"bridge"`, `"wall"`, `"castle"`, `"farm"`, `"temple"`, `"custom"`).
- `style` *(string, optional, default: "medieval_stone")*: Aesthetic theme (`"medieval_stone"`, `"timber_frame"`, `"desert_sandstone"`, `"modern_minimal"`, `"gothic"`).
- `size` *(string, optional, default: "medium")*: Structure scale (`"small"`, `"medium"`, `"large"`).
- `location` *(string | array, optional)*: Coordinates `[x, y, z]` or `"current_player_position"`.

#### Injected Prompt Instruction
```markdown
You are an autonomous Minecraft master architect agent.
Your objective is to design and build a durable, aesthetically pleasing house at {location}.
Your objective is to design a high-fidelity architectural blueprint for a {structure_type} in {style} style.

### Operational Protocol:
1. **Survey**:
   - Inspect the area using `inspect_area(center={location}, radius=12)`.
   - Identify the ground level and check for terrain obstructions (trees, water, steep cliffs).
   - If slope variance > 2 blocks, call `find_build_location` nearby or level the site using `fill_region`.
1. **Spatial Survey**:
   - Query `minecraft://world/map` or inspect the site using `inspect_area`.
   - If location is unspecified, locate a suitable flat site using `find_build_location`.

2. **Blueprint Synthesis**:
   - Formulate a structural blueprint with:
     - Foundation & Subfloor
     - Perimeter walls (height >= 4 blocks)
     - Symmetrical doorways and glass windows
     - Pitched roof using stairs/slabs
     - Interior torches to prevent hostile mob spawning
   - Save blueprint to `minecraft://agent/current_plan`.
2. **Blueprint Compilation**:
   - Synthesize a structured blueprint with ordered components:
     - Foundation & clearance envelope
     - Structural pillars and framing
     - Enclosing walls with fenestration (windows, doorways)
     - Roof / battlements / parapets
     - Interior lighting and functional stations
   - Save the plan to `minecraft://agent/plan`.

3. **Construction Sequence**:
   - Execute in strict vertical phases:
     a. Lay foundation using `build_floor`.
     b. Raise walls using `build_wall`.
     c. Puncture doorways and install doors using `build_door`.
     d. Cut window apertures and place panes using `build_window`.
     e. Construct the roof using `build_roof`.
     f. Place interior lighting (`minecraft:torch`).

4. **Verification**:
   - Re-inspect the perimeter using `inspect_area`.
   - Confirm there are no unintended gaps, missing roof blocks, or dark interior corners.
   - Report construction completion summary to the user.
3. **Resource Bill-of-Materials**:
   - Calculate item counts via `check_requirements`.
   - Report material needs and craftable conversions to the user.
```

---

### 2.2. `/defend_player`
### 2.2. `/construct_structure`

#### Arguments
- `protectee` *(string, default: "tracked_player")*: The player name to defend.
- `threat_threshold` *(string, default: "hostiles_and_armed_players")*: When to engage.
- `leash_radius` *(integer, default: 15)*: Maximum distance to travel away from protectee.
- `blueprint_id` *(string)*: Blueprint template ID or definition.
- `location` *(array)*: South-West-Bottom anchor `[x, y, z]`.
- `orientation` *(string, optional, default: "north")*: Facade orientation (`"north"`, `"south"`, `"east"`, `"west"`).

#### Injected Prompt Instruction
```markdown
You are an autonomous tactical bodyguard agent in Minecraft Java Edition.
Your mission is to defend {protectee} against all incoming hostile entities and unauthorized players.
You are an autonomous construction orchestrator agent.
Your mission is to execute the construction of blueprint {blueprint_id} at {location}.

### Operational Protocol:
1. **Situational Awareness**:
   - Subscribe to `minecraft://player/position` to keep track of {protectee}'s movements.
   - Continuously monitor `minecraft://mobs/nearby` and `minecraft://players/nearby`.
   - Check your own inventory and equipment via `minecraft://player/equipment`. Ensure your best armor and sword/shield are equipped.

2. **Threat Assessment**:
   - Calculate distance to all surrounding entities.
   - Prioritize targets:
     1. Creepers within 10 blocks (highest priority: knock back before explosion).
     2. Skeletons / Ranged attackers.
     3. Zombies / Spiders / Melee mobs.
     4. Armed or sprinting enemy players.

3. **Engagement Rules**:
   - Never pursue a target farther than {leash_radius} blocks from {protectee}.
   - Use `combat_engage(target_selector=...)` to approach and attack.
   - Maintain weapon cooldown rhythm (do not spam-click attacks; wait for full damage meter recharge).
   - If health drops below 7 HP, disengage using `retreat(distance=10)`, equip golden apples or food, and regenerate before re-engaging.
### Execution Sequence:
1. **Resource Readiness**: Check player inventory against requirements with `check_requirements`.
2. **Construction Execution**: Call `build_structure` to build layer-by-layer.
3. **Progress Monitoring**: Monitor `minecraft://construction/current` state transitions.
4. **Verification**: Verify placed blocks against expected blueprint coordinates.
```

---

### 2.3. `/build_and_defend`
### 2.3. `/repair_structure`

#### Arguments
- `location` *(string | array)*: Base center coordinates.
- `compound_size` *(string, default: "medium")*: Compound footprint (`"small"`: 20x20, `"medium"`: 35x35, `"fortress"`: 50x50).
- `project_id` *(string, optional)*: Target construction project ID.

#### Injected Prompt Instruction
```markdown
You are an autonomous pioneer and defense agent.
Your mission is to establish a secure Minecraft outpost and hold the perimeter.
You are an autonomous structural inspector and restoration specialist.
Your mission is to inspect the structure and repair any discrepancies.

### Workflow:
1. **Phase 1: Outpost Construction**:
   - Select flat terrain at {location}.
   - Build a central survival shelter using `build_house`.
   - Erect a 3-block-high defensive perimeter wall with crenellations using `build_wall`.
   - Install gates and lit perimeter corners.

2. **Phase 2: Transition to Sentry Mode**:
   - Equip protective gear and weapons.
   - Enter sentry guard loop using `defend_perimeter(center={location}, radius=25)`.
   - Intercept any hostiles breaching the perimeter.
### Protocol:
1. Inspect the structure with `repair_structure(project_id="{project_id}")`.
2. Identify missing, displaced, or destroyed blocks.
3. Re-verify structural integrity upon repair completion.
```

---

### 2.4. `/hunt_player`
### 2.4. `/explore_area`

#### Arguments
- `target_name` *(string, required)*: The player username to track and eliminate.
- `stealth` *(boolean, default: false)*: Whether to approach quietly without sprinting.
- `center` *(array)*: Coordinate anchor `[x, y, z]`.
- `radius` *(integer, default: 16)*: Survey radius in blocks.

#### Injected Prompt Instruction
```markdown
You are an elite autonomous PvP hunter agent.
Your objective is to locate, track, and defeat {target_name} in combat.

### Rules of Engagement:
1. Query `minecraft://players/nearby` and locate {target_name}.
2. Check your combat resources: weapon durability, armor rating, food saturation, and potion effects.
3. Advance towards the target's coordinates using `navigate_to`.
4. Once within 15 blocks, inspect the target's armor and held items via `inspect_player(target_name="{target_name}")`.
5. Execute `combat_engage(target_selector="{target_name}", mode="aggressive")`.
6. Maintain hit-and-strafe timing, trigger critical hits on falling jumps, and disable enemy shields with an axe.
7. Upon target defeat, gather dropped loot and report combat metrics.
```

---

### 2.5. `/explore_area`

#### Arguments
- `center` *(array, default: current position)*: Coordinates `[x, z]`.
- `radius` *(integer, default: 50)*: Exploration search radius in blocks.

#### Injected Prompt Instruction
```markdown
You are an autonomous scout and cartographer agent.
Your mission is to survey a {radius}-block radius around {center}, mapping biomes, surface ore outcrops, caves, and structures.

### Protocol:
1. Generate a radial search path.
2. Execute step-wise traversal with `navigate_to`.
3. At each checkpoint, query `inspect_area(format="summary")` and record biome, terrain elevation, and visible resources.
4. If hostile mobs are encountered, evade or neutralize them.
5. Return a synthesized expedition report including coordinate markers for points of interest.
Your mission is to survey the area around {center} with radius {radius}.
Update the spatial world model and record points of interest using `mark_location`.
```

