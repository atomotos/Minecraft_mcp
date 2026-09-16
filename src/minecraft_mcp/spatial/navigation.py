import heapq
import math
from typing import Dict, Any, List, Optional, Tuple, Set
from minecraft_mcp.client.bridge import BridgeClient, BridgeError
from minecraft_mcp.spatial.world_model import SpatialWorldModelManager

PASSABLE_BLOCKS = {
    "minecraft:air",
    "minecraft:cave_air",
    "minecraft:void_air",
    "minecraft:short_grass",
    "minecraft:tall_grass",
    "minecraft:fern",
    "minecraft:large_fern",
    "minecraft:dandelion",
    "minecraft:poppy",
    "minecraft:torch",
    "minecraft:wall_torch",
    "minecraft:ladder",
    "minecraft:rail",
    "minecraft:powered_rail",
    "minecraft:lever",
    "minecraft:stone_button",
    "minecraft:oak_button",
    "minecraft:oak_sapling",
    "minecraft:spruce_sapling",
    "minecraft:birch_sapling",
    "minecraft:snow",
}

HAZARDS = {
    "minecraft:lava",
    "minecraft:fire",
    "minecraft:soul_fire",
    "minecraft:magma_block",
    "minecraft:sweet_berry_bush",
    "minecraft:wither_rose",
    "minecraft:powder_snow",
    "minecraft:cactus",
}

