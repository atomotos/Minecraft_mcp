from typing import Dict, Any, List, Tuple, Optional
import math

def build_floor_blocks(
    min_x: int, max_x: int,
    min_z: int, max_z: int,
    y: int,
    material: str
) -> List[Dict[str, Any]]:
    """Generates horizontal rectangular floor/ceiling slice."""
    blocks = []
    x1, x2 = min(min_x, max_x), max(min_x, max_x)
    z1, z2 = min(min_z, max_z), max(min_z, max_z)
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            blocks.append({"x": x, "y": y, "z": z, "block": material})
    return blocks

def build_pillar_blocks(
    x: int, z: int,
    base_y: int, height: int,
    material: str
) -> List[Dict[str, Any]]:
    """Generates vertical pillar column."""
    blocks = []
    for y in range(base_y, base_y + height):
        blocks.append({"x": x, "y": y, "z": z, "block": material})
    return blocks

def build_wall_blocks(
    start_x: int, start_z: int,
    end_x: int, end_z: int,
    base_y: int, height: int,
    thickness: int = 1,
    material: str = "minecraft:stone_bricks",
    crenellations: bool = False
) -> List[Dict[str, Any]]:
    """Generates a linear wall between two 2D points with optional thickness and battlements."""
    blocks = []
    dx = end_x - start_x
    dz = end_z - start_z
    steps = max(abs(dx), abs(dz))

    # Bresenham or axis sampling
    path_points: List[Tuple[int, int]] = []
    if steps == 0:
        path_points.append((start_x, start_z))
    else:
        for s in range(steps + 1):
            t = s / steps
            px = int(round(start_x + t * dx))
            pz = int(round(start_z + t * dz))
            if (px, pz) not in path_points:
                path_points.append((px, pz))

    # Normal offset for thickness > 1
    nx, nz = 0, 0
    if abs(dx) >= abs(dz):
        nz = 1
    else:
        nx = 1

    for px, pz in path_points:
        for th in range(thickness):
            wx = px + th * nx
            wz = pz + th * nz
            for y in range(base_y, base_y + height):
                blocks.append({"x": wx, "y": y, "z": wz, "block": material})

    if crenellations and path_points:
        top_y = base_y + height
        for i, (px, pz) in enumerate(path_points):
            if i % 2 == 0:
                for th in range(thickness):
                    blocks.append({"x": px + th * nx, "y": top_y, "z": pz + th * nz, "block": material})

    return blocks

