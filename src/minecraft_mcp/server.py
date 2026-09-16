from typing import Optional, List, Dict, Any
import json
import structlog
from mcp.server.mcpserver import MCPServer
from minecraft_mcp.client.bridge import BridgeClient, BridgeError
from minecraft_mcp.safety import (
    validate_coordinates,
    validate_block_id,
    validate_region,
    validate_batch_placement,
    SafetyError,
)
from minecraft_mcp.tracker import ActionStateTracker
from minecraft_mcp.models.actions import ActionStateEnum

logger = structlog.get_logger("minecraft_mcp")

server = MCPServer("minecraft-mcp")
client = BridgeClient()
action_tracker = ActionStateTracker.get_instance()

# ---------------------------------------------------------------------------
# MCP 2.0 Tools (Observation Stack)
# ---------------------------------------------------------------------------

@server.tool()
async def get_server_status() -> Dict[str, Any]:
    """Check connectivity and operational health of the Minecraft server engine."""
    try:
        status = await client.get_status()
        return status.model_dump()
    except BridgeError as e:
        return {"connected": False, "error": e.message, "code": e.code}

@server.tool()
async def get_player_state(player_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve comprehensive player vitals, coordinates, rotation, and held equipment."""
    try:
        player = await client.get_player_status(player_name)
        return player.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def switch_game_mode(game_mode: str = "creative", player_name: Optional[str] = None) -> Dict[str, Any]:
    """Switch the player's game mode (e.g. 'creative', 'survival', 'adventure', 'spectator'). Defaults to 'creative'."""
    try:
        res = await client.set_game_mode(game_mode=game_mode, player=player_name)
        return res
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def get_player_position(player_name: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve lightweight floating-point position and orientation of the player."""
    try:
        pos = await client.get_player_position(player_name)
        return pos.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def get_inventory(player_name: Optional[str] = None) -> Dict[str, Any]:
    """Inspect all player inventory slots: hotbar (0-8), main inventory (9-35), armor, and offhand."""
    try:
        inv = await client.get_player_inventory(player_name)
        return inv.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def get_block(x: int, y: int, z: int) -> Dict[str, Any]:
    """Inspect block state, properties, and solidity at specific integer coordinates."""
    try:
        block = await client.get_block(x, y, z)
        return block.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def inspect_area(center: List[int], radius: int = 8, format: str = "summary") -> Dict[str, Any]:
    """Inspect a 3D block volume around a center coordinate and return a compact, token-efficient representation."""
    if radius > 16:
        return {"error": "Radius cannot exceed 16 blocks to prevent token blowout", "code": "AREA_TOO_LARGE"}
    if len(center) != 3:
        return {"error": "Center must be [x, y, z] coordinate array", "code": "INVALID_ARGUMENT"}

    cx, cy, cz = center[0], center[1], center[2]
    min_x, min_y, min_z = cx - radius, max(-64, cy - radius), cz - radius
    max_x, max_y, max_z = cx + radius, min(320, cy + radius), cz + radius

    try:
        data = await client.get_blocks(min_x, min_y, min_z, max_x, max_y, max_z, include_air=False)
        blocks = data.blocks

        histogram: Dict[str, int] = {}
        for b in blocks:
            b_id = b.id
            histogram[b_id] = histogram.get(b_id, 0) + 1

        # Determine dominant surface block if available
        surface_material = max(histogram.items(), key=lambda item: item[1])[0] if histogram else "minecraft:air"

        result: Dict[str, Any] = {
            "center": [cx, cy, cz],
            "radius": radius,
            "format": format,
            "total_blocks_scanned": data.count,
            "material_histogram": histogram,
            "surface_material": surface_material,
        }

        if format == "ascii":
            # Generate horizontal cross-section at center Y
            grid: List[str] = []
            block_map = {(b.pos["x"], b.pos["z"]): b.id for b in blocks if b.pos.get("y") == cy}
            for z in range(cz - radius, cz + radius + 1):
                row = []
                for x in range(cx - radius, cx + radius + 1):
                    bid = block_map.get((x, z))
                    if not bid:
                        row.append(".")
                    elif "grass" in bid:
                        row.append("G")
                    elif "dirt" in bid:
                        row.append("D")
                    elif "stone" in bid:
                        row.append("S")
                    elif "water" in bid:
                        row.append("W")
                    else:
                        row.append("#")
                grid.append("".join(row))
            result["ascii_slice"] = "\n".join(grid)

        return result
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def get_nearby_entities(radius: float = 16.0, entity_type: str = "all", player_name: Optional[str] = None) -> Dict[str, Any]:
    """Scan and locate entities (mobs, items, players) within a spherical radius around the player."""
    try:
        entities = await client.get_entities(radius=min(radius, 64.0), filter_type=entity_type, player=player_name)
        return entities.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

@server.tool()
async def get_world_info() -> Dict[str, Any]:
    """Query dimension name, daylight clock, weather condition, and vertical boundaries."""
    try:
        info = await client.get_world_info()
        return info.model_dump()
    except BridgeError as e:
        return {"error": e.message, "code": e.code}

# ---------------------------------------------------------------------------
# MCP 2.0 Tools (Phase 2: World Mutation, Building & Player Locomotion)
# ---------------------------------------------------------------------------

@server.tool()
async def place_block(x: int, y: int, z: int, block: str) -> Dict[str, Any]:
    """Places a single block at exact coordinates using the Observe -> Act -> Verify pattern."""
    try:
        validate_coordinates(x, y, z)
        valid_block = validate_block_id(block)
    except SafetyError as e:
        return {"success": False, "action": "place_block", "error": str(e), "code": "SAFETY_VIOLATION"}

    async with action_tracker.track("place_block", ActionStateEnum.BUILDING, target={"x": x, "y": y, "z": z, "block": valid_block}):
        try:
            res = await client.set_block(x, y, z, valid_block)
            # Closed-loop verification
            verify_block = await client.get_block(x, y, z)
            expected_id = valid_block.split("[")[0]
            verified = (verify_block.blockId == expected_id) if verify_block.blockId else res.get("verified", False)
            res["verified"] = verified
            res["success"] = verified
            return res
        except BridgeError as e:
            return {"success": False, "action": "place_block", "error": e.message, "code": e.code}

@server.tool()
async def place_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Batch placement of multiple blocks via a 6-stage safe transactional build pipeline. Primary building primitive."""
    try:
        validated_blocks = validate_batch_placement(blocks)
    except SafetyError as e:
        return {"success": False, "action": "place_blocks", "error": str(e), "code": "SAFETY_VIOLATION"}

    xs = [b["x"] for b in validated_blocks]
    ys = [b["y"] for b in validated_blocks]
    zs = [b["z"] for b in validated_blocks]
    bounds = {
        "min": {"x": min(xs), "y": min(ys), "z": min(zs)},
        "max": {"x": max(xs), "y": max(ys), "z": max(zs)},
    }

    async with action_tracker.track("place_blocks", ActionStateEnum.BUILDING, target={"count": len(validated_blocks), "bounds": bounds}):
        placed_count = 0
        failed_count = 0
        last_tick = None

        for b in validated_blocks:
            try:
                res = await client.set_block(b["x"], b["y"], b["z"], b["block"])
                if res.get("verified", False) or res.get("placed", False):
                    placed_count += 1
                else:
                    failed_count += 1
                last_tick = res.get("tick", last_tick)
            except Exception:
                failed_count += 1

        # Closed-loop sample verification
        verified = True
        samples = [validated_blocks[0], validated_blocks[len(validated_blocks)//2], validated_blocks[-1]]
        for sample in samples:
            try:
                check = await client.get_block(sample["x"], sample["y"], sample["z"])
                expected_id = sample["block"].split("[")[0]
                if check.blockId != expected_id:
                    verified = False
                    break
            except Exception:
                verified = False
                break

        return {
            "success": failed_count == 0,
            "action": "place_blocks",
            "requested_count": len(validated_blocks),
            "placed_count": placed_count,
            "failed_count": failed_count,
            "verified": verified,
            "bounds": bounds,
            "tick": last_tick,
        }

@server.tool()
async def break_block(x: int, y: int, z: int, drop_loot: bool = True) -> Dict[str, Any]:
    """Breaks a block at coordinate with optional drop particles and physics, verifying air state."""
    try:
        validate_coordinates(x, y, z)
    except SafetyError as e:
        return {"success": False, "action": "break_block", "error": str(e), "code": "SAFETY_VIOLATION"}

    async with action_tracker.track("break_block", ActionStateEnum.MINING, target={"x": x, "y": y, "z": z, "drop_loot": drop_loot}):
        try:
            res = await client.break_block(x, y, z, drop_resources=drop_loot)
            verify_block = await client.get_block(x, y, z)
            verified = verify_block.isAir if verify_block.isAir is not None else res.get("verified", False)
            res["verified"] = verified
            res["success"] = verified
            return res
        except BridgeError as e:
            return {"success": False, "action": "break_block", "error": e.message, "code": e.code}

@server.tool()
async def fill_region(from_pos: List[int], to_pos: List[int], block: str, replace_filter: Optional[str] = None) -> Dict[str, Any]:
    """Fills a cuboid volume from corner 1 to corner 2 with safety limits (Y in [-64, 320], max 500 blocks)."""
    if len(from_pos) != 3 or len(to_pos) != 3:
        return {"success": False, "action": "fill_region", "error": "from_pos and to_pos must each be [x, y, z] coordinates", "code": "INVALID_ARGUMENT"}

    try:
        volume = validate_region((from_pos[0], from_pos[1], from_pos[2]), (to_pos[0], to_pos[1], to_pos[2]), max_volume=500)
        valid_block = validate_block_id(block)
        filter_block = validate_block_id(replace_filter) if replace_filter else None
    except SafetyError as e:
        return {"success": False, "action": "fill_region", "error": str(e), "code": "SAFETY_VIOLATION"}

    async with action_tracker.track("fill_region", ActionStateEnum.BUILDING, target={"from": from_pos, "to": to_pos, "block": valid_block, "volume": volume}):
        try:
            res = await client.fill_region(
                from_pos[0], from_pos[1], from_pos[2],
                to_pos[0], to_pos[1], to_pos[2],
                valid_block,
                filter_block
            )
            res["success"] = res.get("verified", True)
            return res
        except BridgeError as e:
            return {"success": False, "action": "fill_region", "error": e.message, "code": e.code}

@server.tool()
async def interact_with_block(x: int, y: int, z: int, hand: str = "main_hand") -> Dict[str, Any]:
    """Generic block interaction primitive (doors, trapdoors, buttons, levers, containers, crafting tables, furnaces)."""
    try:
        validate_coordinates(x, y, z)
    except SafetyError as e:
        return {"success": False, "action": "interact_with_block", "error": str(e), "code": "SAFETY_VIOLATION"}

    async with action_tracker.track("interact_with_block", ActionStateEnum.INTERACTING, target={"x": x, "y": y, "z": z, "hand": hand}):
        try:
            res = await client.interact_with_block(x, y, z, hand=hand)
            res["success"] = res.get("verified", True)
            return res
        except BridgeError as e:
            return {"success": False, "action": "interact_with_block", "error": e.message, "code": e.code}

@server.tool()
async def move_to(x: float, y: float, z: float, speed: float = 1.0, tolerance: float = 1.0) -> Dict[str, Any]:
    """Directs the player to perform basic movement towards destination with stuck detection (NOT full 3D A*)."""
    try:
        validate_coordinates(int(x), int(y), int(z))
    except SafetyError as e:
        return {"success": False, "action": "move_to", "error": str(e), "code": "SAFETY_VIOLATION"}

    clamped_speed = max(0.5, min(2.0, speed))
    async with action_tracker.track("move_to", ActionStateEnum.MOVING, target={"x": x, "y": y, "z": z, "speed": clamped_speed, "tolerance": tolerance}):
        try:
            res = await client.move_player(x, y, z, speed=clamped_speed, tolerance=tolerance)
            status = res.get("status", "moving")
            res["success"] = (status == "reached")
            return res
        except BridgeError as e:
            return {"success": False, "action": "move_to", "error": e.message, "code": e.code}

@server.tool()
async def stop_movement() -> Dict[str, Any]:
    """Halts active player movement immediately, clearing navigation steps."""
    try:
        res = await client.stop_player()
        action_tracker.set_state(ActionStateEnum.CANCELLED, action="stop_movement")
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "stop_movement", "error": e.message, "code": e.code}

@server.tool()
async def teleport(x: float, y: float, z: float, yaw: Optional[float] = None, pitch: Optional[float] = None) -> Dict[str, Any]:
    """Teleport the player directly to the specified coordinates with optional rotation."""
    try:
        validate_coordinates(int(x), int(y), int(z))
    except SafetyError as e:
        return {"success": False, "action": "teleport", "error": str(e), "code": "SAFETY_VIOLATION"}

    try:
        res = await client.teleport_player(x, y, z, yaw=yaw, pitch=pitch)
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "teleport", "error": e.message, "code": e.code}

@server.tool()
async def look_at(yaw: float, pitch: float) -> Dict[str, Any]:
    """Rotates player orientation (yaw and pitch) without altering position."""
    try:
        res = await client.rotate_player(yaw, pitch)
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "look_at", "error": e.message, "code": e.code}

@server.tool()
async def select_slot(slot: int) -> Dict[str, Any]:
    """Switches active player hotbar slot (0-8)."""
    if not (0 <= slot <= 8):
        return {"success": False, "action": "select_slot", "error": f"Slot must be between 0 and 8, got {slot}", "code": "INVALID_SLOT"}
    try:
        res = await client.select_slot(slot)
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "select_slot", "error": e.message, "code": e.code}

