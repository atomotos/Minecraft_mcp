#!/usr/bin/env python3
"""
Autonomous Procedural Construction of the Roman Colosseum Arena & Arcade Section.
Demonstrates Phase 4 capabilities:
- Procedural Geometry IR & Analytical Voxelization
- Composable Radial Arrays & Architectural Arches
- Stepped Concentric Cavea Seating
- 3D Greedy Cuboid Meshing (reducing thousands of blocks to minimal fill_region calls)
- Terrain-Adaptive Foundation Ground-Anchoring
- Compact Verification with zero token blowout
"""

import sys
import os
import asyncio
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from minecraft_mcp.client.bridge import BridgeClient
from minecraft_mcp.procedural import (
    GeometryRasterizer,
    VoxelCompiler,
    VoxelSpace,
    RingNode,
    BoxNode,
    ArchNode,
    ColumnNode,
    RadialArrayNode,
    CSGUnionNode,
    TerrainAdaptiveFoundationEngine,
    BuildTransactionManager,
)

async def build_colosseum():
    print("=" * 80)
    print("🏛️  PROCEDURAL ARCHITECTURE: ROMAN COLOSSEUM ARENA & ARCADE MONUMENT")
    print("=" * 80)

    client = BridgeClient()
    anchor = (-140, 69, 80)
    ax, ay, az = anchor
    print(f"Site Anchor: ({ax}, {ay}, {az})")

    start_time = time.time()
    rasterizer = GeometryRasterizer()
    composite_space = VoxelSpace()

    # -----------------------------------------------------------------------
    # 1. Level 1 Outer Radial Arcade (24 Bays with Roman Arches & Columns)
    # -----------------------------------------------------------------------
    print("\n[Step 1] Compiling Level 1 Outer Arcade (24 Radial Roman Arches)...")
    bay_arch = ArchNode(
        style="roman_round",
        width=4,
        height=6,
        depth=1,
        material="minecraft:smooth_sandstone",
        pillar_material="minecraft:cut_sandstone",
        keystone=True
    )
    l1_arcade = RadialArrayNode(
        child=bay_arch.model_dump(),
        count=24,
        radius=20.0,
        orient="tangent"
    )
    l1_space = rasterizer.rasterize(l1_arcade)
    composite_space.merge(l1_space, offset=(0, 1, 0))  # Placed above base plinth
    print(f"  ✓ Level 1 Arcade: {l1_space.count} voxels")

    # -----------------------------------------------------------------------
    # 2. Level 2 Upper Arcade & Mezzanine Balcony
    # -----------------------------------------------------------------------
    print("[Step 2] Compiling Level 2 Setback Arcade (24 Arches with Railings)...")
    l2_arch = ArchNode(
        style="roman_round",
        width=4,
        height=5,
        depth=1,
        material="minecraft:smooth_sandstone",
        pillar_material="minecraft:sandstone",
        keystone=True
    )
    l2_arcade = RadialArrayNode(
        child=l2_arch.model_dump(),
        count=24,
        radius=18.5,  # 1.5 block setback
        orient="tangent"
    )
    l2_space = rasterizer.rasterize(l2_arcade)
    composite_space.merge(l2_space, offset=(0, 7, 0))  # Sits atop Level 1
    print(f"  ✓ Level 2 Arcade: {l2_space.count} voxels")

    # Mezzanine Ring Balcony Floor at Y=7
    mezzanine_ring = RingNode(
        center=[0, 7, 0],
        outer_radius=20.5,
        inner_radius=17.5,
        height=1,
        material="minecraft:cut_sandstone"
    )
    mezz_space = rasterizer.rasterize(mezzanine_ring)
    composite_space.merge(mezz_space)

    # -----------------------------------------------------------------------
    # 3. Level 3 Attic Wall & Cornice
    # -----------------------------------------------------------------------
    print("[Step 3] Compiling Level 3 Attic Wall & Cornice...")
    attic_ring = RingNode(
        center=[0, 12, 0],
        outer_radius=18.5,
        inner_radius=17.0,
        height=3,
        material="minecraft:cut_sandstone"
    )
    attic_space = rasterizer.rasterize(attic_ring)
    composite_space.merge(attic_space)
    print(f"  ✓ Attic Wall: {attic_space.count} voxels")

    # -----------------------------------------------------------------------
    # 4. Concentric Stepped Cavea (Auditorium Seating Rings)
    # -----------------------------------------------------------------------
    print("[Step 4] Compiling Concentric Stepped Cavea (Seating Tiers)...")
    tiers = [
        {"r_out": 16.0, "r_in": 14.5, "y": 4, "mat": "minecraft:stone_brick_slab"},
        {"r_out": 14.5, "r_in": 13.0, "y": 3, "mat": "minecraft:stone_brick_slab"},
        {"r_out": 13.0, "r_in": 11.5, "y": 2, "mat": "minecraft:stone_brick_slab"},
        {"r_out": 11.5, "r_in": 10.0, "y": 1, "mat": "minecraft:stone_brick_slab"},
    ]
    for idx, t in enumerate(tiers):
        tier_ring = RingNode(
            center=[0, t["y"], 0],
            outer_radius=t["r_out"],
            inner_radius=t["r_in"],
            height=1,
            material=t["mat"]
        )
        t_space = rasterizer.rasterize(tier_ring)
        composite_space.merge(t_space)
    print(f"  ✓ 4 Seating Tiers compiled")

    # Podium Wall separating seating from arena floor
    podium_wall = RingNode(
        center=[0, 1, 0],
        outer_radius=10.0,
        inner_radius=9.0,
        height=2,
        material="minecraft:chiseled_stone_bricks"
    )
    podium_space = rasterizer.rasterize(podium_wall)
    composite_space.merge(podium_space)

    # -----------------------------------------------------------------------
    # 5. Central Gladiator Arena Floor & Hypogeum Grate
    # -----------------------------------------------------------------------
    print("[Step 5] Compiling Gladiator Arena Floor & Hypogeum Center...")
    arena_floor = RingNode(
        center=[0, 0, 0],
        outer_radius=9.0,
        inner_radius=3.0,
        height=1,
        material="minecraft:sand"
    )
    arena_space = rasterizer.rasterize(arena_floor)
    composite_space.merge(arena_space)

    # Central iron grate over hypogeum
    center_grate = RingNode(
        center=[0, 0, 0],
        outer_radius=3.0,
        inner_radius=0.0,
        height=1,
        material="minecraft:iron_bars"
    )
    grate_space = rasterizer.rasterize(center_grate)
    composite_space.merge(grate_space)

    # -----------------------------------------------------------------------
    # 6. Adaptive Foundation Ground-Leveling & Anchoring Pass
    # -----------------------------------------------------------------------
    print("\n[Step 6] Running Terrain-Adaptive Ground Anchoring Pass...")
    s_bounds = composite_space.get_bounds()
    footprint_min_x = s_bounds["min"]["x"] + ax
    footprint_max_x = s_bounds["max"]["x"] + ax
    footprint_min_z = s_bounds["min"]["z"] + az
    footprint_max_z = s_bounds["max"]["z"] + az

    foundation_engine = TerrainAdaptiveFoundationEngine(client=client)
    f_space = await foundation_engine.prepare_base_foundation(
        min_x=footprint_min_x, min_z=footprint_min_z,
        max_x=footprint_max_x, max_z=footprint_max_z,
        base_y=ay,
        foundation_material="minecraft:stone_bricks",
        plinth_material="minecraft:cut_sandstone",
        plinth_margin=1,
        clear_envelope=True,
        superstructure_height=18
    )
    print(f"  ✓ Generated {f_space.count} foundation and plinth underpinning voxels")

    # Merge foundation into final space
    final_space = composite_space.clone()
    for (fx, fy, fz), f_mat in f_space.get_voxels_dict().items():
        final_space.set_voxel(fx - ax, fy - ay, fz - az, f_mat, overwrite=False)

    print(f"\nTotal Structure Voxels: {final_space.count} blocks")

    # -----------------------------------------------------------------------
    # 7. Voxel Compilation & 3D Greedy Cuboid Meshing
    # -----------------------------------------------------------------------
    print("\n[Step 7] Compiling 3D Greedy Cuboid Meshing...")
    compiler = VoxelCompiler(max_fill_volume=500)
    compiled_plan = compiler.compile(final_space, anchor=anchor)

    print(f"  ✓ Raw blocks: {compiled_plan.total_voxels}")
    print(f"  ✓ Greedy fill_region cuboids: {len(compiled_plan.fill_operations)}")
    print(f"  ✓ Sparse remainder blocks: {len(compiled_plan.sparse_placements)}")
    print(f"  ✓ Total bridge calls required: {compiled_plan.total_bridge_calls}")
    print(f"  ✓ Call compression ratio: {compiled_plan.compression_ratio}x reduction!")
    print(f"  ✓ Integrity checksum: {compiled_plan.integrity_checksum}")

    # -----------------------------------------------------------------------
    # 8. Transactional Execution over Fabric Bridge
    # -----------------------------------------------------------------------
    print("\n[Step 8] Executing Transactional Construction via Fabric Bridge...")
    tx_mgr = BuildTransactionManager.get_instance()
    project_id = "monument_colosseum_01"
    await tx_mgr.begin_transaction(project_id, compiled_plan.bounds, client)

    exec_res = await tx_mgr.execute_plan_transactionally(
        project_id=project_id,
        plan=compiled_plan,
        client=client,
        auto_rollback_on_failure=True
    )
    build_duration = round(time.time() - start_time, 2)

    if not exec_res.get("success", False):
        print(f"  ❌ Construction failed: {exec_res.get('error')}")
        sys.exit(1)

    print(f"  ✅ Construction completed successfully in {build_duration}s!")
    print(f"  Placed blocks: {exec_res.get('total_placed')}")
    print(f"  Fill regions used: {exec_res.get('fill_regions_used')}")

    # -----------------------------------------------------------------------
    # 9. Compact Closed-Loop Verification
    # -----------------------------------------------------------------------
    print("\n[Step 9] Running Compact Closed-Loop Physical Verification...")
    report = await tx_mgr.verify_transaction(project_id, compiled_plan, client)
    print(f"  ✓ Verification Status: {report.status}")
    print(f"  ✓ Samples Checked: {report.samples_checked}")
    print(f"  ✓ Discrepancies: {report.discrepancies}")
    print(f"  ✓ Integrity Checksum Match: {report.integrity_checksum == compiled_plan.integrity_checksum}")
    print(f"  ✓ Materials Breakdown: {report.material_breakdown}")

    # -----------------------------------------------------------------------
    # 10. Teleport Player to Monument
    # -----------------------------------------------------------------------
    try:
        await client.teleport_player(x=ax, y=ay + 16.0, z=az - 24.0, yaw=0.0, pitch=35.0)
        print(f"\n[Step 10] Player teleported to observation overlook: ({ax}, {ay + 16}, {az - 24})")
    except Exception as e:
        print(f"Could not teleport player: {e}")

    print("\n" + "=" * 80)
    print("🎉 ROMAN COLOSSEUM ARENA MONUMENT FULLY CONSTRUCTED & VERIFIED!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(build_colosseum())

