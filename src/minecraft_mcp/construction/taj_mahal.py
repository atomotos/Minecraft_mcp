"""
Taj Mahal Architectural Blueprint & Voxel Compiler
Generates the complete, mathematically symmetric Mughal architectural ensemble:
- Grand Plinth terrace & entrance staircase
- Four corner Minarets with multi-tiered balconies and cupolas
- Main chamfered octagonal Mausoleum with corner pillars
- Four Monumental Pishtaq (Iwan) arches with lapis & gold inlays
- Inner Cenotaph Chamber with dual memorials, jali screens, and chandelier
- Central cylindrical drum & bulbous Onion Dome (Amrud) with golden Kalash finial
- Four roof Chattris (pillared domed kiosks)
- Charbagh Reflecting Pool with submerged illumination and garden borders
"""

import math
from typing import Dict, Any, List, Tuple
from minecraft_mcp.models.construction import ConstructionStep
from minecraft_mcp.models.blueprint import (
    ArchitecturalBlueprint,
    BlueprintComponent,
    ComponentType,
    Dimensions,
    StructureType,
)

DEFAULT_TAJ_PALETTE = {
    "marble": "minecraft:smooth_quartz",
    "pillar": "minecraft:quartz_pillar",
    "stairs": "minecraft:quartz_stairs",
    "slab": "minecraft:quartz_slab",
    "chiseled": "minecraft:chiseled_quartz_block",
    "trim": "minecraft:smooth_quartz_slab",
    "accent_gold": "minecraft:gold_block",
    "accent_lapis": "minecraft:lapis_block",
    "inlay_floor": "minecraft:polished_blackstone",
    "railing": "minecraft:iron_bars",
    "water": "minecraft:water",
    "pool_light": "minecraft:sea_lantern",
    "pool_border": "minecraft:smooth_stone_slab",
    "garden_leaves": "minecraft:flowering_azalea_leaves[persistent=true]",
    "spire": "minecraft:lightning_rod",
    "lantern": "minecraft:lantern",
    "chain": "minecraft:iron_chain",
}

def create_taj_mahal_blueprint() -> ArchitecturalBlueprint:
    """Returns the ArchitecturalBlueprint model for the Taj Mahal."""
    return ArchitecturalBlueprint(
        id="taj_mahal",
        name="The Taj Mahal",
        structure_type=StructureType.MONUMENT,
        dimensions=Dimensions(width=29, depth=49, height=27),
        palette=DEFAULT_TAJ_PALETTE,
        description="Imperial Mughal monument featuring an elevated marble plinth, 4 minarets, central domed chamber with iwans, onion dome, and reflecting pool.",
        components=[
            BlueprintComponent(name="plinth_foundation", component_type=ComponentType.FOUNDATION, order=1, material_role="marble"),
            BlueprintComponent(name="minarets", component_type=ComponentType.PILLAR, order=2, material_role="marble"),
            BlueprintComponent(name="mausoleum_walls", component_type=ComponentType.WALL, order=3, material_role="marble"),
            BlueprintComponent(name="pishtaq_iwans", component_type=ComponentType.OPENING, order=4, material_role="chiseled"),
            BlueprintComponent(name="interior_chamber", component_type=ComponentType.INTERIOR, order=5, material_role="inlay_floor"),
            BlueprintComponent(name="roof_and_chattris", component_type=ComponentType.ROOF, order=6, material_role="pillar"),
            BlueprintComponent(name="central_onion_dome", component_type=ComponentType.ROOF, order=7, material_role="marble"),
            BlueprintComponent(name="reflecting_pool", component_type=ComponentType.CUSTOM, order=8, material_role="water"),
        ],
    )

