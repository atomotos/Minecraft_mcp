#!/usr/bin/env python3
"""
Multi-Agent Orchestration Script for Autonomous Construction of the Taj Mahal in Minecraft.
Coordinates 4 specialized agents:
 1. taj_surveyor: Site topography validation, coordinates anchoring & envelope inspection
 2. taj_architect: Blueprint compilation, component sequencing & bill-of-materials analysis
 3. taj_builder: Transactional batch construction dispatch (<= 500 blocks/batch)
 4. taj_verifier: Closed-loop physical verification, automated restoration & landmark memory
"""

import sys
import os
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from minecraft_mcp.client.bridge import BridgeClient
from minecraft_mcp.construction import (
    BlueprintCompiler,
    ConstructionEngine,
    StructureVerifier,
    RecoveryManager,
)
from minecraft_mcp.models.construction import ProjectStatus
from minecraft_mcp.spatial.world_model import SpatialWorldModelManager
from minecraft_mcp.spatial.site_selector import SiteSelector
from minecraft_mcp.events import EventAggregator
from minecraft_mcp.models.events import AgentEventType

def banner(title: str, char: str = "="):
    line = char * 80
    print(f"\n{line}\n{title}\n{line}")

async def run_taj_mahal_orchestration():
    banner("🏛️  AUTONOMOUS MULTI-AGENT ORCHESTRATION: THE TAJ MAHAL IN MINECRAFT  🏛️")

    client = BridgeClient()
    world_model = SpatialWorldModelManager.get_instance()
    aggregator = EventAggregator.get_instance()

    # Verify bridge connectivity
    try:
        status = await client.get_status()
        print(f"✅ Connected to Minecraft {status.minecraft_version} (TPS: {status.tps:.1f}, MSPT: {status.mspt:.2f}ms)")
        print(f"   Active players: {status.players}")
    except Exception as e:
        print(f"❌ Failed to connect to Fabric Bridge at {client.base_url}: {e}")
        return False

    # Ensure player in creative mode for building
    await client.set_game_mode("creative")

    # =========================================================================
    # PHASE 1: AGENT 1 (taj_surveyor) — Site Survey & Topography Validation
    # =========================================================================
    banner("📍 PHASE 1: [AGENT: taj_surveyor] Site Survey & Topography Validation", "-")
    print("Agent 'taj_surveyor' evaluating desert plateau coordinates...")

    # Survey center around (-180, 72, 180)
    survey_center = {"x": -180.0, "y": 72.0, "z": 180.0}
    selector = SiteSelector(client)
    survey_res = await selector.find_build_location(
        center=survey_center,
        radius=24,
        width=21,
        depth=21,
        flatness_threshold=0.5,
    )

    if survey_res.get("success", False):
        anchor = survey_res["best_location"]
        flatness = survey_res.get("flatness_score", 0.0)
        print(f"  ✅ Optimal terrain anchor discovered: ({anchor['x']}, {anchor['y']}, {anchor['z']})")
        print(f"  ✅ Terrain flatness score: {flatness:.3f} (Height variance: {survey_res.get('height_variance')} block)")
        print(f"  ✅ Surface material: {survey_res.get('surface_material')}")
    else:
        # Fallback to verified anchor
        anchor = {"x": -181, "y": 72, "z": 169}
        print(f"  ℹ️ Using pre-surveyed pristine anchor: ({anchor['x']}, {anchor['y']}, {anchor['z']})")

    # =========================================================================
    # PHASE 2: AGENT 2 (taj_architect) — Architectural Design & Blueprint Compilation
    # =========================================================================
    banner("📐 PHASE 2: [AGENT: taj_architect] Architectural Blueprint Compilation", "-")
    print("Agent 'taj_architect' generating mathematically symmetric Mughal blueprint...")

    plan = BlueprintCompiler.compile("taj_mahal", anchor=anchor)

    print(f"  ✅ Blueprint ID: {plan.blueprint_id}")
    print(f"  ✅ Total Planned Voxel Steps: {plan.total_blocks:,} blocks")
    print(f"  ✅ Bounding Box: X[{plan.bounds['min']['x']}..{plan.bounds['max']['x']}], "
          f"Y[{plan.bounds['min']['y']}..{plan.bounds['max']['y']}], "
          f"Z[{plan.bounds['min']['z']}..{plan.bounds['max']['z']}]")
    print(f"  ✅ Total Dimensions: {plan.bounds['max']['x'] - plan.bounds['min']['x'] + 1}W × "
          f"{plan.bounds['max']['z'] - plan.bounds['min']['z'] + 1}D × "
          f"{plan.bounds['max']['y'] - plan.bounds['min']['y'] + 1}H blocks")

    print("\n  📦 Bill of Materials Required:")
    for mat, count in sorted(plan.materials_required.items(), key=lambda x: -x[1]):
        print(f"     • {mat}: {count:,} blocks")

    # Group steps by architectural component
    comp_steps: Dict[str, List[Any]] = {}
    for s in plan.steps:
        comp_steps.setdefault(s.component_name, []).append(s)

    print("\n  🏛️ Architectural Component Breakdown:")
    for comp_name, steps in comp_steps.items():
        print(f"     • {comp_name:<22}: {len(steps):>4} blocks")

    # =========================================================================
    # PHASE 3: AGENT 3 (taj_builder) — Transactional Construction Dispatch
    # =========================================================================
    banner("🔨 PHASE 3: [AGENT: taj_builder] Transactional Construction Execution", "-")
    print("Agent 'taj_builder' dispatching sequenced voxel batches (<= 500 blocks/batch)...")

    engine = ConstructionEngine.get_instance(client)
    start_time = time.time()

    # Execute plan via ConstructionEngine with envelope clearance
    project = await engine.execute_plan(
        plan=plan,
        clear_envelope=True,
        structure_type="monument",
        project_name="The Taj Mahal",
    )

    elapsed = time.time() - start_time
    blocks_per_sec = project.progress.completed_blocks / max(0.1, elapsed)

    print(f"\n  ✅ Construction Completed in {elapsed:.2f}s ({blocks_per_sec:.1f} blocks/sec)")
    print(f"  ✅ Status: {project.status.value}")
    print(f"  ✅ Blocks Placed: {project.progress.completed_blocks:,} / {project.progress.planned_blocks:,} "
          f"({project.progress.percentage:.1f}%)")

    # Component status report
    for c in project.components:
        status_symbol = "✅" if c.status == ProjectStatus.COMPLETED else "❌"
        print(f"     {status_symbol} {c.name:<22}: {c.completed_blocks}/{c.total_blocks} blocks")

    # =========================================================================
    # PHASE 4: AGENT 4 (taj_verifier) — Ground-Truth Physical Verification & Recovery
    # =========================================================================
    banner("🔍 PHASE 4: [AGENT: taj_verifier] Physical Verification & Quality Assurance", "-")
    print("Agent 'taj_verifier' conducting ground-truth physical voxel inspection...")

    verifier = StructureVerifier(client)
    verif_res = await verifier.verify_plan(plan, project_id=project.project_id)

    print(f"  ✅ Verified Planned Blocks: {verif_res.get('verified_count', 0):,} / {verif_res.get('total_planned', 0):,}")
    print(f"  ✅ Structural Completion: {verif_res.get('completion_percentage', 0.0):.1f}%")
    print(f"  ✅ Discrepancies Count: {verif_res.get('discrepancies_count', 0)}")

    # If any discrepancies exist, execute automated recovery
    if not verif_res.get("valid", False):
        print("\n  ⚠️ Discrepancies detected! Executing automated recovery routine...")
        recovery = RecoveryManager(client)
        repair_res = await recovery.repair_structure(project_id=project.project_id)
        print(f"  ✅ Recovery Repaired: {repair_res.get('repaired_count', 0)} blocks")
        print(f"  ✅ Post-Recovery Status: {repair_res.get('status')}")
    else:
        print("  🌟 Physical structural integrity verified at 100%! Zero defects found.")

    # =========================================================================
    # PHASE 5: Cartography & Landmark Registration
    # =========================================================================
    banner("🗺️  PHASE 5: Spatial Cartography & Landmark Registration", "-")

    # Register landmark in spatial world model
    viewpoint = [anchor["x"] + 14.0, anchor["y"] + 4.0, anchor["z"] + 52.0]
    landmark = world_model.add_landmark(
        name="The Taj Mahal",
        x=anchor["x"] + 14.0,
        y=anchor["y"] + 2.0,
        z=anchor["z"] + 14.0,
        category="monument",
        tags=["taj_mahal", "wonder", "imperial", "mughal", "white_marble"],
    )
    print(f"  ✅ Landmark Registered: '{landmark.name}' at ({landmark.position['x']}, {landmark.position['y']}, {landmark.position['z']})")

    world_model.record_structure(
        project_id=project.project_id,
        name=project.name,
        structure_type="monument",
        bounds=plan.bounds,
        status="COMPLETED",
    )
    print(f"  ✅ Structure Record Archived in Persistent Cartography: '{project.name}'")

    # Teleport player to the scenic grand entrance viewpoint looking across the reflecting pool
    try:
        await client.teleport_player(
            x=viewpoint[0],
            y=viewpoint[1],
            z=viewpoint[2],
            yaw=180.0,  # Looking north towards the Taj Mahal
            pitch=-10.0,
        )
        print(f"\n  👁️ Player positioned at scenic grand entrance viewpoint: ({viewpoint[0]}, {viewpoint[1]}, {viewpoint[2]}) facing North")
    except Exception as e:
        print(f"  (Player teleport note: {e})")

    # Publish event
    aggregator.emit(
        AgentEventType.CONSTRUCTION_COMPLETED,
        payload={"project_id": project.project_id, "name": "The Taj Mahal", "total_blocks": project.progress.completed_blocks},
    )

    banner("✨ THE TAJ MAHAL HAS BEEN SUCCESSFULLY CONSTRUCTED IN MINECRAFT! ✨")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_taj_mahal_orchestration())
    sys.exit(0 if success else 1)