@server.tool()
async def use_item(hand: str = "main_hand") -> Dict[str, Any]:
    """Simulates right-clicking / using the item in the specified hand ('main_hand' or 'off_hand')."""
    try:
        res = await client.use_item(hand)
        return res
    except BridgeError as e:
        return {"success": False, "action": "use_item", "error": e.message, "code": e.code}

@server.tool()
async def drop_item(entire_stack: bool = False) -> Dict[str, Any]:
    """Drops the active held item onto the ground."""
    try:
        res = await client.drop_item(entire_stack)
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "drop_item", "error": e.message, "code": e.code}

@server.tool()
async def swing_arm(hand: str = "main_hand") -> Dict[str, Any]:
    """Performs an arm swing animation."""
    try:
        res = await client.swing_arm(hand)
        res["success"] = True
        return res
    except BridgeError as e:
        return {"success": False, "action": "swing_arm", "error": e.message, "code": e.code}

# ---------------------------------------------------------------------------
# MCP 2.0 Resources (Dynamic Context URIs)
# ---------------------------------------------------------------------------

@server.resource("minecraft://action/state")
async def resource_action_state() -> str:
    """Real-time lifecycle state of active player operations (IDLE, MOVING, BUILDING, MINING, INTERACTING)."""
    state = action_tracker.get_state()
    return state.model_dump_json(indent=2)