def generate_taj_mahal_steps(
    anchor: Dict[str, int],
    palette_override: Dict[str, str] = None,
) -> List[ConstructionStep]:
    """
    Generates all sequenced ConstructionSteps for the Taj Mahal ensemble.
    Coordinates are relative to the anchor position:
    - ax, ay, az: Northwest corner of the main plinth
    - Facing: South (entrance and reflecting pool extend towards +Z)
    """
    palette = DEFAULT_TAJ_PALETTE.copy()
    if palette_override:
        palette.update(palette_override)

    ax = anchor["x"]
    ay = anchor["y"]
    az = anchor["z"]

    steps: List[ConstructionStep] = []

    m_marble = palette["marble"]
    m_pillar = palette["pillar"]
    m_stairs = palette["stairs"]
    m_slab = palette["slab"]
    m_chiseled = palette["chiseled"]
    m_gold = palette["accent_gold"]
    m_lapis = palette["accent_lapis"]
    m_blackstone = palette["inlay_floor"]
    m_bars = palette["railing"]
    m_water = palette["water"]
    m_sea_lantern = palette["pool_light"]
    m_pool_border = palette["pool_border"]
    m_leaves = palette["garden_leaves"]
    m_spire = palette["spire"]
    m_lantern = palette["lantern"]
    m_chain = palette["chain"]

    # =========================================================================
    # 1. GRAND PLINTH (29 x 29 Terrace) & ENTRANCE STEPS
    # =========================================================================
    comp = "plinth_foundation"
    pw, pd = 29, 29

    # Layer 0: Solid Sub-Base
    for x in range(ax, ax + pw):
        for z in range(az, az + pd):
            steps.append(ConstructionStep(x=x, y=ay, z=z, block=m_marble, component_name=comp))

    # Layer 1: Terrace Floor & Perimeter Chiseled Trim
    for x in range(ax, ax + pw):
        for z in range(az, az + pd):
            is_edge = (x == ax or x == ax + pw - 1 or z == az or z == az + pd - 1)
            b = m_chiseled if is_edge else m_marble
            steps.append(ConstructionStep(x=x, y=ay + 1, z=z, block=b, component_name=comp))

    # South Ceremonial Entrance Stairs (leading up from ground to terrace)
    # Width: 5 blocks (x: ax + 12 to ax + 16), at z = az + pd
    for x in range(ax + 12, ax + 17):
        steps.append(ConstructionStep(x=x, y=ay, z=az + pd, block=f"{m_stairs}[facing=north,half=bottom]", component_name=comp))
        steps.append(ConstructionStep(x=x, y=ay + 1, z=az + pd - 1, block=f"{m_stairs}[facing=north,half=bottom]", component_name=comp))

    # =========================================================================
    # 2. FOUR CORNER MINARETS (Height 25 blocks)
    # =========================================================================
    comp = "minarets"
    minaret_centers = [
        (ax + 3, az + 3),       # NW
        (ax + 25, az + 3),      # NE
        (ax + 3, az + 25),      # SW
        (ax + 25, az + 25),     # SE
    ]

    for cx, cz in minaret_centers:
        # Minaret Base (y: ay + 2 to ay + 4) - Octagonal 3x3
        for y in range(ay + 2, ay + 5):
            for dx in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if abs(dx) == 1 and abs(dz) == 1:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_chiseled, component_name=comp))
                    else:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_marble, component_name=comp))

        # Minaret Shaft (y: ay + 5 to ay + 21) - Slender column with pillar core
        for y in range(ay + 5, ay + 22):
            # Center core
            steps.append(ConstructionStep(x=cx, y=y, z=cz, block=m_pillar, component_name=comp))
            # Cross arms
            steps.append(ConstructionStep(x=cx + 1, y=y, z=cz, block=m_marble, component_name=comp))
            steps.append(ConstructionStep(x=cx - 1, y=y, z=cz, block=m_marble, component_name=comp))
            steps.append(ConstructionStep(x=cx, y=y, z=cz + 1, block=m_marble, component_name=comp))
            steps.append(ConstructionStep(x=cx, y=y, z=cz - 1, block=m_marble, component_name=comp))

            # Tier 1 Balcony at y = ay + 11
            if y == ay + 11:
                for dx in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if abs(dx) == 1 and abs(dz) == 1:
                            steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))
                # Railings around balcony
                for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    steps.append(ConstructionStep(x=cx + dx, y=y + 1, z=cz + dz, block=m_bars, component_name=comp))

            # Tier 2 Balcony at y = ay + 17
            if y == ay + 17:
                for dx in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if abs(dx) == 1 and abs(dz) == 1:
                            steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))
                for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    steps.append(ConstructionStep(x=cx + dx, y=y + 1, z=cz + dz, block=m_bars, component_name=comp))

        # Upper Balcony Platform (y = ay + 22)
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                steps.append(ConstructionStep(x=cx + dx, y=ay + 22, z=cz + dz, block=m_chiseled, component_name=comp))

        # Cupola Columns (y: ay + 23 to ay + 24)
        for y in range(ay + 23, ay + 25):
            for dx, dz in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_pillar, component_name=comp))
            # Open air inside cupola

        # Cupola Roof & Finial (y: ay + 25 to ay + 27)
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                steps.append(ConstructionStep(x=cx + dx, y=ay + 25, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))
        steps.append(ConstructionStep(x=cx, y=ay + 26, z=cz, block=m_gold, component_name=comp))
        steps.append(ConstructionStep(x=cx, y=ay + 27, z=cz, block=m_spire, component_name=comp))

    # =========================================================================
    # 3. CENTRAL MAUSOLEUM (17x17 Chamfered Octagonal Tomb)
    # =========================================================================
    comp = "mausoleum_walls"
    # Centered: from x = ax + 6 to ax + 22, z = az + 6 to az + 22
    tx1, tx2 = ax + 6, ax + 22
    tz1, tz2 = az + 6, az + 22
    base_y = ay + 2
    wall_height = 11  # y: ay + 2 to ay + 12

    # Helper: Check if (x, z) is inside 17x17 chamfered octagon
    def is_in_octagon(x: int, z: int) -> bool:
        if not (tx1 <= x <= tx2 and tz1 <= z <= tz2):
            return False
        # Cut 3x3 triangles at each corner
        dx1 = x - tx1
        dx2 = tx2 - x
        dz1 = z - tz1
        dz2 = tz2 - z
        if dx1 + dz1 < 3:
            return False
        if dx2 + dz1 < 3:
            return False
        if dx1 + dz2 < 3:
            return False
        if dx2 + dz2 < 3:
            return False
        return True

    def is_octagon_perimeter(x: int, z: int) -> bool:
        if not is_in_octagon(x, z):
            return False
        # If any orthogonal neighbor is outside, it's on the perimeter
        for ox, oz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if not is_in_octagon(x + ox, z + oz):
                return True
        return False

    # Erect perimeter walls
    for y in range(base_y, base_y + wall_height):
        for x in range(tx1, tx2 + 1):
            for z in range(tz1, tz2 + 1):
                if is_octagon_perimeter(x, z):
                    # Corners use quartz pillars for crisp vertical edges
                    dx1, dx2 = x - tx1, tx2 - x
                    dz1, dz2 = z - tz1, tz2 - z
                    is_corner = (dx1 + dz1 == 3) or (dx2 + dz1 == 3) or (dx1 + dz2 == 3) or (dx2 + dz2 == 3)
                    b = m_pillar if is_corner else m_marble
                    steps.append(ConstructionStep(x=x, y=y, z=z, block=b, component_name=comp))

    # Decorative Roof Frieze (y = base_y + wall_height)
    roof_frieze_y = base_y + wall_height  # ay + 13
    for x in range(tx1, tx2 + 1):
        for z in range(tz1, tz2 + 1):
            if is_in_octagon(x, z):
                is_edge = is_octagon_perimeter(x, z)
                b = m_chiseled if is_edge else m_marble
                steps.append(ConstructionStep(x=x, y=roof_frieze_y, z=z, block=b, component_name=comp))

    # =========================================================================
    # 4. FOUR MONUMENTAL PISHTAQ (Grand Recessed Iwan Arches)
    # =========================================================================
    comp = "pishtaq_iwans"
    # Facades: North (z=tz1), South (z=tz2), West (x=tx1), East (x=tx2)
    # Center 5 blocks of each cardinal wall:
    mid_x = ax + 14
    mid_z = az + 14

    facades = [
        ("south", mid_x, tz2, 1, 0, [0, -1]),   # South entrance
        ("north", mid_x, tz1, 1, 0, [0, 1]),    # North
        ("west",  tx1, mid_z, 0, 1, [1, 0]),    # West
        ("east",  tx2, mid_z, 0, 1, [-1, 0]),   # East
    ]

    for name, fcx, fcz, par_x, par_z, inward in facades:
        # Grand recessed archway: 5 blocks wide, 8 blocks high
        for offset in [-2, -1, 0, 1, 2]:
            wx = fcx + offset * par_x
            wz = fcz + offset * par_z

            # Outer framing & Inlay
            for h in range(1, 9):
                cur_y = base_y + h
                # Arch top curve
                is_arch_top = (h >= 7 and abs(offset) >= 2) or (h == 8 and abs(offset) >= 1)

                if is_arch_top or abs(offset) == 2:
                    # Grand portal frame with lapis inlay
                    frame_block = m_gold if (h == 8 and offset == 0) else m_lapis if (h % 2 == 1) else m_chiseled
                    steps.append(ConstructionStep(x=wx, y=cur_y, z=wz, block=frame_block, component_name=comp))
                else:
                    # Recessed vault (1-2 blocks inward)
                    rec_x = wx + inward[0]
                    rec_z = wz + inward[1]
                    # Create open arched recess
                    steps.append(ConstructionStep(x=wx, y=cur_y, z=wz, block="minecraft:air", component_name=comp))
                    # Inner back wall of recess
                    back_x = wx + inward[0] * 2
                    back_z = wz + inward[1] * 2
                    if is_in_octagon(back_x, back_z):
                        steps.append(ConstructionStep(x=back_x, y=cur_y, z=back_z, block=m_chiseled, component_name=comp))

        # South facade entrance portal: cut open doorway at y = base_y, base_y + 1
        if name == "south":
            for y in [base_y, base_y + 1]:
                steps.append(ConstructionStep(x=mid_x, y=y, z=tz2, block="minecraft:air", component_name=comp))
                steps.append(ConstructionStep(x=mid_x, y=y, z=tz2 - 1, block="minecraft:air", component_name=comp))

    # =========================================================================
    # 5. INNER CENOTAPH CHAMBER & MEMORIALS
    # =========================================================================
    comp = "interior_chamber"
    # Geometric mosaic floor (y = base_y - 1 or base_y)
    for x in range(tx1 + 3, tx2 - 2):
        for z in range(tz1 + 3, tz2 - 2):
            # Chessboard / Islamic tessellation pattern
            is_accent = ((x + z) % 2 == 0)
            b = m_chiseled if is_accent else m_blackstone
            steps.append(ConstructionStep(x=x, y=base_y, z=z, block=b, component_name=comp))

    # Central Cenotaphs (Memorials for Mumtaz Mahal & Shah Jahan)
    # Centered around (mid_x, mid_z) = (ax + 14, az + 14)
    # Mumtaz Mahal's Cenotaph (Center):
    steps.append(ConstructionStep(x=mid_x, y=base_y + 1, z=mid_z, block=m_gold, component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=base_y + 1, z=mid_z - 1, block=f"{m_slab}[type=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=base_y + 2, z=mid_z, block=f"{m_slab}[type=bottom]", component_name=comp))

    # Shah Jahan's Cenotaph (Slightly larger, offset to the west as historically):
    steps.append(ConstructionStep(x=mid_x - 2, y=base_y + 1, z=mid_z, block=m_marble, component_name=comp))
    steps.append(ConstructionStep(x=mid_x - 2, y=base_y + 1, z=mid_z - 1, block=m_gold, component_name=comp))
    steps.append(ConstructionStep(x=mid_x - 2, y=base_y + 2, z=mid_z, block=f"{m_slab}[type=bottom]", component_name=comp))

    # Jali Screen (Marble lattice enclosure around cenotaphs):
    for jx in range(mid_x - 3, mid_x + 2):
        for jz in range(mid_z - 2, mid_z + 2):
            is_screen = (jx == mid_x - 3 or jx == mid_x + 1 or jz == mid_z - 2 or jz == mid_z + 1)
            # Entrance opening on South side of jali
            if is_screen and not (jz == mid_z + 1 and jx == mid_x):
                steps.append(ConstructionStep(x=jx, y=base_y + 1, z=jz, block=m_bars, component_name=comp))

    # Ornamental Palace Lanterns atop the Jali corner posts
    steps.append(ConstructionStep(x=mid_x - 3, y=base_y + 2, z=mid_z - 2, block=f"{m_lantern}[hanging=false]", component_name=comp))
    steps.append(ConstructionStep(x=mid_x + 1, y=base_y + 2, z=mid_z - 2, block=f"{m_lantern}[hanging=false]", component_name=comp))
    steps.append(ConstructionStep(x=mid_x - 3, y=base_y + 2, z=mid_z + 1, block=f"{m_lantern}[hanging=false]", component_name=comp))
    steps.append(ConstructionStep(x=mid_x + 1, y=base_y + 2, z=mid_z + 1, block=f"{m_lantern}[hanging=false]", component_name=comp))

    # =========================================================================
    # 6. ROOF CHATTRIS (4 Pillared Domed Kiosks)
    # =========================================================================
    comp = "roof_and_chattris"
    chattri_centers = [
        (ax + 9, az + 9),       # NW
        (ax + 19, az + 9),      # NE
        (ax + 9, az + 19),      # SW
        (ax + 19, az + 19),     # SE
    ]

    chattri_base_y = roof_frieze_y + 1  # ay + 14

    for kx, kz in chattri_centers:
        # 4 slender corner pillars (height 3)
        for y in range(chattri_base_y, chattri_base_y + 3):
            for dx, dz in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                steps.append(ConstructionStep(x=kx + dx, y=y, z=kz + dz, block=m_pillar, component_name=comp))

        # Chattri Dome Canopy (y = chattri_base_y + 3 to + 4)
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                steps.append(ConstructionStep(x=kx + dx, y=chattri_base_y + 3, z=kz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))
        steps.append(ConstructionStep(x=kx, y=chattri_base_y + 4, z=kz, block=m_gold, component_name=comp))
        steps.append(ConstructionStep(x=kx, y=chattri_base_y + 5, z=kz, block=m_spire, component_name=comp))

    # =========================================================================
    # 7. CENTRAL ONION DOME (Amrud) & GOLDEN FINIAL
    # =========================================================================
    comp = "central_onion_dome"
    dome_base_y = roof_frieze_y + 1  # ay + 14

    # Cylindrical High Drum (y: ay + 14 to ay + 16, diameter 7)
    for y in range(dome_base_y, dome_base_y + 3):
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                dist_sq = dx * dx + dz * dz
                # Circular ring of radius 3.2
                if 5 <= dist_sq <= 10:
                    steps.append(ConstructionStep(x=mid_x + dx, y=y, z=mid_z + dz, block=m_chiseled, component_name=comp))

    # Bulbous Onion Dome Curve:
    # Mughal onion domes bulge outward first before tapering to a sharp peak!
    onion_layers = [
        # (y_offset, min_r_sq, max_r_sq, material)
        (3, 10, 18, m_marble),   # y = ay + 17: Bulge outward (Radius ~4.2, 9x9 swell)
        (4, 10, 18, m_marble),   # y = ay + 18: Maximum bulge
        (5, 7, 13, m_marble),    # y = ay + 19: Contracting inward (Radius ~3.3, 7x7)
        (6, 4, 8, m_marble),     # y = ay + 20: Tapering (Radius ~2.5, 5x5)
        (7, 1, 4, m_marble),     # y = ay + 21: Upper cap (Radius ~1.8, 3x3)
        (8, 0, 1, m_marble),     # y = ay + 22: Apex peak (Radius ~1.0, 1x1)
    ]

    for dy, min_r, max_r, mat in onion_layers:
        cur_y = dome_base_y + dy
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                dist_sq = dx * dx + dz * dz
                if min_r <= dist_sq <= max_r:
                    steps.append(ConstructionStep(x=mid_x + dx, y=cur_y, z=mid_z + dz, block=mat, component_name=comp))

    # Golden Kalash & Lotus Finial (y = dome_base_y + 9 to + 12)
    steps.append(ConstructionStep(x=mid_x, y=dome_base_y + 9, z=mid_z, block=m_gold, component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=dome_base_y + 10, z=mid_z, block=m_gold, component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=dome_base_y + 11, z=mid_z, block=m_spire, component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=dome_base_y + 12, z=mid_z, block=m_spire, component_name=comp))

    # =========================================================================
    # 8. CHARBAGH REFLECTING POOL & GARDEN WATER CHANNEL
    # =========================================================================
    comp = "reflecting_pool"
    # Extends south from z = az + 31 to az + 48 (length 18 blocks)
    # Center line at mid_x (ax + 14)
    # Width: 5 blocks total (x: ax + 12 to ax + 16)
    pool_z_start = az + 31
    pool_z_end = az + 48

    for z in range(pool_z_start, pool_z_end + 1):
        # Center 3 blocks: Water canal
        for x in range(mid_x - 1, mid_x + 2):
            # Recessed seabed with submerged sea lanterns
            is_light_node = (z % 4 == 0 and x == mid_x)
            bed_block = m_sea_lantern if is_light_node else m_marble
            steps.append(ConstructionStep(x=x, y=ay - 1, z=z, block=bed_block, component_name=comp))
            # Water surface level
            steps.append(ConstructionStep(x=x, y=ay, z=z, block=m_water, component_name=comp))

        # Stone Coping & Border Walkways on East & West edges
        steps.append(ConstructionStep(x=mid_x - 2, y=ay, z=z, block=m_pool_border, component_name=comp))
        steps.append(ConstructionStep(x=mid_x + 2, y=ay, z=z, block=m_pool_border, component_name=comp))

        # Flanking Flowering Azalea Hedges
        steps.append(ConstructionStep(x=mid_x - 3, y=ay, z=z, block=m_leaves, component_name=comp))
        steps.append(ConstructionStep(x=mid_x + 3, y=ay, z=z, block=m_leaves, component_name=comp))

    # Southern Terminating Fountain / Platform at the end of the pool
    for x in range(mid_x - 3, mid_x + 4):
        steps.append(ConstructionStep(x=x, y=ay, z=pool_z_end + 1, block=m_chiseled, component_name=comp))
    steps.append(ConstructionStep(x=mid_x, y=ay + 1, z=pool_z_end + 1, block=m_sea_lantern, component_name=comp))

    return steps

