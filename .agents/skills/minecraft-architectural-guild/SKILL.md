---
name: minecraft-architectural-guild
description: >-
  Orchestrates the autonomous multi-agent architectural construction guild in Minecraft Java Edition.
  Use this skill when constructing monuments, temples, cathedrals, castles, or large-scale architecture
  by dispatching specialized subagents (Site Surveyor, Structural Mason, Artisan Carver, and QA Inspector).
---

# Minecraft Architectural Guild Orchestration Skill

This skill guides the Lead Architect (primary agent) in orchestrating specialized subagents within the Antigravity agenting platform to construct complex monumental architecture.

## The Architectural Guild Roles

1. **Lead Architect / Contractor** (Primary Agent):
   - Formulates the master build strategy, initializes the shared blackboard, and manages the subagent lifecycle.
2. **Site Surveyor & Ground Engineer** (`site_surveyor`):
   - Probes topography, levels the foundation datum $Y_{base}$, and anchors fill columns down to solid bedrock/dirt.
3. **Structural Mason & Geometry Builder** (`structural_mason`):
   - Compiles load-bearing geometry (colonnades, arches, vaults, domes) via procedural ASTs and 3D greedy cuboid meshing.
4. **Artisan Carver & Interior Specialist** (`artisan_carver`):
   - Carves architectural millwork, stained glass traceries, cornices, balustrades, lanterns, and interior furnishings.
5. **QA Inspector & Structural Verifier** (`qa_inspector`):
   - Audits physical blocks against the Geometry IR spec, runs automated repair for any defects, and issues final certification.

---

## Multi-Agent Execution Protocol

### Step 1: Project Initialization & Blackboard Setup
1. Query available architectural templates:
   Read resource `minecraft://geometry/templates`.
2. Initialize the project on the blackboard:
   Call `update_blackboard(key="monument_name", value="<monument_name>")`
   Call `update_blackboard(key="anchor", value=[<x>, <y>, <z>])`

### Step 2: Phase 1 — Site Surveyor & Ground Anchoring
1. Invoke the `site_surveyor` subagent via `invoke_subagent`:
   ```json
   {
     "TypeName": "self",
     "Role": "Site Surveyor & Geotechnical Engineer",
     "Prompt": "Survey terrain around anchor coordinates [...]. Determine base datum Y_base, clear obstruction envelope, and anchor sub-foundation columns down to solid ground using TerrainAdaptiveFoundationEngine. Post surveyed footprint and datum Y_base to minecraft://orchestration/blackboard."
   }
   ```
2. Await completion notification. Verify surveyed footprint on `minecraft://orchestration/blackboard`.
3. Update milestone: `record_progress_milestone(phase="SURVEY_FOUNDATION", progress_pct=100.0, status="COMPLETED")`.

### Step 3: Phase 2 — Structural Mason & Procedural Shell
1. Claim spatial zone for the superstructure:
   Call `assign_spatial_zone(agent_id="mason_01", min_coord=[...], max_coord=[...], zone_name="Superstructure Shell")`.
2. Invoke the `structural_mason` subagent via `invoke_subagent`:
   ```json
   {
     "TypeName": "self",
     "Role": "Structural Mason & Geometry Builder",
     "Prompt": "Read site datum Y_base and surveyed bounds from minecraft://orchestration/blackboard. Compile and construct the heavy structural shell for '<monument_template>' using compile_and_build() with greedy cuboid meshing. Verify structural integrity and report completion."
   }
   ```
3. Await completion notification. Release spatial zone via `release_spatial_zone(agent_id="mason_01")`.
4. Update milestone: `record_progress_milestone(phase="STRUCTURAL_SHELL", progress_pct=100.0, status="COMPLETED")`.

### Step 4: Phase 3 — Artisan Carver & Interior Detailing
1. Claim spatial detailing zones:
   Call `assign_spatial_zone(agent_id="artisan_01", min_coord=[...], max_coord=[...], zone_name="Ornamental Detailing")`.
2. Invoke the `artisan_carver` subagent via `invoke_subagent`:
   ```json
   {
     "TypeName": "self",
     "Role": "Artisan Carver & Interior Specialist",
     "Prompt": "Read structural bounds from blackboard. Carve window traceries, place cornices, balustrades, and battlements. Install lanterns and torches for full illumination. Add floor tiling and portal doors. Release zone when finished."
   }
   ```
3. Await completion notification. Update milestone: `record_progress_milestone(phase="ARCHITECTURAL_DETAILING", progress_pct=100.0, status="COMPLETED")`.

### Step 5: Phase 4 — QA Inspector & Structural Certification
1. Invoke the `qa_inspector` subagent via `invoke_subagent`:
   ```json
   {
     "TypeName": "self",
     "Role": "QA Inspector & Structural Verifier",
     "Prompt": "Perform closed-loop physical verification via verify_structure_compact(). Sample corner and center blocks. If discrepancies exist, run repair_structure(). Record final 100% certified scorecard to minecraft://inspection/scorecard."
   }
   ```
2. Await completion notification. Review `minecraft://inspection/scorecard`.
3. Update milestone: `record_progress_milestone(phase="QA_CERTIFICATION", progress_pct=100.0, status="COMPLETED")`.

### Step 6: Landmark Registration & Presentation
1. Register landmark in persistent cartography:
   Call `mark_location(name="<Monument Name>", position=[<x>, <y>, <z>], category="monument")`.
2. Present certified scorecard and architectural overview to the user.

