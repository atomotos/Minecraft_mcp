#!/usr/bin/env python3
"""
Test script for Phase 3: Spatial Intelligence, Architectural Planning & Autonomous Construction.
Tests the MCP 2.0 server over stdio against the live Minecraft Fabric 26.2 server.
Executes the comprehensive 12-point Phase 3 verification suite:
 1. Tool Registry Verification (All 32 Tools Registered)
 2. Resource Registry Verification (All 11 Dynamic Resources Registered)
 3. Prompt Registry Verification (All 6 Prompts Registered)
 4. Architectural & Material Knowledge Resources (blocks, materials, architecture)
 5. Spatial Memory & Landmark Tracking (mark_location, get_landmarks, scan_region)
 6. Topographical Site Selection (find_build_location with flatness scoring)
 7. Architectural Requirements Analysis (check_requirements & crafting calculation)
 8. Voxel-Aware 3D A* Navigation (navigate_to with terrain step calculation)
 9. Parametric Curtain Wall Generator (build_wall with crenellations)
10. Parametric Roof Generator (build_roof with styles & materials)
11. Autonomous Structure Construction (build_structure end-to-end execution)
12. Structure Verification & Automated Repair (repair_structure & active plan/progress tracking)
"""

import sys
import os
import asyncio
import json
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

def parse_tool_result(res) -> dict:
    if not res or not res.content:
        return {}
    txt = res.content[0].text
    try:
        return json.loads(txt)
    except Exception:
        return {"raw": txt}

