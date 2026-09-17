import math
from typing import Dict, Any, List, Optional, Tuple
from minecraft_mcp.client.bridge import BridgeClient, BridgeError
from minecraft_mcp.spatial.world_model import SpatialWorldModelManager

HAZARDOUS_BLOCKS = {
    "minecraft:lava",
    "minecraft:fire",
    "minecraft:soul_fire",
    "minecraft:magma_block",
    "minecraft:cactus",
}

WATER_BLOCKS = {
    "minecraft:water",
    "minecraft:flowing_water",
}

PASSABLE_VEGETATION = {
    "minecraft:air",
    "minecraft:cave_air",
    "minecraft:short_grass",
    "minecraft:tall_grass",
    "minecraft:fern",
    "minecraft:large_fern",
    "minecraft:dandelion",
    "minecraft:poppy",
    "minecraft:blue_orchid",
    "minecraft:allium",
    "minecraft:azure_bluet",
    "minecraft:red_tulip",
    "minecraft:orange_tulip",
    "minecraft:white_tulip",
    "minecraft:pink_tulip",
    "minecraft:oxeye_daisy",
    "minecraft:cornflower",
    "minecraft:lily_of_the_valley",
    "minecraft:dead_bush",
}

class SiteSelector:
    """
    Evaluates terrain around a center point to discover optimal building footprints.
    Analyzes height variance (flatness), surface stability, and clearance requirements.
    """

    def __init__(self, bridge_client: Optional[BridgeClient] = None):
        self.client = bridge_client or BridgeClient()

    async def find_build_location(
        self,
        center: Dict[str, float],
        radius: int = 24,
        width: int = 9,
        depth: int = 9,
        flatness_threshold: float = 0.7,
        player_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scans surrounding terrain within radius and identifies the best build site
        for a footprint of (width x depth).
        """
        cx = int(round(center.get("x", 0.0)))
        cy = int(round(center.get("y", 64.0)))
        cz = int(round(center.get("z", 0.0)))

        # Constrain scan radius and vertical span to stay comfortably under 32,768 blocks limit
        scan_radius = min(max(radius, 8), 24)
        # Vertical window: cy - 6 to cy + 6 (13 layers)
        # Max volume: (2 * scan_radius + 1)^2 * 13 => for r=24: 49*49*13 = 31,213 <= 32,768
        min_y = max(-64, cy - 6)
        max_y = min(320, cy + 6)
        min_x = cx - scan_radius
        max_x = cx + scan_radius
        min_z = cz - scan_radius
        max_z = cz + scan_radius

        try:
            area_data = await self.client.get_blocks(
                min_x=min_x,
                min_y=min_y,
                min_z=min_z,
                max_x=max_x,
                max_y=max_y,
                max_z=max_z,
                include_air=False,
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to scan terrain: {str(e)}",
                "center": {"x": cx, "y": cy, "z": cz},
            }

        # Build solid height map: (x, z) -> highest solid block y and its block_id
        # Also track hazardous blocks
        height_map: Dict[Tuple[int, int], Tuple[int, str]] = {}
        hazard_map: Dict[Tuple[int, int], str] = {}

        for b in area_data.blocks:
            bx, by, bz = b.pos["x"], b.pos["y"], b.pos["z"]
            bid = b.id.lower()

            if bid in HAZARDOUS_BLOCKS or bid in WATER_BLOCKS:
                hazard_map[(bx, bz)] = bid

            # Check if block is solid ground (not passable vegetation/air)
            if bid not in PASSABLE_VEGETATION and bid not in HAZARDOUS_BLOCKS and bid not in WATER_BLOCKS:
                if (bx, bz) not in height_map or by > height_map[(bx, bz)][0]:
                    height_map[(bx, bz)] = (by, bid)

        # Record explored area in world model
        world_model = SpatialWorldModelManager.get_instance()
        world_model.record_explored_area([cx, cy, cz], scan_radius, area_data.count)

        # Evaluate candidate origins (ox, oz)
        # Candidate origins step by 2 blocks for performance across the search radius
        step = 2
        candidates: List[Dict[str, Any]] = []

        for ox in range(min_x + 1, max_x - width, step):
            for oz in range(min_z + 1, max_z - depth, step):
                # Check all columns within footprint
                heights: List[int] = []
                materials: Dict[str, int] = {}
                has_hazard = False

                for fx in range(ox, ox + width):
                    for fz in range(oz, oz + depth):
                        if (fx, fz) in hazard_map:
                            has_hazard = True
                            break
                        if (fx, fz) in height_map:
                            h, mat = height_map[(fx, fz)]
                            heights.append(h)
                            materials[mat] = materials.get(mat, 0) + 1
                    if has_hazard:
                        break

                if has_hazard or len(heights) < (width * depth * 0.75):
                    # Incomplete ground data or hazard present
                    continue

                min_h = min(heights)
                max_h = max(heights)
                delta_h = max_h - min_h
                avg_h = sum(heights) / len(heights)
                target_base_y = int(round(avg_h)) + 1  # Build on top of ground

                # Flatness score: 1.0 for completely flat, drops with height variation
                variance = sum((h - avg_h) ** 2 for h in heights) / len(heights)
                flatness_score = 1.0 / (1.0 + (delta_h * 0.6) + (variance * 0.4))

                # Clearance blocks needed: blocks above target_base_y - 1 that would need excavation
                clearance_count = 0
                for fx in range(ox, ox + width):
                    for fz in range(oz, oz + depth):
                        if (fx, fz) in height_map:
                            h, _ = height_map[(fx, fz)]
                            if h >= target_base_y:
                                clearance_count += (h - target_base_y + 1)

                # Distance from anchor (center)
                center_site_x = ox + width / 2.0
                center_site_z = oz + depth / 2.0
                dist_to_player = math.sqrt((center_site_x - cx) ** 2 + (center_site_z - cz) ** 2)
                proximity_score = 1.0 / (1.0 + (dist_to_player * 0.05))

                # Composite score: heavily favor flatness, then proximity, penalize clearance
                clearance_penalty = min(1.0, clearance_count / (width * depth * 2.0))
                composite_score = (flatness_score * 0.65) + (proximity_score * 0.25) - (clearance_penalty * 0.10)

                primary_mat = max(materials.items(), key=lambda item: item[1])[0] if materials else "minecraft:dirt"

                candidate = {
                    "location": {"x": ox, "y": target_base_y, "z": oz},
                    "dimensions": {"width": width, "depth": depth},
                    "flatness_score": round(flatness_score, 3),
                    "height_variance": delta_h,
                    "clearance_blocks_needed": clearance_count,
                    "surface_material": primary_mat,
                    "distance": round(dist_to_player, 1),
                    "composite_score": round(composite_score, 3),
                }
                candidates.append(candidate)

        if not candidates:
            return {
                "success": False,
                "message": f"No suitable build sites found within radius {radius} (terrain may be obstructed or mostly water/void)",
                "center": {"x": cx, "y": cy, "z": cz},
            }

        # Sort descending by composite score
        candidates.sort(key=lambda c: c["composite_score"], reverse=True)
        best = candidates[0]

        # Record best region in spatial world model
        world_model.record_region(
            min_pos={"x": best["location"]["x"], "y": best["location"]["y"], "z": best["location"]["z"]},
            max_pos={"x": best["location"]["x"] + width - 1, "y": best["location"]["y"] + 10, "z": best["location"]["z"] + depth - 1},
            surface_material=best["surface_material"],
            flatness=best["flatness_score"],
        )

        return {
            "success": True,
            "best_location": best["location"],
            "dimensions": best["dimensions"],
            "flatness_score": best["flatness_score"],
            "height_variance": best["height_variance"],
            "clearance_blocks_needed": best["clearance_blocks_needed"],
            "surface_material": best["surface_material"],
            "distance_from_anchor": best["distance"],
            "meets_threshold": best["flatness_score"] >= flatness_threshold,
            "candidates_evaluated": len(candidates),
            "top_candidates": candidates[:5],
        }

