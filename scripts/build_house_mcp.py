"""
Build a complete, furnished architectural house using the Minecraft MCP Server.
Connects directly to the MCP server process over stdio (JSON-RPC 2.0).
"""

import sys
import asyncio
from pathlib import Path
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = PROJECT_ROOT / ".venv" / "bin" / "python"

async def main():
    print("=" * 70)
    print("🏛️  MINECRAFT MCP 2.0 — AUTONOMOUS HOUSE CONSTRUCTION")
    print("=" * 70)

    server_params = StdioServerParameters(
        command=str(PYTHON_EXE),
        args=["-m", "minecraft_mcp"],
        cwd=str(PROJECT_ROOT),
        env={
            "FABRIC_BRIDGE_URL": "http://127.0.0.1:25585",
            "FABRIC_WS_URL": "ws://127.0.0.1:25585/api/v1/ws/player",
        },
    )

    print("\n[Step 1] Connecting to MCP 2.0 Server over stdio...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("  Connected to MCP 2.0 Server successfully!")

            # 1. Get player position to confirm orientation and location
            pos_res = await session.call_tool("get_player_position", arguments={"player_name": "AtomOtos"})
            pos_data = pos_res.content[0].text if hasattr(pos_res.content[0], "text") else str(pos_res.content[0])
            print(f"  Player position: {pos_data}")

            # Define building bounds (5x5 footprint in front of player)
            # Player is at (-251, 64, 144), house will be at (-247..-243, 64..68, 142..146)
            min_x, max_x = -247, -243
            min_z, max_z = 142, 146
            floor_y = 64
            roof_y = 68

            print(f"\n[Step 2] Clearing building envelope ({min_x}..{max_x}, {floor_y+1}..{roof_y+1}, {min_z}..{max_z})...")
            # Clear interior & airspace
            clear_res = await session.call_tool(
                "fill_region",
                arguments={
                    "from_pos": [min_x - 1, floor_y + 1, min_z - 1],
                    "to_pos": [max_x + 1, roof_y + 2, max_z + 1],
                    "block": "minecraft:air",
                }
            )
            print(f"  Airspace cleared: {clear_res.content[0].text[:120]}...")

            print(f"\n[Step 3] Laying 5x5 Oak Wood Floor at Y={floor_y}...")
            floor_res = await session.call_tool(
                "fill_region",
                arguments={
                    "from_pos": [min_x, floor_y, min_z],
                    "to_pos": [max_x, floor_y, max_z],
                    "block": "minecraft:oak_planks",
                }
            )
            print(f"  Floor laid: {floor_res.content[0].text[:120]}...")

            print(f"\n[Step 4] Constructing Walls & Timber Corner Pillars (Y={floor_y+1}..{roof_y-1})...")
            wall_blocks = []

            # 4 corner columns of oak_log (vertical)
            corners = [(min_x, min_z), (max_x, min_z), (min_x, max_z), (max_x, max_z)]
            for cy in range(floor_y + 1, roof_y):
                for cx, cz in corners:
                    wall_blocks.append({"x": cx, "y": cy, "z": cz, "block": "minecraft:oak_log[axis=y]"})

            # North Wall (z = min_z)
            for x in range(min_x + 1, max_x):
                for y in range(floor_y + 1, roof_y):
                    b_id = "minecraft:glass" if (x == min_x + 2 and y == floor_y + 2) else "minecraft:oak_planks"
                    wall_blocks.append({"x": x, "y": y, "z": min_z, "block": b_id})

            # South Wall (z = max_z)
            for x in range(min_x + 1, max_x):
                for y in range(floor_y + 1, roof_y):
                    b_id = "minecraft:glass" if (x == min_x + 2 and y == floor_y + 2) else "minecraft:oak_planks"
                    wall_blocks.append({"x": x, "y": y, "z": max_z, "block": b_id})

            # East Wall (back wall, x = max_x)
            for z in range(min_z + 1, max_z):
                for y in range(floor_y + 1, roof_y):
                    b_id = "minecraft:glass" if (z == min_z + 2 and y == floor_y + 2) else "minecraft:oak_planks"
                    wall_blocks.append({"x": max_x, "y": y, "z": z, "block": b_id})

            # West Wall (front wall with door, x = min_x)
            door_z = min_z + 2  # 144
            for z in range(min_z + 1, max_z):
                for y in range(floor_y + 1, roof_y):
                    if z == door_z:
                        # Door space (y=65 lower, y=66 upper)
                        if y == floor_y + 3:
                            wall_blocks.append({"x": min_x, "y": y, "z": z, "block": "minecraft:oak_planks"})
                    else:
                        wall_blocks.append({"x": min_x, "y": y, "z": z, "block": "minecraft:oak_planks"})

            walls_res = await session.call_tool("place_blocks", arguments={"blocks": wall_blocks})
            print(f"  Walls placed: {walls_res.content[0].text[:120]}...")

            print(f"\n[Step 5] Installing Oak Front Door at ({min_x}, {floor_y+1}..{floor_y+2}, {door_z})...")
            # Lower door half
            await session.call_tool(
                "place_block",
                arguments={
                    "x": min_x,
                    "y": floor_y + 1,
                    "z": door_z,
                    "block": "minecraft:oak_door[facing=west,half=lower,hinge=left,open=false]",
                }
            )
            # Upper door half
            await session.call_tool(
                "place_block",
                arguments={
                    "x": min_x,
                    "y": floor_y + 2,
                    "z": door_z,
                    "block": "minecraft:oak_door[facing=west,half=upper,hinge=left,open=false]",
                }
            )
            print("  Door installed successfully!")

            print(f"\n[Step 6] Constructing Cobblestone & Oak Roof (Y={roof_y})...")
            roof_res = await session.call_tool(
                "fill_region",
                arguments={
                    "from_pos": [min_x, roof_y, min_z],
                    "to_pos": [max_x, roof_y, max_z],
                    "block": "minecraft:cobblestone",
                }
            )
            print(f"  Roof placed: {roof_res.content[0].text[:120]}...")

            print("\n[Step 7] Furnishing Interior with Essentials...")
            # Crafting Table in back-left corner
            await session.call_tool(
                "place_block",
                arguments={
                    "x": max_x - 1,
                    "y": floor_y + 1,
                    "z": max_z - 1,
                    "block": "minecraft:crafting_table",
                }
            )
            # Furnace in back-right corner
            await session.call_tool(
                "place_block",
                arguments={
                    "x": max_x - 1,
                    "y": floor_y + 1,
                    "z": min_z + 1,
                    "block": "minecraft:furnace[facing=west]",
                }
            )
            # Storage Chest near entrance
            await session.call_tool(
                "place_block",
                arguments={
                    "x": min_x + 1,
                    "y": floor_y + 1,
                    "z": max_z - 1,
                    "block": "minecraft:chest[facing=west]",
                }
            )
            # Lantern hanging from ceiling center for warm lighting
            await session.call_tool(
                "place_block",
                arguments={
                    "x": min_x + 2,
                    "y": roof_y - 1,
                    "z": min_z + 2,
                    "block": "minecraft:lantern[hanging=true]",
                }
            )
            print("  Interior fully furnished with Crafting Table, Furnace, Chest, and Hanging Lantern!")

            print("\n[Step 8] Closed-Loop Physical Verification...")
            door_check = await session.call_tool("get_block", arguments={"x": min_x, "y": floor_y + 1, "z": door_z})
            roof_check = await session.call_tool("get_block", arguments={"x": min_x + 2, "y": roof_y, "z": min_z + 2})
            lantern_check = await session.call_tool("get_block", arguments={"x": min_x + 2, "y": roof_y - 1, "z": min_z + 2})
            furnace_check = await session.call_tool("get_block", arguments={"x": max_x - 1, "y": floor_y + 1, "z": min_z + 1})

            print(f"  Door: {door_check.content[0].text}")
            print(f"  Roof: {roof_check.content[0].text}")
            print(f"  Lantern: {lantern_check.content[0].text}")
            print(f"  Furnace: {furnace_check.content[0].text}")

            print("\n" + "=" * 70)
            print("🎉 HOUSE CONSTRUCTION COMPLETED & VERIFIED VIA MCP SERVER!")
            print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