async def run_phase3_verification():
    print("=" * 80)
    print("🏰 MINECRAFT MCP 2.0 — PHASE 3 AUTONOMOUS ARCHITECTURE & SPATIAL SUITE")
    print("=" * 80)

    server_params = StdioServerParameters(
        command=str(root_dir / ".venv" / "bin" / "python"),
        args=["-m", "minecraft_mcp"],
        env=os.environ.copy(),
    )

    passed_tests = 0
    total_tests = 0

    def assert_test(condition: bool, name: str, details: str = ""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  ✅ [PASS] Test {total_tests:02d}: {name} {details}")
        else:
            print(f"  ❌ [FAIL] Test {total_tests:02d}: {name} {details}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to MCP 2.0 Server over stdio.\n")

            # ------------------------------------------------------------------
            # Test 1: Tool Registry (32 tools)
            # ------------------------------------------------------------------
            tools_res = await session.list_tools()
            tool_names = {t.name for t in tools_res.tools}
            expected_phase3_tools = {
                "build_structure", "build_wall", "build_roof",
                "find_build_location", "navigate_to", "check_requirements",
                "repair_structure", "scan_region", "mark_location", "get_landmarks"
            }
            has_all_p3_tools = expected_phase3_tools.issubset(tool_names)
            assert_test(
                len(tool_names) >= 32 and has_all_p3_tools,
                "Tool Registry Verification",
                f"({len(tool_names)} registered, all 10 Phase 3 tools present)"
            )

            # ------------------------------------------------------------------
            # Test 2: Resource Registry (11 resources)
            # ------------------------------------------------------------------
            res_list = await session.list_resources()
            resource_uris = {str(r.uri) for r in res_list.resources}
            expected_phase3_resources = {
                "minecraft://world/map",
                "minecraft://construction/current",
                "minecraft://knowledge/blocks",
                "minecraft://knowledge/materials",
                "minecraft://knowledge/architecture",
                "minecraft://agent/plan"
            }
            has_all_p3_res = expected_phase3_resources.issubset(resource_uris)
            assert_test(
                len(resource_uris) >= 11 and has_all_p3_res,
                "Resource Registry Verification",
                f"({len(resource_uris)} registered, all 6 Phase 3 resources present)"
            )

            # ------------------------------------------------------------------
            # Test 3: Prompt Registry (6 prompts)
            # ------------------------------------------------------------------
            prompts_res = await session.list_prompts()
            prompt_names = {p.name for p in prompts_res.prompts}
            expected_prompts = {
                "explore_area", "architect_structure", "construct_structure",
                "resume_construction", "repair_structure", "establish_base"
            }
            has_all_prompts = expected_prompts.issubset(prompt_names)
            assert_test(
                len(prompt_names) >= 6 and has_all_prompts,
                "Prompt Registry Verification",
                f"({len(prompt_names)} prompts registered)"
            )

            # ------------------------------------------------------------------
            # Test 4: Knowledge Resources
            # ------------------------------------------------------------------
            blocks_res = await session.read_resource("minecraft://knowledge/blocks")
            blocks_data = json.loads(blocks_res.contents[0].text)
            materials_res = await session.read_resource("minecraft://knowledge/materials")
            materials_data = json.loads(materials_res.contents[0].text)
            arch_res = await session.read_resource("minecraft://knowledge/architecture")
            arch_data = json.loads(arch_res.contents[0].text)

            knowledge_valid = (
                len(blocks_data) >= 5 and
                len(materials_data) >= 3 and
                "templates" in arch_data and
                "watchtower" in arch_data["templates"]
            )
            assert_test(
                knowledge_valid,
                "Knowledge Resources",
                f"({len(blocks_data)} blocks, {len(materials_data)} palettes, {len(arch_data.get('templates', []))} templates)"
            )

            # ------------------------------------------------------------------
            # Test 5: Spatial Memory & Landmark Tracking
            # ------------------------------------------------------------------
            mark_res = await session.call_tool(
                "mark_location",
                arguments={"name": "Pioneer Camp", "position": [-250.0, 64.0, 150.0], "category": "base", "tags": ["camp", "phase3"]}
            )
            mark_data = parse_tool_result(mark_res)

            get_lm_res = await session.call_tool("get_landmarks", arguments={"category": "base"})
            get_lm_data = parse_tool_result(get_lm_res)

            scan_res = await session.call_tool("scan_region", arguments={"center": [-250, 64, 150], "radius": 8})
            scan_data = parse_tool_result(scan_res)

            map_res = await session.read_resource("minecraft://world/map")
            map_data = json.loads(map_res.contents[0].text)

            spatial_valid = (
                mark_data.get("success", False) and
                get_lm_data.get("count", 0) >= 1 and
                scan_data.get("success", False) and
                len(map_data.get("landmarks", [])) >= 1
            )
            assert_test(
                spatial_valid,
                "Spatial Memory & Landmarks",
                f"(Landmark created: '{mark_data.get('landmark', {}).get('name')}', {scan_data.get('total_blocks_scanned', 0)} blocks scanned)"
            )

            # ------------------------------------------------------------------
            # Test 6: Topographical Site Selection
            # ------------------------------------------------------------------
            site_res = await session.call_tool(
                "find_build_location",
                arguments={"radius": 16, "width": 7, "depth": 7, "flatness_threshold": 0.5, "center": [-250, 64, 150]}
            )
            site_data = parse_tool_result(site_res)
            site_valid = site_data.get("success", False) and "best_location" in site_data
            best_loc = site_data.get("best_location", {"x": -260, "y": 64, "z": 160})
            assert_test(
                site_valid,
                "Topographical Site Selection",
                f"(Best site at ({best_loc.get('x')}, {best_loc.get('y')}, {best_loc.get('z')}), flatness {site_data.get('flatness_score')})"
            )

            # ------------------------------------------------------------------
            # Test 7: Architectural Requirements Analysis
            # ------------------------------------------------------------------
            req_res = await session.call_tool(
                "check_requirements",
                arguments={"blueprint": "watchtower", "location": best_loc}
            )
            req_data = parse_tool_result(req_res)
            req_valid = (
                req_data.get("success", False) and
                req_data.get("total_blocks_required", 0) > 0 and
                "materials_required" in req_data
            )
            assert_test(
                req_valid,
                "Requirements & Crafting Calculation",
                f"({req_data.get('total_blocks_required')} blocks needed, status '{req_data.get('status')}')"
            )

            # ------------------------------------------------------------------
            # Test 8: Voxel-Aware 3D A* Navigation
            # ------------------------------------------------------------------
            nav_target_x = float(best_loc.get("x", -250))
            nav_target_y = float(best_loc.get("y", 64))
            nav_target_z = float(best_loc.get("z", 150))
            nav_res = await session.call_tool(
                "navigate_to",
                arguments={"x": nav_target_x, "y": nav_target_y, "z": nav_target_z, "tolerance": 4.0}
            )
            nav_data = parse_tool_result(nav_res)
            nav_valid = nav_data.get("success", False)
            assert_test(
                nav_valid,
                "Voxel 3D A* Navigation",
                f"(Arrived: {nav_data.get('arrived', False)}, final pos: {nav_data.get('final_position')})"
            )

            # ------------------------------------------------------------------
            # Test 9: Parametric Curtain Wall Generator
            # ------------------------------------------------------------------
            wall_start = [best_loc.get("x", -260), best_loc.get("y", 64), best_loc.get("z", 160) - 4]
            wall_end = [best_loc.get("x", -260) + 5, best_loc.get("y", 64), best_loc.get("z", 160) - 4]
            wall_res = await session.call_tool(
                "build_wall",
                arguments={
                    "start_pos": wall_start,
                    "end_pos": wall_end,
                    "height": 3,
                    "thickness": 1,
                    "material": "minecraft:stone_bricks",
                    "crenellations": True
                }
            )
            wall_data = parse_tool_result(wall_res)
            wall_valid = wall_data.get("success", False) and wall_data.get("placed_count", 0) > 0
            assert_test(
                wall_valid,
                "Parametric Wall Generator",
                f"(Placed {wall_data.get('placed_count')} stone brick blocks with crenellations)"
            )

            # ------------------------------------------------------------------
            # Test 10: Parametric Roof Generator
            # ------------------------------------------------------------------
            roof_origin = [best_loc.get("x", -260), best_loc.get("y", 64) + 4, best_loc.get("z", 160) - 4]
            roof_res = await session.call_tool(
                "build_roof",
                arguments={
                    "origin": roof_origin,
                    "width": 6,
                    "depth": 3,
                    "style": "flat",
                    "slab_material": "minecraft:stone_brick_slab",
                    "overhang": False
                }
            )
            roof_data = parse_tool_result(roof_res)
            roof_valid = roof_data.get("success", False) and roof_data.get("placed_count", 0) > 0
            assert_test(
                roof_valid,
                "Parametric Roof Generator",
                f"(Placed {roof_data.get('placed_count')} slab blocks, style '{roof_data.get('style')}')"
            )

            # ------------------------------------------------------------------
            # Test 11: Autonomous Structure Construction (End-to-End)
            # ------------------------------------------------------------------
            # Build a compact temple / pavilion structure (5x5, pillared)
            build_site = {"x": best_loc.get("x", -260) + 8, "y": best_loc.get("y", 64), "z": best_loc.get("z", 160)}
            struct_res = await session.call_tool(
                "build_structure",
                arguments={
                    "blueprint": "pillared_temple",
                    "location": build_site,
                    "clear_envelope": True
                }
            )
            struct_data = parse_tool_result(struct_res)
            struct_valid = (
                struct_data.get("status") == "COMPLETED" and
                struct_data.get("progress", {}).get("completed_blocks", 0) > 0
            )
            assert_test(
                struct_valid,
                "Autonomous Structure Construction",
                f"(Project: '{struct_data.get('project_id')}', {struct_data.get('progress', {}).get('completed_blocks')} blocks placed, status '{struct_data.get('status')}')"
            )

            # ------------------------------------------------------------------
            # Test 12: Structure Verification & Automated Repair
            # ------------------------------------------------------------------
            # Inspect plan resource and current project resource
            plan_res = await session.read_resource("minecraft://agent/plan")
            plan_data = json.loads(plan_res.contents[0].text)
            curr_proj_res = await session.read_resource("minecraft://construction/current")
            curr_proj_data = json.loads(curr_proj_res.contents[0].text)

            # Intentionally simulate damage: break 1 block of the built temple
            damage_pos = {"x": build_site["x"] + 1, "y": build_site["y"] + 1, "z": build_site["z"] + 1}
            await session.call_tool("break_block", arguments={"x": damage_pos["x"], "y": damage_pos["y"], "z": damage_pos["z"], "drop_loot": False})

            # Run automated repair
            repair_res = await session.call_tool("repair_structure", arguments={"project_id": struct_data.get("project_id")})
            repair_data = parse_tool_result(repair_res)
            repair_valid = (
                repair_data.get("success", False) and
                repair_data.get("repaired_count", 0) >= 1 and
                repair_data.get("status") == "COMPLETED"
            )
            assert_test(
                repair_valid,
                "Verification & Automated Repair",
                f"(Repaired {repair_data.get('repaired_count')} block(s), final status '{repair_data.get('status')}')"
            )

    print("\n" + "=" * 80)
    print(f"📊 PHASE 3 VERIFICATION SUMMARY: {passed_tests}/{total_tests} TESTS PASSED ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 80)

    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(run_phase3_verification())
    sys.exit(0 if success else 1)
