"""
3D Discrete Voxel Space representation for procedural construction.
Manages spatial storage, CSG voxel operations, material histograms, and integrity checksums.
"""

import hashlib
from typing import Dict, Tuple, Optional, Any, List, Set

class VoxelSpace:
    """In-memory 3D discrete voxel workspace."""

    def __init__(self):
        # Maps (x, y, z) -> block_state_string
        self._voxels: Dict[Tuple[int, int, int], str] = {}

    def set_voxel(self, x: int, y: int, z: int, block: str, overwrite: bool = True) -> None:
        pos = (int(round(x)), int(round(y)), int(round(z)))
        if not overwrite and pos in self._voxels:
            return
        # Remap legacy block IDs to 26.2 registry names
        if block == "minecraft:chain" or block.startswith("minecraft:chain["):
            block = block.replace("minecraft:chain", "minecraft:iron_chain", 1)
        elif block == "chain" or block.startswith("chain["):
            block = block.replace("chain", "minecraft:iron_chain", 1)
        self._voxels[pos] = block

    def get_voxel(self, x: int, y: int, z: int) -> Optional[str]:
        return self._voxels.get((int(round(x)), int(round(y)), int(round(z))))

    def delete_voxel(self, x: int, y: int, z: int) -> bool:
        pos = (int(round(x)), int(round(y)), int(round(z)))
        if pos in self._voxels:
            del self._voxels[pos]
            return True
        return False

    def clear(self) -> None:
        self._voxels.clear()

    @property
    def count(self) -> int:
        return len(self._voxels)

    def is_empty(self) -> bool:
        return len(self._voxels) == 0

    def get_positions(self) -> Set[Tuple[int, int, int]]:
        return set(self._voxels.keys())

    def get_voxels_dict(self) -> Dict[Tuple[int, int, int], str]:
        return self._voxels.copy()

    def get_bounds(self) -> Dict[str, Dict[str, int]]:
        if not self._voxels:
            return {
                "min": {"x": 0, "y": 0, "z": 0},
                "max": {"x": 0, "y": 0, "z": 0},
            }
        xs = [p[0] for p in self._voxels.keys()]
        ys = [p[1] for p in self._voxels.keys()]
        zs = [p[2] for p in self._voxels.keys()]
        return {
            "min": {"x": min(xs), "y": min(ys), "z": min(zs)},
            "max": {"x": max(xs), "y": max(ys), "z": max(zs)},
        }

    def material_histogram(self) -> Dict[str, int]:
        histogram: Dict[str, int] = {}
        for block in self._voxels.values():
            histogram[block] = histogram.get(block, 0) + 1
        return histogram

    def compute_checksum(self) -> str:
        """Deterministic SHA256 integrity checksum of all voxel coordinates and materials."""
        if not self._voxels:
            return "00000000"
        hasher = hashlib.sha256()
        for pos in sorted(self._voxels.keys()):
            entry = f"{pos[0]},{pos[1]},{pos[2]}:{self._voxels[pos]}\n"
            hasher.update(entry.encode("utf-8"))
        return hasher.hexdigest()[:16]

    def clone(self) -> "VoxelSpace":
        new_space = VoxelSpace()
        new_space._voxels = self._voxels.copy()
        return new_space

    def merge(self, other: "VoxelSpace", offset: Tuple[int, int, int] = (0, 0, 0), overwrite: bool = True) -> None:
        """Union operation: Merges another VoxelSpace with coordinate offset."""
        dx, dy, dz = offset
        for (x, y, z), block in other._voxels.items():
            target_pos = (x + dx, y + dy, z + dz)
            if overwrite or target_pos not in self._voxels:
                self._voxels[target_pos] = block

    def subtract(self, subtrahend: "VoxelSpace", offset: Tuple[int, int, int] = (0, 0, 0)) -> int:
        """CSG Subtract: Carves out all coordinates in subtrahend from this VoxelSpace."""
        dx, dy, dz = offset
        carved_count = 0
        for x, y, z in subtrahend._voxels.keys():
            target_pos = (x + dx, y + dy, z + dz)
            if target_pos in self._voxels:
                del self._voxels[target_pos]
                carved_count += 1
        return carved_count

    def intersect(self, other: "VoxelSpace", offset: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """CSG Intersect: Keeps only coordinates that exist in both spaces."""
        dx, dy, dz = offset
        other_coords = {(x + dx, y + dy, z + dz) for x, y, z in other._voxels.keys()}
        to_delete = [pos for pos in self._voxels.keys() if pos not in other_coords]
        for pos in to_delete:
            del self._voxels[pos]

    def to_block_list(self, anchor: Tuple[int, int, int] = (0, 0, 0)) -> List[Dict[str, Any]]:
        """Converts voxels to a list of coordinate dictionaries relative to an anchor."""
        ax, ay, az = anchor
        result = []
        for (x, y, z), block in self._voxels.items():
            result.append({
                "x": x + ax,
                "y": y + ay,
                "z": z + az,
                "block": block,
            })
        return result

