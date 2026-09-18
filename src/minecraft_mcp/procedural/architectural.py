"""
High-Level Architectural Primitives for Minecraft Procedural Construction.
Compiles arches, classical columns, domes, vaults, balconies, and staircases into Geometry IR / VoxelSpace.
"""

import math
from typing import TYPE_CHECKING
from minecraft_mcp.procedural.ir import (
    GeometryNode,
    ArchNode,
    ColumnNode,
    DomeNode,
    VaultNode,
    BalconyNode,
    StaircaseNode,
    BoxNode,
    CylinderNode,
    SphereNode,
    EllipsoidNode,
    ArcNode,
    CSGSubtractNode,
    CSGUnionNode,
)
from minecraft_mcp.procedural.voxel_space import VoxelSpace

if TYPE_CHECKING:
    from minecraft_mcp.procedural.rasterizer import GeometryRasterizer

def rasterize_architectural_primitive(node: GeometryNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Dispatches architectural primitive nodes to their procedural builder."""
    if isinstance(node, ArchNode):
        return build_arch(node, rasterizer)
    elif isinstance(node, ColumnNode):
        return build_column(node, rasterizer)
    elif isinstance(node, DomeNode):
        return build_dome(node, rasterizer)
    elif isinstance(node, VaultNode):
        return build_vault(node, rasterizer)
    elif isinstance(node, BalconyNode):
        return build_balcony(node, rasterizer)
    elif isinstance(node, StaircaseNode):
        return build_staircase(node, rasterizer)
    else:
        raise ValueError(f"Unsupported architectural node type: {type(node)}")

def build_arch(node: ArchNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a parametric architectural arch (Roman round, Gothic pointed, or Islamic horseshoe)."""
    space = VoxelSpace()
    w = max(4, node.width)
    h = max(4, node.height)
    d = max(1, node.depth)
    mat = node.material
    pier_mat = node.pillar_material or mat

    half_w = w // 2
    inner_half_w = max(1, half_w - 1)
    springing_h = max(2, h - half_w)  # Height where the curve begins

    # 1. Left and Right Vertical Piers
    for y in range(0, springing_h):
        for z in range(0, d):
            space.set_voxel(-half_w, y, z, pier_mat)
            space.set_voxel(half_w, y, z, pier_mat)

    # 2. Curving Arch Ring
    if node.style == "roman_round":
        radius = half_w
        for angle in range(0, 181, 2):
            rad = math.radians(angle)
            for z in range(0, d):
                # Arch voussoirs
                vx = int(round(-radius * math.cos(rad)))
                vy = int(round(springing_h + radius * math.sin(rad)))
                space.set_voxel(vx, vy, z, mat)

    elif node.style == "gothic_pointed":
        # Two intersecting circular arcs from opposing springing points
        r = w * 0.75
        for z in range(0, d):
            # Left arc curving right
            for angle in range(30, 91, 2):
                rad = math.radians(angle)
                vx = int(round(-half_w + r - r * math.cos(rad)))
                vy = int(round(springing_h + r * math.sin(rad) - (r * 0.5)))
                if vx <= 0 and vy <= h:
                    space.set_voxel(vx, vy, z, mat)
            # Right arc curving left
            for angle in range(30, 91, 2):
                rad = math.radians(angle)
                vx = int(round(half_w - r + r * math.cos(rad)))
                vy = int(round(springing_h + r * math.sin(rad) - (r * 0.5)))
                if vx >= 0 and vy <= h:
                    space.set_voxel(vx, vy, z, mat)

    elif node.style == "islamic_horseshoe":
        # Curve extends beyond 180 degrees
        radius = half_w
        for angle in range(-15, 196, 2):
            rad = math.radians(angle)
            for z in range(0, d):
                vx = int(round(-radius * math.cos(rad)))
                vy = int(round(springing_h + radius * math.sin(rad)))
                space.set_voxel(vx, vy, z, mat)

    else:  # Segmental
        radius = half_w * 1.4
        offset_y = radius * 0.5
        for angle in range(45, 136, 2):
            rad = math.radians(angle)
            for z in range(0, d):
                vx = int(round(-radius * math.cos(rad)))
                vy = int(round(springing_h - offset_y + radius * math.sin(rad)))
                space.set_voxel(vx, vy, z, mat)

    # 3. Keystone at Arch Apex
    if node.keystone:
        top_y = springing_h + half_w
        for z in range(0, d):
            space.set_voxel(0, top_y, z, "minecraft:chiseled_sandstone" if "sandstone" in mat else "minecraft:chiseled_stone_bricks")

    return space

def build_column(node: ColumnNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a classical order column with base plinth, cylindrical shaft, and capital."""
    space = VoxelSpace()
    r = max(0.5, node.radius)
    h = max(3, node.height)
    mat = node.material
    base_mat = node.base_material or mat
    cap_mat = node.capital_material or mat

    base_h = 1 if node.base else 0
    cap_h = 1 if node.capital else 0
    shaft_h = max(1, h - base_h - cap_h)

    # 1. Base Plinth
    if node.base:
        base_r = int(math.ceil(r + 0.5))
        for dx in range(-base_r, base_r + 1):
            for dz in range(-base_r, base_r + 1):
                space.set_voxel(dx, 0, dz, base_mat)

    # 2. Shaft
    start_y = base_h
    r_ceil = int(math.ceil(r))
    r_sq = r * r
    for y in range(start_y, start_y + shaft_h):
        for dx in range(-r_ceil, r_ceil + 1):
            for dz in range(-r_ceil, r_ceil + 1):
                d_sq = dx * dx + dz * dz
                if d_sq <= r_sq + 0.25:
                    if node.fluted:
                        # Fluted grooves on cardinal / diagonal cuts
                        ang = math.atan2(dz, dx)
                        if abs(math.sin(ang * 4)) > 0.9 and d_sq > (r * 0.7) ** 2:
                            continue
                    space.set_voxel(dx, y, dz, mat)

    # 3. Capital Plinth
    if node.capital:
        cap_y = start_y + shaft_h
        cap_r = int(math.ceil(r + 0.5))
        for dx in range(-cap_r, cap_r + 1):
            for dz in range(-cap_r, cap_r + 1):
                space.set_voxel(dx, cap_y, dz, cap_mat)

    return space

def build_dome(node: DomeNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a parametric architectural dome (hemispherical, onion, or coffered)."""
    space = VoxelSpace()
    r = max(3.0, node.radius)
    h = node.height or r
    mat = node.material
    r_ceil = int(math.ceil(r))

    if node.style == "onion":
        # Tapered bulbous onion dome (Taj Mahal style)
        steps = int(round(h * 1.5))
        for y in range(steps):
            t = y / float(steps)
            if t < 0.4:
                # Bulge outward
                curr_r = r * (0.85 + 0.35 * math.sin(t / 0.4 * (math.pi / 2)))
            else:
                # Taper to point
                decay = (t - 0.4) / 0.6
                curr_r = r * 1.2 * math.cos(decay * (math.pi / 2))

            curr_r = max(0.5, curr_r)
            cr_ceil = int(math.ceil(curr_r))
            cr_sq = curr_r * curr_r
            inner_sq = max(0.0, curr_r - 1.0) ** 2

            for dx in range(-cr_ceil, cr_ceil + 1):
                for dz in range(-cr_ceil, cr_ceil + 1):
                    d_sq = dx * dx + dz * dz
                    if inner_sq <= d_sq <= cr_sq + 0.25:
                        space.set_voxel(dx, y, dz, mat)

        if node.finial:
            for fy in range(steps, steps + 4):
                space.set_voxel(0, fy, 0, node.finial_material)

    else:
        # Standard hemispherical or saucer dome
        h_ceil = int(math.ceil(h))
        for y in range(h_ceil + 1):
            t = y / float(h)
            curr_r = r * math.sqrt(max(0.0, 1.0 - t * t))
            cr_ceil = int(math.ceil(curr_r))
            cr_sq = curr_r * curr_r
            inner_sq = max(0.0, curr_r - 1.0) ** 2

            # Oculus check
            if node.oculus and y == h_ceil:
                continue

            for dx in range(-cr_ceil, cr_ceil + 1):
                for dz in range(-cr_ceil, cr_ceil + 1):
                    d_sq = dx * dx + dz * dz
                    if inner_sq <= d_sq <= cr_sq + 0.25:
                        space.set_voxel(dx, y, dz, mat)

        if node.finial and not node.oculus:
            space.set_voxel(0, h_ceil + 1, 0, node.finial_material)

    return space

def build_vault(node: VaultNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a barrel or groin vault ceiling."""
    space = VoxelSpace()
    w = max(4, node.width)
    d = max(4, node.depth)
    h = max(3, node.height)
    mat = node.material
    half_w = w // 2

    if node.style == "barrel":
        # Continuous cylindrical arch along depth axis
        for z in range(d):
            for angle in range(0, 181, 3):
                rad = math.radians(angle)
                vx = int(round(-half_w * math.cos(rad)))
                vy = int(round(h * math.sin(rad)))
                space.set_voxel(vx, vy, z, mat)

    elif node.style == "groin":
        # Two intersecting barrel vaults
        half_d = d // 2
        for x in range(-half_w, half_w + 1):
            for z in range(-half_d, half_d + 1):
                # Diagonal rib lines and ceiling profile
                tx = abs(x) / float(half_w)
                tz = abs(z) / float(half_d)
                vy = int(round(h * math.sqrt(max(0.0, 1.0 - max(tx, tz) ** 2))))
                space.set_voxel(x, vy, z, mat)

    return space

def build_balcony(node: BalconyNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a projecting cantilevered balcony with corbels and railing."""
    space = VoxelSpace()
    w = node.width
    d = node.depth
    mat = node.material
    corbel_mat = node.corbel_material or mat
    half_w = w // 2

    # 1. Floor Slab at Y=0
    for x in range(-half_w, half_w + 1):
        for z in range(0, d + 1):
            space.set_voxel(x, 0, z, mat)

    # 2. Corbel Brackets at Y=-1 and Y=-2
    for x in [-half_w, 0, half_w]:
        space.set_voxel(x, -1, d // 2, corbel_mat)
        space.set_voxel(x, -2, 1, corbel_mat)

    # 3. Perimeter Railing at Y=1
    railing = node.railing_material
    for x in range(-half_w, half_w + 1):
        space.set_voxel(x, 1, d, railing)  # Front railing
    for z in range(0, d):
        space.set_voxel(-half_w, 1, z, railing)  # Left railing
        space.set_voxel(half_w, 1, z, railing)   # Right railing

    return space

def build_staircase(node: StaircaseNode, rasterizer: "GeometryRasterizer") -> VoxelSpace:
    """Builds a continuous spiral staircase rising around a central column."""
    space = VoxelSpace()
    r = max(2.0, node.radius)
    h = node.height
    step_mat = node.step_material
    core_mat = node.central_pillar_material

    # 1. Central Support Pillar
    for y in range(h):
        space.set_voxel(0, y, 0, core_mat)

    # 2. Spiral Steps
    # Rotate 45 degrees per 1 block of vertical rise
    for y in range(h):
        angle = y * 45.0
        rad = math.radians(angle)
        for dist in range(1, int(round(r)) + 1):
            sx = int(round(dist * math.cos(rad)))
            sz = int(round(dist * math.sin(rad)))
            space.set_voxel(sx, y, sz, step_mat)

    return space