class NavigationManager:
    """
    Voxel-aware 3D A* pathfinding and waypoint locomotion controller.
    Evaluates solid footing, head/body clearance, 1-block steps up, and safe drops.
    """

    def __init__(self, bridge_client: Optional[BridgeClient] = None):
        self.client = bridge_client or BridgeClient()

    async def find_path(
        self,
        start: Tuple[int, int, int],
        goal: Tuple[int, int, int],
        max_iterations: int = 1500,
    ) -> Optional[List[Dict[str, int]]]:
        """
        Executes 3D A* search on the voxel grid between start and goal coordinates.
        Returns ordered list of integer block coordinates from start to goal.
        """
        sx, sy, sz = start
        gx, gy, gz = goal

        if (sx, sy, sz) == (gx, gy, gz):
            return [{"x": gx, "y": gy, "z": gz}]

        # Compute bounding box covering start and goal with padding
        pad_h = 6
        pad_v = 4
        min_x = min(sx, gx) - pad_h
        max_x = max(sx, gx) + pad_h
        min_y = max(-64, min(sy, gy) - pad_v)
        max_y = min(320, max(sy, gy) + pad_v)
        min_z = min(sz, gz) - pad_h
        max_z = max(sz, gz) + pad_h

        # Guard against volume > 32,768 limit
        vol = (max_x - min_x + 1) * (max_y - min_y + 1) * (max_z - min_z + 1)
        if vol > 32000:
            # Shrink padding if span is large
            pad_h = 3
            pad_v = 3
            min_x = min(sx, gx) - pad_h
            max_x = max(sx, gx) + pad_h
            min_y = max(-64, min(sy, gy) - pad_v)
            max_y = min(320, max(sy, gy) + pad_v)
            min_z = min(sz, gz) - pad_h
            max_z = max(sz, gz) + pad_h

        try:
            area = await self.client.get_blocks(
                min_x=min_x,
                min_y=min_y,
                min_z=min_z,
                max_x=max_x,
                max_y=max_y,
                max_z=max_z,
                include_air=False,
            )
        except Exception:
            return None

        # Build solid voxel set and hazard set
        solid_voxels: Set[Tuple[int, int, int]] = set()
        hazard_voxels: Set[Tuple[int, int, int]] = set()

        for b in area.blocks:
            bx, by, bz = b.pos["x"], b.pos["y"], b.pos["z"]
            bid = b.id.lower()
            if bid in HAZARDS:
                hazard_voxels.add((bx, by, bz))
            elif bid not in PASSABLE_BLOCKS:
                solid_voxels.add((bx, by, bz))

        def is_passable(pos: Tuple[int, int, int]) -> bool:
            return pos not in solid_voxels and pos not in hazard_voxels

        def is_walkable(x: int, y: int, z: int) -> bool:
            # Ground (y - 1) must be solid
            if (x, y - 1, z) not in solid_voxels:
                return False
            # Feet (y) and head (y + 1) must be passable
            if not is_passable((x, y, z)) or not is_passable((x, y + 1, z)):
                return False
            return True

        def heuristic(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
            # 3D Euclidean distance
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)

        # Priority queue stores (f_score, counter, current_node)
        counter = 0
        open_set: List[Tuple[float, int, Tuple[int, int, int]]] = []
        heapq.heappush(open_set, (heuristic(start, goal), counter, start))

        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        g_score: Dict[Tuple[int, int, int], float] = {start: 0.0}
        closed_set: Set[Tuple[int, int, int]] = set()

        iterations = 0
        closest_node = start
        closest_dist = heuristic(start, goal)

        while open_set and iterations < max_iterations:
            iterations += 1
            _, _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue
            closed_set.add(current)

            cx, cy, cz = current

            # Check if reached goal
            if current == goal or (abs(cx - gx) <= 1 and abs(cy - gy) <= 1 and abs(cz - gz) <= 1 and is_walkable(gx, gy, gz)):
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return [{"x": p[0], "y": p[1], "z": p[2]} for p in path]

            curr_dist = heuristic(current, goal)
            if curr_dist < closest_dist:
                closest_dist = curr_dist
                closest_node = current

            # Neighbors: 4 orthogonal directions
            for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, nz = cx + dx, cz + dz

                # 1. Level step (dy = 0)
                if is_walkable(nx, cy, nz):
                    cand = (nx, cy, nz)
                    step_cost = 1.0
                    tentative_g = g_score[current] + step_cost
                    if tentative_g < g_score.get(cand, float("inf")):
                        came_from[cand] = current
                        g_score[cand] = tentative_g
                        counter += 1
                        heapq.heappush(open_set, (tentative_g + heuristic(cand, goal), counter, cand))

                # 2. Step up (+1 jump)
                # Requires head clearance above current: (cx, cy + 2, cz) must be passable
                if is_passable((cx, cy + 2, cz)) and is_walkable(nx, cy + 1, nz):
                    cand = (nx, cy + 1, nz)
                    step_cost = 1.3
                    tentative_g = g_score[current] + step_cost
                    if tentative_g < g_score.get(cand, float("inf")):
                        came_from[cand] = current
                        g_score[cand] = tentative_g
                        counter += 1
                        heapq.heappush(open_set, (tentative_g + heuristic(cand, goal), counter, cand))

                # 3. Step down / safe drop (1 to 3 blocks)
                for drop in range(1, 4):
                    drop_y = cy - drop
                    if drop_y < min_y:
                        break
                    # Clearance for drop: air must be clear from cy down to drop_y + 1
                    clear_drop = all(is_passable((nx, y_check, nz)) for y_check in range(drop_y, cy + 1))
                    if clear_drop and is_walkable(nx, drop_y, nz):
                        cand = (nx, drop_y, nz)
                        step_cost = 1.0 + (drop * 0.2)
                        tentative_g = g_score[current] + step_cost
                        if tentative_g < g_score.get(cand, float("inf")):
                            came_from[cand] = current
                            g_score[cand] = tentative_g
                            counter += 1
                            heapq.heappush(open_set, (tentative_g + heuristic(cand, goal), counter, cand))
                        break  # Stop checking deeper drops once ground reached

        # If no complete path to goal, but made significant progress towards goal
        if closest_node != start and closest_dist < heuristic(start, goal) * 0.5:
            path = [closest_node]
            curr = closest_node
            while curr in came_from:
                curr = came_from[curr]
                path.append(curr)
            path.reverse()
            return [{"x": p[0], "y": p[1], "z": p[2]} for p in path]

        return None

    async def navigate_to(
        self,
        x: float,
        y: float,
        z: float,
        speed: float = 1.0,
        tolerance: float = 1.0,
        player: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculates a safe 3D route and moves the player towards the target destination.
        Uses A* pathfinding and Phase 2 locomotion primitives.
        """
        try:
            pos = await self.client.get_player_position(player)
            current_x, current_y, current_z = pos.x, pos.y, pos.z
        except Exception as e:
            return {"success": False, "error": f"Failed to get player position: {str(e)}"}

        dist_to_goal = math.sqrt((x - current_x) ** 2 + (y - current_y) ** 2 + (z - current_z) ** 2)
        if dist_to_goal <= tolerance:
            return {
                "success": True,
                "arrived": True,
                "message": "Player is already at destination within tolerance",
                "final_position": {"x": round(current_x, 2), "y": round(current_y, 2), "z": round(current_z, 2)},
                "distance": round(dist_to_goal, 2),
            }

        start_node = (int(round(current_x)), int(round(current_y)), int(round(current_z)))
        goal_node = (int(round(x)), int(round(y)), int(round(z)))

        # Find 3D A* path
        path = await self.find_path(start_node, goal_node)

        world_model = SpatialWorldModelManager.get_instance()

        if path and len(path) > 1:
            # Simplify path: pick waypoints every 3-4 blocks or at direction changes
            simplified_waypoints: List[Dict[str, float]] = []
            for i, node in enumerate(path):
                if i == 0:
                    continue
                if i == len(path) - 1 or i % 3 == 0:
                    simplified_waypoints.append({"x": float(node["x"]) + 0.5, "y": float(node["y"]), "z": float(node["z"]) + 0.5})

            # Traverse waypoints using move_player
            last_pos = {"x": current_x, "y": current_y, "z": current_z}
            stuck_detected = False

            for wp in simplified_waypoints:
                try:
                    move_res = await self.client.move_player(
                        x=wp["x"],
                        y=wp["y"],
                        z=wp["z"],
                        speed=speed,
                        tolerance=tolerance,
                        player=player,
                    )
                    if move_res.get("stuck", False):
                        stuck_detected = True
                        break
                    last_pos = move_res.get("currentPosition", wp)
                except Exception:
                    # If move_player fails, break
                    break

            # Update position in world model
            try:
                final_pos_obj = await self.client.get_player_position(player)
                final_pos = {"x": round(final_pos_obj.x, 2), "y": round(final_pos_obj.y, 2), "z": round(final_pos_obj.z, 2)}
            except Exception:
                final_pos = last_pos

            world_model.update_player_position(final_pos["x"], final_pos["y"], final_pos["z"])

            remaining_dist = math.sqrt((x - final_pos["x"]) ** 2 + (y - final_pos["y"]) ** 2 + (z - final_pos["z"]) ** 2)

            return {
                "success": True,
                "arrived": remaining_dist <= tolerance,
                "path_length": len(path),
                "waypoints_count": len(simplified_waypoints),
                "stuck_detected": stuck_detected,
                "final_position": final_pos,
                "remaining_distance": round(remaining_dist, 2),
            }
        else:
            # Fallback to direct move_player if A* could not compute detailed path (e.g. flat ground or close)
            try:
                move_res = await self.client.move_player(
                    x=x,
                    y=y,
                    z=z,
                    speed=speed,
                    tolerance=tolerance,
                    player=player,
                )
                final_pos = move_res.get("currentPosition", {"x": x, "y": y, "z": z})
                world_model.update_player_position(final_pos["x"], final_pos["y"], final_pos["z"])
                return {
                    "success": True,
                    "arrived": move_res.get("arrived", False),
                    "stuck_detected": move_res.get("stuck", False),
                    "final_position": final_pos,
                    "direct_locomotion": True,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Locomotion failed: {str(e)}",
                }
