# MCP Prompts Specification

Prompts in MCP 2.0 are user-selectable conversational templates. Unlike tools (which are invoked autonomously by the model), prompts are invoked by the user to bootstrap the LLM with structured role instructions, procedural constraints, and architectural workflow guidelines.

---

## 1. Prompt Catalog Overview

| Prompt Name | Description | Arguments |
| :--- | :--- | :--- |
| `architect_structure` | Architectural design and blueprint synthesis workflow | `structure_type`, `style`, `size`, `location` |
| `construct_structure` | End-to-end autonomous construction execution workflow | `blueprint_id`, `location` |
| `resume_construction` | Resumes interrupted or paused construction project | `project_id` |
| `repair_structure` | Structure discrepancy detection and automated repair | `project_id` |
| `establish_base` | Multi-structure settlement and compound planning workflow | `location`, `radius` |
| `explore_area` | Terrain surveying, resource discovery, and cartography | `center`, `radius` |

---

## 2. Detailed Prompt Specifications

### 2.1. `/architect_structure`

#### Arguments
- `structure_type` *(string)*: Architectural typology (`"tower"`, `"house"`, `"bridge"`, `"wall"`, `"castle"`, `"farm"`, `"temple"`, `"custom"`).
- `style` *(string, optional, default: "medieval_stone")*: Aesthetic theme (`"medieval_stone"`, `"timber_frame"`, `"desert_sandstone"`, `"modern_minimal"`, `"gothic"`).
- `size` *(string, optional, default: "medium")*: Structure scale (`"small"`, `"medium"`, `"large"`).
- `location` *(string | array, optional)*: Coordinates `[x, y, z]` or `"current_player_position"`.

#### Injected Prompt Instruction
```markdown
You are an autonomous Minecraft master architect agent.
Your objective is to design a high-fidelity architectural blueprint for a {structure_type} in {style} style.

### Operational Protocol:
1. **Spatial Survey**:
   - Query `minecraft://world/map` or inspect the site using `inspect_area`.
   - If location is unspecified, locate a suitable flat site using `find_build_location`.

2. **Blueprint Compilation**:
   - Synthesize a structured blueprint with ordered components:
     - Foundation & clearance envelope
     - Structural pillars and framing
     - Enclosing walls with fenestration (windows, doorways)
     - Roof / battlements / parapets
     - Interior lighting and functional stations
   - Save the plan to `minecraft://agent/plan`.

3. **Resource Bill-of-Materials**:
   - Calculate item counts via `check_requirements`.
   - Report material needs and craftable conversions to the user.
```

---

### 2.2. `/construct_structure`

#### Arguments
- `blueprint_id` *(string)*: Blueprint template ID or definition.
- `location` *(array)*: South-West-Bottom anchor `[x, y, z]`.
- `orientation` *(string, optional, default: "north")*: Facade orientation (`"north"`, `"south"`, `"east"`, `"west"`).

#### Injected Prompt Instruction
```markdown
You are an autonomous construction orchestrator agent.
Your mission is to execute the construction of blueprint {blueprint_id} at {location}.

### Execution Sequence:
1. **Resource Readiness**: Check player inventory against requirements with `check_requirements`.
2. **Construction Execution**: Call `build_structure` to build layer-by-layer.
3. **Progress Monitoring**: Monitor `minecraft://construction/current` state transitions.
4. **Verification**: Verify placed blocks against expected blueprint coordinates.
```

---

### 2.3. `/repair_structure`

#### Arguments
- `project_id` *(string, optional)*: Target construction project ID.

#### Injected Prompt Instruction
```markdown
You are an autonomous structural inspector and restoration specialist.
Your mission is to inspect the structure and repair any discrepancies.

### Protocol:
1. Inspect the structure with `repair_structure(project_id="{project_id}")`.
2. Identify missing, displaced, or destroyed blocks.
3. Re-verify structural integrity upon repair completion.
```

---

### 2.4. `/explore_area`

#### Arguments
- `center` *(array)*: Coordinate anchor `[x, y, z]`.
- `radius` *(integer, default: 16)*: Survey radius in blocks.

#### Injected Prompt Instruction
```markdown
You are an autonomous scout and cartographer agent.
Your mission is to survey the area around {center} with radius {radius}.
Update the spatial world model and record points of interest using `mark_location`.
```
