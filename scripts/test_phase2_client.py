#!/usr/bin/env python3
"""
Test script for Phase 2: World Mutation, Player Actions & Direct Building.
Tests the MCP 2.0 server over stdio against the live Minecraft Fabric 26.2 server.
Executes the comprehensive 12-point Test Set A suite:
 1. Single Block Placement (place_block) & Closed-Loop Verification
 2. Batch Block Placement (place_blocks) via 6-Stage Pipeline
 3. Block Destruction (break_block) & Air State Verification
 4. Bounded Cuboid Fill (fill_region) & Sample Verification
 5. Safety Boundary Enforcement (Y bounds [-64, 320] and max volume 500)
 6. Door / Trapdoor Interaction (interact_with_block toggle)
 7. Button / Lever Interaction (interact_with_block power toggle)
 8. Container Interaction (interact_with_block container menu)
 9. Basic Locomotion (move_to) & Tolerance Threshold
10. Movement Cancellation (stop_movement)
11. Stuck Detection (move_to into obstructed wall)
12. Action State Resource (minecraft://action/state tracking)
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

async def run_phase2_verification():
    print("=" * 75)
    print("🚀 MINECRAFT MCP 2.0 — PHASE 2 MUTATION & ACTIONS VERIFICATION")
    print("=" * 75)

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

    print("\n[Step 1] Connecting to MCP 2.0 server process over stdio...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("  Connected to MCP 2.0 server successfully!")

            # Verify server connectivity
            status_res = parse_tool_result(await session.call_tool("get_server_status", {}))
            if not status_res.get("connected", False):
                print(f"  ❌ Cannot connect to Minecraft Fabric Bridge: {status_res}")
                sys.exit(1)
            print(f"  Minecraft Server online: v{status_res.get('minecraft_version')}, TPS: {status_res.get('tps')}")

            # Get player position to anchor test coordinates
            player_state = parse_tool_result(await session.call_tool("get_player_state", {}))
            if "position" in player_state:
                px = int(player_state["position"]["x"])
                py = int(player_state["position"]["y"])
                pz = int(player_state["position"]["z"])
                print(f"  Found connected player '{player_state.get('name')}' at ({px}, {py}, {pz})")
            else:
                px, py, pz = -238, 67, 143
                print(f"  Using default test anchor at ({px}, {py}, {pz})")

            # Offset test coordinates slightly away from player feet
            tx = px + 3
            ty = py
            tz = pz + 3

            # Switch player to creative mode for tests
            await session.call_tool("switch_game_mode", {"game_mode": "creative"})

            # -------------------------------------------------------------------
            # Test 1: Single Block Placement (place_block) & Closed-Loop Verification
            # -------------------------------------------------------------------
            print("\n--- Test 1: Single Block Placement (place_block) ---")
            p1_res = parse_tool_result(await session.call_tool("place_block", {
                "x": tx, "y": ty, "z": tz, "block": "minecraft:stone"
            }))
            print(f"  Result: {p1_res}")
            check_p1 = parse_tool_result(await session.call_tool("get_block", {"x": tx, "y": ty, "z": tz}))
            assert_test(
                p1_res.get("verified") is True and check_p1.get("blockId") == "minecraft:stone",
                "Single Block Placement & Verification",
                f"(placed stone at {tx},{ty},{tz}, verified={p1_res.get('verified')})"
            )

            # -------------------------------------------------------------------
            # Test 2: Batch Block Placement (place_blocks) via 6-Stage Pipeline
            # -------------------------------------------------------------------
            print("\n--- Test 2: Batch Block Placement (place_blocks) ---")
            batch_blocks = [
                {"x": tx, "y": ty + 1, "z": tz, "block": "minecraft:oak_planks"},
                {"x": tx + 1, "y": ty + 1, "z": tz, "block": "minecraft:oak_planks"},
                {"x": tx + 2, "y": ty + 1, "z": tz, "block": "minecraft:oak_planks"},
            ]
            p2_res = parse_tool_result(await session.call_tool("place_blocks", {"blocks": batch_blocks}))
            print(f"  Result: {p2_res}")
            assert_test(
                p2_res.get("success") is True and p2_res.get("placed_count") == 3 and p2_res.get("verified") is True,
                "Batch Block Placement (6-Stage Pipeline)",
                f"(placed 3 oak_planks, verified={p2_res.get('verified')})"
            )

            # -------------------------------------------------------------------
            # Test 3: Block Destruction (break_block) & Air State Verification
            # -------------------------------------------------------------------
            print("\n--- Test 3: Block Destruction (break_block) ---")
            p3_res = parse_tool_result(await session.call_tool("break_block", {"x": tx, "y": ty, "z": tz, "drop_loot": True}))
            print(f"  Result: {p3_res}")
            check_p3 = parse_tool_result(await session.call_tool("get_block", {"x": tx, "y": ty, "z": tz}))
            assert_test(
                p3_res.get("verified") is True and check_p3.get("isAir") is True,
                "Block Destruction & Air State Verification",
                f"(destroyed {tx},{ty},{tz}, isAir={check_p3.get('isAir')})"
            )

            # Clean up test 2 batch blocks
            for b in batch_blocks:
                await session.call_tool("break_block", {"x": b["x"], "y": b["y"], "z": b["z"], "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 4: Bounded Cuboid Fill (fill_region) & Sample Verification
            # -------------------------------------------------------------------
            print("\n--- Test 4: Bounded Cuboid Fill (fill_region) ---")
            fill_from = [tx, ty, tz]
            fill_to = [tx + 1, ty + 1, tz + 1]  # 2x2x2 = 8 blocks
            p4_res = parse_tool_result(await session.call_tool("fill_region", {
                "from_pos": fill_from,
                "to_pos": fill_to,
                "block": "minecraft:glass"
            }))
            print(f"  Result: {p4_res}")
            assert_test(
                p4_res.get("success") is True and p4_res.get("volume") == 8 and p4_res.get("verified") is True,
                "Bounded Cuboid Fill & Sample Verification",
                f"(volume={p4_res.get('volume')}, placed={p4_res.get('placed_count')})"
            )

            # Clean up glass fill
            for fx in range(tx, tx + 2):
                for fy in range(ty, ty + 2):
                    for fz in range(tz, tz + 2):
                        await session.call_tool("break_block", {"x": fx, "y": fy, "z": fz, "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 5: Safety Boundary Enforcement (Y bounds & volume limits)
            # -------------------------------------------------------------------
            print("\n--- Test 5: Safety Boundary Enforcement ---")
            # 5a. Out of bounds Y (< -64)
            err_y = parse_tool_result(await session.call_tool("place_block", {
                "x": tx, "y": -70, "z": tz, "block": "minecraft:stone"
            }))
            # 5b. Excessive volume (> 500 blocks)
            err_vol = parse_tool_result(await session.call_tool("fill_region", {
                "from_pos": [tx, ty, tz],
                "to_pos": [tx + 10, ty + 10, tz + 10],  # 11x11x11 = 1331 blocks > 500
                "block": "minecraft:stone"
            }))
            safety_passed = (
                err_y.get("code") == "SAFETY_VIOLATION" and
                err_vol.get("code") == "SAFETY_VIOLATION"
            )
            assert_test(
                safety_passed,
                "Deterministic Safety Boundaries (Y in [-64, 320], Volume <= 500)",
                f"(Y=-70 -> {err_y.get('code')}, Vol=1331 -> {err_vol.get('code')})"
            )

            # -------------------------------------------------------------------
            # Test 6: Door / Trapdoor Interaction (interact_with_block)
            # -------------------------------------------------------------------
            print("\n--- Test 6: Door / Trapdoor Interaction ---")
            # Place closed door
            await session.call_tool("place_block", {
                "x": tx, "y": ty, "z": tz,
                "block": "minecraft:oak_door[facing=north,half=lower,open=false]"
            })
            p6_res = parse_tool_result(await session.call_tool("interact_with_block", {
                "x": tx, "y": ty, "z": tz
            }))
            print(f"  Result: {p6_res}")
            assert_test(
                p6_res.get("interaction_type") == "door_toggle" and p6_res.get("state_changed") is True,
                "Door / Trapdoor Interaction (State Toggle)",
                f"(type={p6_res.get('interaction_type')}, state_changed={p6_res.get('state_changed')})"
            )
            await session.call_tool("break_block", {"x": tx, "y": ty, "z": tz, "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 7: Button / Lever Interaction (interact_with_block)
            # -------------------------------------------------------------------
            print("\n--- Test 7: Button / Lever Interaction ---")
            # Place lever on top of a solid block
            await session.call_tool("place_block", {"x": tx, "y": ty, "z": tz, "block": "minecraft:stone"})
            await session.call_tool("place_block", {
                "x": tx, "y": ty + 1, "z": tz,
                "block": "minecraft:lever[face=floor,powered=false]"
            })
            p7_res = parse_tool_result(await session.call_tool("interact_with_block", {
                "x": tx, "y": ty + 1, "z": tz
            }))
            print(f"  Result: {p7_res}")
            assert_test(
                p7_res.get("interaction_type") == "lever_toggle" and p7_res.get("state_changed") is True,
                "Button / Lever Interaction (Power Toggle)",
                f"(type={p7_res.get('interaction_type')}, state_changed={p7_res.get('state_changed')})"
            )
            await session.call_tool("break_block", {"x": tx, "y": ty + 1, "z": tz, "drop_loot": False})
            await session.call_tool("break_block", {"x": tx, "y": ty, "z": tz, "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 8: Container / Crafting Station Interaction (interact_with_block)
            # -------------------------------------------------------------------
            print("\n--- Test 8: Container Interaction ---")
            await session.call_tool("place_block", {"x": tx, "y": ty, "z": tz, "block": "minecraft:chest"})
            p8_res = parse_tool_result(await session.call_tool("interact_with_block", {
                "x": tx, "y": ty, "z": tz
            }))
            print(f"  Result: {p8_res}")
            assert_test(
                p8_res.get("interaction_type") == "container_open" and p8_res.get("verified") is True,
                "Container / Chest Interaction (Menu Open)",
                f"(type={p8_res.get('interaction_type')}, verified={p8_res.get('verified')})"
            )
            await session.call_tool("break_block", {"x": tx, "y": ty, "z": tz, "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 9: Basic Locomotion (move_to) & Tolerance Threshold
            # -------------------------------------------------------------------
            print("\n--- Test 9: Basic Locomotion (move_to) ---")
            curr_pos = parse_tool_result(await session.call_tool("get_player_position", {}))
            c_x, c_y, c_z = curr_pos["x"], curr_pos["y"], curr_pos["z"]
            target_x, target_y, target_z = c_x + 1.5, c_y, c_z + 1.5

            p9_res = parse_tool_result(await session.call_tool("move_to", {
                "x": target_x, "y": target_y, "z": target_z, "speed": 1.0, "tolerance": 1.0
            }))
            print(f"  Result: {p9_res}")
            assert_test(
                p9_res.get("status") == "reached" or p9_res.get("distance_remaining", 10.0) <= 1.0,
                "Basic Locomotion (move_to Reached Within Tolerance)",
                f"(status={p9_res.get('status')}, dist_remaining={p9_res.get('distance_remaining')})"
            )

            # -------------------------------------------------------------------
            # Test 10: Movement Cancellation (stop_movement)
            # -------------------------------------------------------------------
            print("\n--- Test 10: Movement Cancellation (stop_movement) ---")
            # Trigger stop_movement
            p10_res = parse_tool_result(await session.call_tool("stop_movement", {}))
            print(f"  Result: {p10_res}")
            assert_test(
                p10_res.get("status") == "cancelled" and p10_res.get("success") is True,
                "Movement Cancellation (stop_movement Immediate Halt)",
                f"(status={p10_res.get('status')})"
            )

            # -------------------------------------------------------------------
            # Test 11: Stuck Detection (Obstructed Navigation)
            # -------------------------------------------------------------------
            print("\n--- Test 11: Stuck Detection (Obstructed Navigation) ---")
            # Place a solid 2-block high wall in front of an obstruction target
            obs_x, obs_y, obs_z = tx, ty, tz
            await session.call_tool("place_block", {"x": obs_x, "y": obs_y, "z": obs_z, "block": "minecraft:obsidian"})
            await session.call_tool("place_block", {"x": obs_x, "y": obs_y + 1, "z": obs_z, "block": "minecraft:obsidian"})

            p11_res = parse_tool_result(await session.call_tool("move_to", {
                "x": float(obs_x), "y": float(obs_y), "z": float(obs_z), "speed": 1.0, "tolerance": 0.5
            }))
            print(f"  Result: {p11_res}")
            assert_test(
                p11_res.get("status") == "stuck" and p11_res.get("success") is False,
                "Stuck Detection (Obstruction Halts Navigation)",
                f"(status={p11_res.get('status')}, success={p11_res.get('success')})"
            )
            # Clean up obsidian
            await session.call_tool("break_block", {"x": obs_x, "y": obs_y + 1, "z": obs_z, "drop_loot": False})
            await session.call_tool("break_block", {"x": obs_x, "y": obs_y, "z": obs_z, "drop_loot": False})

            # -------------------------------------------------------------------
            # Test 12: Action State Resource (minecraft://action/state)
            # -------------------------------------------------------------------
            print("\n--- Test 12: Action State Resource Observation ---")
            state_text = await session.read_resource("minecraft://action/state")
            state_data = json.loads(state_text.contents[0].text if state_text.contents else "{}")
            print(f"  Resource payload: {state_data}")
            assert_test(
                "state" in state_data and state_data.get("state") in ["IDLE", "CANCELLED", "MOVING", "BUILDING", "MINING", "INTERACTING"],
                "Action State Resource (minecraft://action/state Lifecycle)",
                f"(state={state_data.get('state')}, updated_at={state_data.get('updated_at')})"
            )

    print("\n" + "=" * 75)
    print(f"🏆 PHASE 2 TEST SUITE RESULTS: {passed_tests}/{total_tests} TESTS PASSED")
    print("=" * 75)

    if passed_tests == total_tests:
        print("🎉 ALL 12 PHASE 2 ARCHITECTURAL REQUIREMENTS FULLY VERIFIED!")
        return 0
    else:
        print(f"⚠️ {total_tests - passed_tests} test(s) failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_phase2_verification())
    sys.exit(exit_code)

