"""
Voxel Compiler with 3D Greedy Cuboid Meshing for Minecraft Procedural Construction.
Decomposes arbitrary 3D voxel clouds into a minimal set of fill_region cuboids and sparse batches,
reducing bridge HTTP calls and tick latency by up to 95%.
"""

from typing import Dict, Any, List, Tuple, Set, Optional
from pydantic import BaseModel, Field
from minecraft_mcp.procedural.voxel_space import VoxelSpace

class CuboidFillOp(BaseModel):
    """Represents a bounded cuboid fill operation for the Fabric bridge."""
    from_pos: List[int]
    to_pos: List[int]
    block: str
    volume: int

class CompiledBuildPlan(BaseModel):
    """Optimized compilation plan ready for high-speed execution."""
    total_voxels: int
    fill_operations: List[CuboidFillOp] = Field(default_factory=list)
    sparse_placements: List[Dict[str, Any]] = Field(default_factory=list)
    materials_summary: Dict[str, int] = Field(default_factory=dict)
    bounds: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    integrity_checksum: str
    total_bridge_calls: int = 0
    compression_ratio: float = 1.0

class VoxelCompiler:
    """Compiles a VoxelSpace into an optimized sequence of fill_region and batched place_blocks operations."""

    def __init__(self, max_fill_volume: int = 500, max_sparse_batch: int = 500):
        self.max_fill_volume = max_fill_volume
        self.max_sparse_batch = max_sparse_batch

    def compile(self, space: VoxelSpace, anchor: Tuple[int, int, int] = (0, 0, 0)) -> CompiledBuildPlan:
        """Executes greedy cuboid meshing on space and returns a CompiledBuildPlan."""
        total_voxels = space.count
        if total_voxels == 0:
            return CompiledBuildPlan(
                total_voxels=0,
                integrity_checksum="00000000",
                total_bridge_calls=0,
                compression_ratio=1.0,
            )

        ax, ay, az = anchor
        voxels_dict = space.get_voxels_dict()

        # 1. Group coordinates by material
        material_coords: Dict[str, Set[Tuple[int, int, int]]] = {}
        for (x, y, z), mat in voxels_dict.items():
            if mat not in material_coords:
                material_coords[mat] = set()
            material_coords[mat].add((x, y, z))

        fill_ops: List[CuboidFillOp] = []
        sparse_voxels: List[Dict[str, Any]] = []

        # 2. Greedy Cuboid Meshing per material
        for mat, coords in material_coords.items():
            unvisited = coords.copy()

            while unvisited:
                # Pick seed with lowest Y, then Z, then X for deterministic builds
                seed = min(unvisited, key=lambda p: (p[1], p[2], p[0]))
                sx, sy, sz = seed

                # Expand along +X
                dx = 0
                while (sx + dx + 1, sy, sz) in unvisited:
                    dx += 1

                # Expand along +Z
                dz = 0
                while True:
                    next_z = sz + dz + 1
                    # Check if entire row (sx..sx+dx, sy, next_z) is unvisited
                    row_ok = all((sx + i, sy, next_z) in unvisited for i in range(dx + 1))
                    if row_ok:
                        dz += 1
                    else:
                        break

                # Expand along +Y
                dy = 0
                while True:
                    next_y = sy + dy + 1
                    # Check if entire rectangle (sx..sx+dx, next_y, sz..sz+dz) is unvisited
                    layer_ok = all(
                        (sx + ix, next_y, sz + iz) in unvisited
                        for ix in range(dx + 1)
                        for iz in range(dz + 1)
                    )
                    if layer_ok:
                        dy += 1
                    else:
                        break

                # Cuboid volume
                w = dx + 1
                h = dy + 1
                d = dz + 1
                vol = w * h * d

                # Mark all contained voxels as visited
                for ix in range(w):
                    for iy in range(h):
                        for iz in range(d):
                            unvisited.discard((sx + ix, sy + iy, sz + iz))

                # If volume is 1 or 2, treat as sparse block to avoid tiny fill overhead
                if vol <= 2:
                    for ix in range(w):
                        for iy in range(h):
                            for iz in range(d):
                                sparse_voxels.append({
                                    "x": sx + ix + ax,
                                    "y": sy + iy + ay,
                                    "z": sz + iz + az,
                                    "block": mat,
                                })
                else:
                    # If volume <= max_fill_volume, add as a single fill op
                    if vol <= self.max_fill_volume:
                        fill_ops.append(CuboidFillOp(
                            from_pos=[sx + ax, sy + ay, sz + az],
                            to_pos=[sx + dx + ax, sy + dy + ay, sz + dz + az],
                            block=mat,
                            volume=vol,
                        ))
                    else:
                        # Partition large cuboid into sub-cuboids <= max_fill_volume
                        sub_ops = self._partition_cuboid(
                            x1=sx + ax, y1=sy + ay, z1=sz + az,
                            x2=sx + dx + ax, y2=sy + dy + ay, z2=sz + dz + az,
                            block=mat
                        )
                        fill_ops.extend(sub_ops)

        # 3. Calculate metrics
        sparse_batches = (len(sparse_voxels) + self.max_sparse_batch - 1) // self.max_sparse_batch if sparse_voxels else 0
        total_calls = len(fill_ops) + sparse_batches
        comp_ratio = round(total_voxels / max(1, total_calls), 2)

        return CompiledBuildPlan(
            total_voxels=total_voxels,
            fill_operations=fill_ops,
            sparse_placements=sparse_voxels,
            materials_summary=space.material_histogram(),
            bounds=space.get_bounds(),
            integrity_checksum=space.compute_checksum(),
            total_bridge_calls=total_calls,
            compression_ratio=comp_ratio,
        )

    def _partition_cuboid(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> List[CuboidFillOp]:
        """Subdivides a large cuboid along its longest dimension so each sub-volume <= max_fill_volume."""
        sub_ops: List[CuboidFillOp] = []
        queue = [(x1, y1, z1, x2, y2, z2)]

        while queue:
            cx1, cy1, cz1, cx2, cy2, cz2 = queue.pop(0)
            w = cx2 - cx1 + 1
            h = cy2 - cy1 + 1
            d = cz2 - cz1 + 1
            vol = w * h * d

            if vol <= self.max_fill_volume:
                sub_ops.append(CuboidFillOp(
                    from_pos=[cx1, cy1, cz1],
                    to_pos=[cx2, cy2, cz2],
                    block=block,
                    volume=vol
                ))
            else:
                # Split along longest dimension
                if w >= h and w >= d:
                    mid_x = cx1 + (w // 2) - 1
                    queue.append((cx1, cy1, cz1, mid_x, cy2, cz2))
                    queue.append((mid_x + 1, cy1, cz1, cx2, cy2, cz2))
                elif h >= w and h >= d:
                    mid_y = cy1 + (h // 2) - 1
                    queue.append((cx1, cy1, cz1, cx2, mid_y, cz2))
                    queue.append((cx1, mid_y + 1, cz1, cx2, cy2, cz2))
                else:
                    mid_z = cz1 + (d // 2) - 1
                    queue.append((cx1, cy1, cz1, cx2, cy2, mid_z))
                    queue.append((cx1, cy1, mid_z + 1, cx2, cy2, cz2))

        return sub_ops

