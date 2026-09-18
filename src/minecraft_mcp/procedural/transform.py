"""
Affine transformation engine for procedural Minecraft geometry.
Handles 3D translations, Euler rotations, scaling, mirroring, and voxel space transformation.
"""

import math
from typing import Tuple, Optional, Dict
from minecraft_mcp.procedural.ir import TransformSpec
from minecraft_mcp.procedural.voxel_space import VoxelSpace

def rotate_point_yaw(x: float, y: float, z: float, angle_deg: float) -> Tuple[float, float, float]:
    """Rotates a point around the vertical Y axis (yaw)."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    nx = x * cos_a - z * sin_a
    nz = x * sin_a + z * cos_a
    return nx, y, nz

def rotate_point_pitch(x: float, y: float, z: float, angle_deg: float) -> Tuple[float, float, float]:
    """Rotates a point around the horizontal X axis (pitch)."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    ny = y * cos_a - z * sin_a
    nz = y * sin_a + z * cos_a
    return x, ny, nz

def rotate_point_roll(x: float, y: float, z: float, angle_deg: float) -> Tuple[float, float, float]:
    """Rotates a point around the longitudinal Z axis (roll)."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    nx = x * cos_a - y * sin_a
    ny = x * sin_a + y * cos_a
    return nx, ny, z

def transform_point(
    x: float, y: float, z: float,
    transform: TransformSpec,
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
) -> Tuple[float, float, float]:
    """Applies a composite TransformSpec (Scale -> Mirror -> Rotate -> Translate) to a point relative to center."""
    cx, cy, cz = center
    # 1. Shift to local origin
    px = x - cx
    py = y - cy
    pz = z - cz

    # 2. Scale
    if transform.scale:
        px *= transform.scale[0]
        py *= transform.scale[1]
        pz *= transform.scale[2]

    # 3. Mirror
    if transform.mirror == "X":
        px = -px
    elif transform.mirror == "Y":
        py = -py
    elif transform.mirror == "Z":
        pz = -pz

    # 4. Rotation (Yaw -> Pitch -> Roll)
    if transform.rotation_y != 0.0:
        px, py, pz = rotate_point_yaw(px, py, pz, transform.rotation_y)
    if transform.rotation_x != 0.0:
        px, py, pz = rotate_point_pitch(px, py, pz, transform.rotation_x)
    if transform.rotation_z != 0.0:
        px, py, pz = rotate_point_roll(px, py, pz, transform.rotation_z)

    # 5. Shift back and apply translation
    tx, ty, tz = transform.translation
    final_x = px + cx + tx
    final_y = py + cy + ty
    final_z = pz + cz + tz
    return final_x, final_y, final_z

def remap_block_facing(block: str, rotation_y_deg: float) -> str:
    """Remaps facing property on directional blocks (e.g. stairs, doors) when rotated around Y."""
    rot = int(round(rotation_y_deg)) % 360
    if rot < 0:
        rot += 360

    if rot not in (90, 180, 270) or "facing=" not in block:
        return block

    facings = ["north", "east", "south", "west"]
    for i, f in enumerate(facings):
        if f"facing={f}" in block:
            shift = rot // 90
            new_facing = facings[(i + shift) % 4]
            return block.replace(f"facing={f}", f"facing={new_facing}")
    return block

def transform_voxel_space(space: VoxelSpace, transform: TransformSpec, center: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> VoxelSpace:
    """Transforms all voxels in a VoxelSpace according to a TransformSpec."""
    result = VoxelSpace()
    for (x, y, z), block in space.get_voxels_dict().items():
        tx, ty, tz = transform_point(float(x), float(y), float(z), transform, center)
        remapped_block = remap_block_facing(block, transform.rotation_y)
        result.set_voxel(int(round(tx)), int(round(ty)), int(round(tz)), remapped_block)
    return result