def build_roof_blocks(
    min_x: int, max_x: int,
    min_z: int, max_z: int,
    base_y: int,
    style: str = "pitched",
    stair_material: str = "minecraft:oak_stairs",
    slab_material: str = "minecraft:oak_slab",
    overhang: int = 1
) -> List[Dict[str, Any]]:
    """Generates architectural roof structures: pitched (gable), hip (pyramid), or flat with parapet."""
    blocks = []
    x1 = min(min_x, max_x) - overhang
    x2 = max(min_x, max_x) + overhang
    z1 = min(min_z, max_z) - overhang
    z2 = max(min_z, max_z) + overhang

    width = x2 - x1 + 1
    depth = z2 - z1 + 1

    clean_stair = stair_material.split("[")[0]
    clean_slab = slab_material.split("[")[0]

    if style == "flat":
        # Flat roof slab
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                blocks.append({"x": x, "y": base_y, "z": z, "block": slab_material})
        # Parapet border
        for x in range(x1, x2 + 1):
            blocks.append({"x": x, "y": base_y + 1, "z": z1, "block": slab_material})
            blocks.append({"x": x, "y": base_y + 1, "z": z2, "block": slab_material})
        for z in range(z1 + 1, z2):
            blocks.append({"x": x1, "y": base_y + 1, "z": z, "block": slab_material})
            blocks.append({"x": x2, "y": base_y + 1, "z": z, "block": slab_material})

    elif style == "hip":
        # 4-way slope meeting in center
        layers = min(width, depth) // 2
        for layer in range(layers):
            cur_y = base_y + layer
            cx1, cx2 = x1 + layer, x2 - layer
            cz1, cz2 = z1 + layer, z2 - layer
            if cx1 > cx2 or cz1 > cz2:
                break
            # North and South slopes
            for x in range(cx1, cx2 + 1):
                blocks.append({"x": x, "y": cur_y, "z": cz1, "block": f"{clean_stair}[facing=south,half=bottom]"})
                blocks.append({"x": x, "y": cur_y, "z": cz2, "block": f"{clean_stair}[facing=north,half=bottom]"})
            # West and East slopes
            for z in range(cz1 + 1, cz2):
                blocks.append({"x": cx1, "y": cur_y, "z": z, "block": f"{clean_stair}[facing=east,half=bottom]"})
                blocks.append({"x": cx2, "y": cur_y, "z": z, "block": f"{clean_stair}[facing=west,half=bottom]"})

        # Apex cap
        final_y = base_y + layers
        ax1, ax2 = x1 + layers, x2 - layers
        az1, az2 = z1 + layers, z2 - layers
        for x in range(min(ax1, ax2), max(ax1, ax2) + 1):
            for z in range(min(az1, az2), max(az1, az2) + 1):
                blocks.append({"x": x, "y": final_y, "z": z, "block": slab_material})

    else:
        # Pitched (Gable) along the shorter axis
        if width <= depth:
            # Slope along X axis, ridge runs along Z axis
            layers = width // 2
            for layer in range(layers):
                cur_y = base_y + layer
                lx = x1 + layer
                rx = x2 - layer
                for z in range(z1, z2 + 1):
                    blocks.append({"x": lx, "y": cur_y, "z": z, "block": f"{clean_stair}[facing=east,half=bottom]"})
                    blocks.append({"x": rx, "y": cur_y, "z": z, "block": f"{clean_stair}[facing=west,half=bottom]"})

            # Ridge cap
            apex_y = base_y + layers
            mid_x1 = x1 + layers
            mid_x2 = x2 - layers
            for mx in range(mid_x1, mid_x2 + 1):
                for z in range(z1, z2 + 1):
                    blocks.append({"x": mx, "y": apex_y, "z": z, "block": slab_material})
        else:
            # Slope along Z axis, ridge runs along X axis
            layers = depth // 2
            for layer in range(layers):
                cur_y = base_y + layer
                lz = z1 + layer
                rz = z2 - layer
                for x in range(x1, x2 + 1):
                    blocks.append({"x": x, "y": cur_y, "z": lz, "block": f"{clean_stair}[facing=south,half=bottom]"})
                    blocks.append({"x": x, "y": cur_y, "z": rz, "block": f"{clean_stair}[facing=north,half=bottom]"})

            # Ridge cap
            apex_y = base_y + layers
            mid_z1 = z1 + layers
            mid_z2 = z2 - layers
            for mz in range(mid_z1, mid_z2 + 1):
                for x in range(x1, x2 + 1):
                    blocks.append({"x": x, "y": apex_y, "z": mz, "block": slab_material})

    return blocks

def build_doorway_blocks(
    x: int, y: int, z: int,
    facing: str = "north",
    door_material: str = "minecraft:oak_door"
) -> List[Dict[str, Any]]:
    """Generates two door half blocks."""
    clean_door = door_material.split("[")[0]
    return [
        {"x": x, "y": y, "z": z, "block": f"{clean_door}[facing={facing},half=lower,hinge=left,open=false]"},
        {"x": x, "y": y + 1, "z": z, "block": f"{clean_door}[facing={facing},half=upper,hinge=left,open=false]"},
    ]

def build_window_blocks(
    start_x: int, y: int, start_z: int,
    width: int = 1, height: int = 1,
    glass_material: str = "minecraft:glass_pane",
    axis: str = "x"
) -> List[Dict[str, Any]]:
    """Generates window aperture blocks."""
    blocks = []
    for h in range(height):
        cy = y + h
        for w in range(width):
            if axis == "x":
                blocks.append({"x": start_x + w, "y": cy, "z": start_z, "block": glass_material})
            else:
                blocks.append({"x": start_x, "y": cy, "z": start_z + w, "block": glass_material})
    return blocks