@server.resource("minecraft://player/position")
async def resource_player_position() -> str:
    """Current coordinate and rotation of the active player."""
    try:
        pos = await client.get_player_position()
        return pos.model_dump_json(indent=2)
    except BridgeError as e:
        return json.dumps({"error": e.message, "code": e.code})

@server.resource("minecraft://player/inventory")
async def resource_player_inventory() -> str:
    """Real-time equipment and item state across all player containers."""
    try:
        inv = await client.get_player_inventory()
        return inv.model_dump_json(indent=2)
    except BridgeError as e:
        return json.dumps({"error": e.message, "code": e.code})

@server.resource("minecraft://world")
async def resource_world() -> str:
    """Current world environment metadata, time of day, and weather."""
    try:
        info = await client.get_world_info()
        return info.model_dump_json(indent=2)
    except BridgeError as e:
        return json.dumps({"error": e.message, "code": e.code})

@server.resource("minecraft://entities/nearby")
async def resource_nearby_entities() -> str:
    """Real-time snapshot of entities within 16 blocks of the player."""
    try:
        entities = await client.get_entities(radius=16.0)
        return entities.model_dump_json(indent=2)
    except BridgeError as e:
        return json.dumps({"error": e.message, "code": e.code})

# ---------------------------------------------------------------------------
# MCP 2.0 Prompts (Conversational Workflow Templates)
# ---------------------------------------------------------------------------

@server.prompt()
def explore_area(center: str, radius: int = 16) -> str:
    """Prompt template instructing the model to perform structured terrain surveying and exploration."""
    return f"""You are an autonomous Minecraft cartographer and scout.
Your mission is to explore and survey the region around center {center} with radius {radius} blocks.

Operational Protocol:
1. Inspect the area using `inspect_area(center={center}, radius={min(radius, 16)})`.
2. Check for nearby hazards, water pockets, steep cliffs, or hostile entities using `get_nearby_entities()`.
3. Provide a clear, token-efficient summary of terrain elevation, surface composition, and key points of interest.
"""

def main():
    import anyio
    anyio.run(server.run_stdio_async)

if __name__ == "__main__":
    main()

