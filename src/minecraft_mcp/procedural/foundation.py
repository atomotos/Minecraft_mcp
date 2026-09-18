"""
Terrain-Adaptive Foundation & Ground Anchoring Engine for Minecraft Procedural Construction.
Analyzes natural topography across a structure's bounding footprint, levels the base datum,
and generates solid sub-foundation underpinning down to natural bedrock/dirt to eliminate floating voids.
"""

from typing import Dict, Any, List, Tuple, Optional
import structlog
from minecraft_mcp.client.bridge import BridgeClient
from minecraft_mcp.procedural.voxel_space import VoxelSpace

logger = structlog.get_logger("minecraft_mcp.procedural.foundation")

class TerrainAdaptiveFoundationEngine:
    """Computes and constructs ground-anchored foundations and leveled site plinths."""

    def __init__(self, client: Optional[BridgeClient] = None):
        self.client = client

    async def profile_terrain_footprint(
        self,
        min_x: int, min_z: int,
        max_x: int, max_z: int,
        search_y_min: int = 50,
        search_y_max: int = 120
    ) -> Dict[Tuple[int, int], int]:
        """Queries the live Minecraft world to determine the highest solid ground level for every (x, z) column."""
        heightmap: Dict[Tuple[int, int], int] = {}
        if not self.client:
            # Fallback for offline / unit tests: flat default at search_y_min + 10
            default_ground = (search_y_min + search_y_max) // 2
            for x in range(min_x, max_x + 1):
                for z in range(min_z, max_z + 1):
                    heightmap[(x, z)] = default_ground
            return heightmap

        try:
            # Query block data across the bounding volume
            data = await self.client.get_blocks(
                min_x=min_x, min_y=search_y_min, min_z=min_z,
                max_x=max_x, max_y=search_y_max, max_z=max_z,
                include_air=False
            )
            # Find max solid Y per (x, z)
            for b in data.blocks:
                bx, by, bz = b.pos["x"], b.pos["y"], b.pos["z"]
                bid = b.id.lower()
                # Ignore non-solid vegetation like grass, leaves, flowers, air
                if any(veg in bid for veg in ["leaves", "flower", "tall_grass", "fern", "vine", "snow"]):
                    continue
                if (bx, bz) not in heightmap or by > heightmap[(bx, bz)]:
                    heightmap[(bx, bz)] = by

        except Exception as e:
            logger.warning("Could not probe live terrain heightmap, using default datum", error=str(e))

        # Fill any missing columns with median ground height
        all_vals = list(heightmap.values())
        median_y = sorted(all_vals)[len(all_vals) // 2] if all_vals else 64
        for x in range(min_x, max_x + 1):
            for z in range(min_z, max_z + 1):
                if (x, z) not in heightmap:
                    heightmap[(x, z)] = median_y

        return heightmap

    def generate_foundation_voxels(
        self,
        min_x: int, min_z: int,
        max_x: int, max_z: int,
        base_y: int,
        heightmap: Dict[Tuple[int, int], int],
        foundation_material: str = "minecraft:stone_bricks",
        plinth_material: Optional[str] = None,
        plinth_margin: int = 1,
        max_underpinning_depth: int = 16
    ) -> VoxelSpace:
        """Generates solid sub-foundation fill columns downward from base_y - 1 to ground height, plus a leveled plinth."""
        space = VoxelSpace()
        plinth_mat = plinth_material or foundation_material

        p_min_x = min_x - plinth_margin
        p_max_x = max_x + plinth_margin
        p_min_z = min_z - plinth_margin
        p_max_z = max_z + plinth_margin

        # 1. Leveled Plinth Terrace at base_y
        for x in range(p_min_x, p_max_x + 1):
            for z in range(p_min_z, p_max_z + 1):
                space.set_voxel(x, base_y, z, plinth_mat)

        # 2. Sub-Foundation Underpinning Columns Downwards to Solid Ground
        for x in range(p_min_x, p_max_x + 1):
            for z in range(p_min_z, p_max_z + 1):
                ground_y = heightmap.get((x, z), base_y - 1)
                # If terrain dips below the plinth, fill solid blocks down to ground
                if ground_y < base_y:
                    lowest_fill = max(ground_y, base_y - max_underpinning_depth)
                    for y in range(lowest_fill, base_y):
                        space.set_voxel(x, y, z, foundation_material)

        return space

    async def prepare_base_foundation(
        self,
        min_x: int, min_z: int,
        max_x: int, max_z: int,
        base_y: int,
        foundation_material: str = "minecraft:stone_bricks",
        plinth_material: Optional[str] = None,
        plinth_margin: int = 1,
        clear_envelope: bool = True,
        superstructure_height: int = 20
    ) -> VoxelSpace:
        """End-to-end foundation preparation: probes terrain, clears airspace, and returns anchored foundation voxels."""
        # 1. Probe local ground elevation
        heightmap = await self.profile_terrain_footprint(
            min_x=min_x - plinth_margin,
            min_z=min_z - plinth_margin,
            max_x=max_x + plinth_margin,
            max_z=max_z + plinth_margin,
            search_y_min=max(-64, base_y - 20),
            search_y_max=min(320, base_y + 10),
        )

        # 2. Optional: clear obstructing interior envelope in live world
        if clear_envelope and self.client:
            try:
                vol = (max_x - min_x + 1) * superstructure_height * (max_z - min_z + 1)
                if vol <= 500:
                    await self.client.fill_region(
                        min_x, base_y + 1, min_z,
                        max_x, min(319, base_y + superstructure_height), max_z,
                        "minecraft:air"
                    )
            except Exception as e:
                logger.warning("Envelope airspace clearing skipped or failed", error=str(e))

        # 3. Generate foundation and plinth voxels
        return self.generate_foundation_voxels(
            min_x=min_x, min_z=min_z,
            max_x=max_x, max_z=max_z,
            base_y=base_y,
            heightmap=heightmap,
            foundation_material=foundation_material,
            plinth_material=plinth_material,
            plinth_margin=plinth_margin,
        )

