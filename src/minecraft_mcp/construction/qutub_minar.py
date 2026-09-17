"""
Qutub Minar Architectural Blueprint & Voxel Compiler
Generates the complete, historically faithful Indo-Islamic architectural ensemble:
- Elevated Courtyard Plinth & Cloister Terrace with perimeter trim & ceremonial entrance
- The ancient Iron Pillar of Delhi (Gupta era metallurgical marvel) in the courtyard
- Storey 1: Tapering base with 24 alternating circular (rounded) and angular (pointed) flutings,
  carved calligraphic bands, and arched entrance portal
- Balcony 1: Projecting muqarnas-style corbel brackets with iron railings and lanterns
- Storey 2: Tapered shaft with exclusively rounded (semicircular) flutings and chiseled band
- Balcony 2: Second projecting corbeled balcony ring
- Storey 3: Tapered shaft with exclusively angular (triangular) flutings and chiseled band
- Balcony 3: Third projecting corbeled balcony ring
- Storey 4: Contrasting white marble (smooth quartz & pillar) with red sandstone accent bands
- Balcony 4: Fourth projecting balcony ring
- Storey 5: White marble upper chamber with panoramic arched viewing portals
- Upper Cupola Pavilion: Pillared domed kiosk with golden cap and lightning rod finial
- Complete interior hollow core with continuous spiraling staircase and arrow-slit windows
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

DEFAULT_QUTUB_PALETTE = {
    "sandstone_base": "minecraft:red_sandstone",
    "sandstone_cut": "minecraft:cut_red_sandstone",
    "sandstone_chiseled": "minecraft:chiseled_red_sandstone",
    "sandstone_stairs": "minecraft:smooth_red_sandstone_stairs",
    "sandstone_slab": "minecraft:smooth_red_sandstone_slab",
    "sandstone_wall": "minecraft:red_sandstone_wall",
    "marble_white": "minecraft:smooth_quartz",
    "marble_pillar": "minecraft:quartz_pillar",
    "marble_stairs": "minecraft:quartz_stairs",
    "marble_slab": "minecraft:quartz_slab",
    "marble_chiseled": "minecraft:chiseled_quartz_block",
    "iron_railing": "minecraft:iron_bars",
    "iron_pillar_base": "minecraft:anvil[facing=north]",
    "iron_pillar_shaft": "minecraft:polished_blackstone_wall",
    "iron_pillar_cap": "minecraft:chiseled_polished_blackstone",
    "iron_pillar_plate": "minecraft:heavy_weighted_pressure_plate",
    "finial_gold": "minecraft:gold_block",
    "finial_rod": "minecraft:lightning_rod",
    "lantern": "minecraft:lantern",
    "lantern_hanging": "minecraft:lantern[hanging=true]",
    "air": "minecraft:air",
}

def create_qutub_minar_blueprint() -> ArchitecturalBlueprint:
    """Returns the ArchitecturalBlueprint model for the Qutub Minar."""
    return ArchitecturalBlueprint(
        id="qutub_minar",
        name="The Qutub Minar",
        structure_type=StructureType.TOWER,
        dimensions=Dimensions(width=19, depth=19, height=48),
        palette=DEFAULT_QUTUB_PALETTE,
        description="Historic 5-storey tapering Indo-Islamic victory minaret with fluted sandstone ribs, projecting corbeled balconies, white marble upper tiers, courtyard plinth, and the Iron Pillar of Delhi.",
        components=[
            BlueprintComponent(name="courtyard_plinth", component_type=ComponentType.FOUNDATION, order=1, material_role="sandstone_base"),
            BlueprintComponent(name="iron_pillar", component_type=ComponentType.INTERIOR, order=2, material_role="iron_pillar_shaft"),
            BlueprintComponent(name="podium_and_storey_1", component_type=ComponentType.WALL, order=3, material_role="sandstone_cut"),
            BlueprintComponent(name="balcony_1", component_type=ComponentType.FLOOR, order=4, material_role="iron_railing"),
            BlueprintComponent(name="storey_2", component_type=ComponentType.WALL, order=5, material_role="sandstone_cut"),
            BlueprintComponent(name="balcony_2", component_type=ComponentType.FLOOR, order=6, material_role="iron_railing"),
            BlueprintComponent(name="storey_3", component_type=ComponentType.WALL, order=7, material_role="sandstone_stairs"),
            BlueprintComponent(name="balcony_3", component_type=ComponentType.FLOOR, order=8, material_role="iron_railing"),
            BlueprintComponent(name="storey_4", component_type=ComponentType.WALL, order=9, material_role="marble_white"),
            BlueprintComponent(name="balcony_4", component_type=ComponentType.FLOOR, order=10, material_role="iron_railing"),
            BlueprintComponent(name="storey_5", component_type=ComponentType.WALL, order=11, material_role="marble_white"),
            BlueprintComponent(name="cupola_and_finial", component_type=ComponentType.ROOF, order=12, material_role="finial_gold"),
            BlueprintComponent(name="interior_staircase", component_type=ComponentType.INTERIOR, order=13, material_role="sandstone_stairs"),
        ],
    )

def generate_qutub_minar_steps(
    anchor: Dict[str, int],
    palette_override: Dict[str, str] = None,
) -> List[ConstructionStep]:
    """
    Generates all sequenced ConstructionSteps for the Qutub Minar complex.
    Coordinates relative to anchor:
    - ax, ay, az: Northwest corner of the courtyard plinth
    - Plinth dimensions: 19 x 19 (ax..ax+18, az..az+18)
    - Minar center: cx = ax + 9, cz = az + 9
    """
    palette = DEFAULT_QUTUB_PALETTE.copy()
    if palette_override:
        palette.update(palette_override)

    ax = anchor["x"]
    ay = anchor["y"]
    az = anchor["z"]

    cx = ax + 9
    cz = az + 9

    steps: List[ConstructionStep] = []

    m_base = palette["sandstone_base"]
    m_cut = palette["sandstone_cut"]
    m_chiseled = palette["sandstone_chiseled"]
    m_stairs = palette["sandstone_stairs"]
    m_slab = palette["sandstone_slab"]
    m_wall = palette["sandstone_wall"]
    m_marble = palette["marble_white"]
    m_pillar = palette["marble_pillar"]
    m_mstairs = palette["marble_stairs"]
    m_mslab = palette["marble_slab"]
    m_mchiseled = palette["marble_chiseled"]
    m_bars = palette["iron_railing"]
    m_anvil = palette["iron_pillar_base"]
    m_pwall = palette["iron_pillar_shaft"]
    m_pcap = palette["iron_pillar_cap"]
    m_pplate = palette["iron_pillar_plate"]
    m_gold = palette["finial_gold"]
    m_rod = palette["finial_rod"]
    m_lantern = palette["lantern"]
    m_hlantern = palette["lantern_hanging"]
    m_air = palette["air"]

    # =========================================================================
    # 1. COURTYARD PLINTH (19 x 19) & CEREMONIAL ENTRANCE STEPS
    # =========================================================================
    comp = "courtyard_plinth"
    pw, pd = 19, 19

    # Layer 0: Solid Sub-Base Foundation (y = ay)
    for x in range(ax, ax + pw):
        for z in range(az, az + pd):
            steps.append(ConstructionStep(x=x, y=ay, z=z, block=m_base, component_name=comp))

    # Layer 1: Paved Courtyard Terrace Floor (y = ay + 1)
    for x in range(ax, ax + pw):
        for z in range(az, az + pd):
            is_edge = (x == ax or x == ax + pw - 1 or z == az or z == az + pd - 1)
            b = m_chiseled if is_edge else m_cut
            steps.append(ConstructionStep(x=x, y=ay + 1, z=z, block=b, component_name=comp))

    # Perimeter Low Wall / Balustrade on terrace edges (except south entrance)
    for x in range(ax, ax + pw):
        for z in range(az, az + pd):
            if x == ax or x == ax + pw - 1 or z == az:
                steps.append(ConstructionStep(x=x, y=ay + 2, z=z, block=f"{m_slab}[type=bottom]", component_name=comp))
            elif z == az + pd - 1 and not (cx - 2 <= x <= cx + 2):
                steps.append(ConstructionStep(x=x, y=ay + 2, z=z, block=f"{m_slab}[type=bottom]", component_name=comp))

    # South Ceremonial Entrance Stairs leading up from ground to terrace (y = ay to ay + 1)
    for x in range(cx - 2, cx + 3):
        steps.append(ConstructionStep(x=x, y=ay, z=az + pd, block=f"{m_stairs}[facing=north,half=bottom]", component_name=comp))
        steps.append(ConstructionStep(x=x, y=ay + 1, z=az + pd - 1, block=f"{m_stairs}[facing=north,half=bottom]", component_name=comp))

    # Decorative Cloister Arches in North-West and North-East corners of Courtyard
    for corner_x, corner_z in [(ax + 2, az + 2), (ax + pw - 3, az + 2)]:
        steps.append(ConstructionStep(x=corner_x, y=ay + 2, z=corner_z, block=m_chiseled, component_name=comp))
        steps.append(ConstructionStep(x=corner_x, y=ay + 3, z=corner_z, block=m_wall, component_name=comp))
        steps.append(ConstructionStep(x=corner_x, y=ay + 4, z=corner_z, block=m_chiseled, component_name=comp))
        steps.append(ConstructionStep(x=corner_x, y=ay + 5, z=corner_z, block=m_lantern, component_name=comp))

    # =========================================================================
    # 2. THE IRON PILLAR OF DELHI (Courtyard Landmark)
    # =========================================================================
    comp = "iron_pillar"
    ip_x, ip_z = cx - 5, cz + 4
    # Stone plinth surround for the pillar
    for dx in [-1, 0, 1]:
        for dz in [-1, 0, 1]:
            if dx == 0 and dz == 0:
                continue
            steps.append(ConstructionStep(x=ip_x + dx, y=ay + 2, z=ip_z + dz, block=f"{m_slab}[type=bottom]", component_name=comp))

    # Ancient Iron Base
    steps.append(ConstructionStep(x=ip_x, y=ay + 2, z=ip_z, block=m_anvil, component_name=comp))
    # Weathered Rust-Resistant Shaft (4 blocks tall)
    for y in range(ay + 3, ay + 7):
        steps.append(ConstructionStep(x=ip_x, y=y, z=ip_z, block=m_pwall, component_name=comp))
    # Inverted Bell Capital & Top Abacus
    steps.append(ConstructionStep(x=ip_x, y=ay + 7, z=ip_z, block=m_pcap, component_name=comp))
    steps.append(ConstructionStep(x=ip_x, y=ay + 8, z=ip_z, block=m_pplate, component_name=comp))

    # =========================================================================
    # 3. MINAR PODIUM & STOREY 1 (Height: ay + 2 to ay + 13)
    # 24 Alternating Circular and Angular Flutings, Calligraphy Bands, Entrance Arch
    # =========================================================================
    comp = "podium_and_storey_1"

    # Octagonal Stepped Base Podium at y = ay + 2 (radius 5, 11x11 octagonal plinth)
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            if abs(dx) + abs(dz) <= 7:
                is_rim = (abs(dx) + abs(dz) == 7 or abs(dx) == 5 or abs(dz) == 5)
                b = m_chiseled if is_rim else m_cut
                steps.append(ConstructionStep(x=cx + dx, y=ay + 2, z=cz + dz, block=b, component_name=comp))

    # 24 Flutings definition for Storey 1 around cx, cz (radius 4)
    # Each entry: (dx, dz, fluting_type, facing_dir)
    # fluting_type: 'round' (cut_red_sandstone) or 'angular' (smooth_red_sandstone_stairs)
    flutings_s1: List[Tuple[int, int, str, str]] = [
        # North sector (dz <= -3)
        (0, -4, "round", "north"),
        (1, -4, "angular", "north"),
        (2, -3, "round", "north"),
        (3, -3, "angular", "north"),
        (3, -2, "round", "east"),
        # East sector (dx >= 3)
        (4, -1, "angular", "east"),
        (4, 0, "round", "east"),
        (4, 1, "angular", "east"),
        (3, 2, "round", "east"),
        (3, 3, "angular", "south"),
        # South sector (dz >= 3)
        (2, 3, "round", "south"),
        (1, 4, "angular", "south"),
        (0, 4, "round", "south"),     # Entrance portal at ground level
        (-1, 4, "angular", "south"),
        (-2, 3, "round", "south"),
        (-3, 3, "angular", "south"),
        # West sector (dx <= -3)
        (-3, 2, "round", "west"),
        (-4, 1, "angular", "west"),
        (-4, 0, "round", "west"),
        (-4, -1, "angular", "west"),
        (-3, -2, "round", "west"),
        # North-West return
        (-3, -3, "angular", "north"),
        (-2, -3, "round", "north"),
        (-1, -4, "angular", "north"),
    ]

    # Fill solid wall core between outer flutings and inner hollow shaft
    for y in range(ay + 3, ay + 14):
        # Decorative Calligraphic Bands at y = ay + 6 and y = ay + 11
        is_band = (y == ay + 6 or y == ay + 11)

        # Core ring: radius 1 to 3
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                dist_sq = dx * dx + dz * dz
                # Inner hollow shaft radius 1.5 (dx in [-1..1], dz in [-1..1])
                if abs(dx) <= 1 and abs(dz) <= 1:
                    # Carve hollow interior (will place stairs later)
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))
                elif dist_sq <= 12:
                    # Intermediate masonry backing
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_base, component_name=comp))

        # Place the 24 flutings on the exterior
        for dx, dz, f_type, f_dir in flutings_s1:
            # Entrance Portal on South side (y = ay + 3 to ay + 5 at dz = 4, dx = 0)
            if dz >= 3 and abs(dx) <= 1 and y <= ay + 5:
                if dx == 0 and y <= ay + 4:
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))
                    continue
                elif dx == 0 and y == ay + 5:
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_stairs}[facing=south,half=top]", component_name=comp))
                    continue

            # Arrow-slit windows in Cardinal points at y = ay + 8
            if y == ay + 8 and ((dx == 0 and abs(dz) == 4) or (dz == 0 and abs(dx) == 4)):
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_bars, component_name=comp))
                continue

            if is_band:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_chiseled, component_name=comp))
            elif f_type == "round":
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_cut, component_name=comp))
            else:
                # Angular sharp fluting: outward facing stairs
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_stairs}[facing={f_dir},half=bottom]", component_name=comp))

    # South Entrance Porch / Gateway Frame (y = ay + 3 to ay + 6)
    steps.append(ConstructionStep(x=cx - 1, y=ay + 3, z=cz + 5, block=m_chiseled, component_name=comp))
    steps.append(ConstructionStep(x=cx - 1, y=ay + 4, z=cz + 5, block=m_cut, component_name=comp))
    steps.append(ConstructionStep(x=cx - 1, y=ay + 5, z=cz + 5, block=m_chiseled, component_name=comp))

    steps.append(ConstructionStep(x=cx + 1, y=ay + 3, z=cz + 5, block=m_chiseled, component_name=comp))
    steps.append(ConstructionStep(x=cx + 1, y=ay + 4, z=cz + 5, block=m_cut, component_name=comp))
    steps.append(ConstructionStep(x=cx + 1, y=ay + 5, z=cz + 5, block=m_chiseled, component_name=comp))

    steps.append(ConstructionStep(x=cx, y=ay + 5, z=cz + 5, block=f"{m_stairs}[facing=north,half=top]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 6, z=cz + 5, block=f"{m_slab}[type=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 6, z=cz + 4, block=m_lantern, component_name=comp))

    # =========================================================================
    # 4. BALCONY 1 (Projecting Muqarnas Corbel Balcony, y = ay + 14 to ay + 15)
    # =========================================================================
    comp = "balcony_1"
    # y = ay + 14: Projecting corbel brackets (inverted stairs) expanding to radius 5 (11x11)
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            if abs(dx) + abs(dz) <= 7:
                is_outer = (abs(dx) == 5 or abs(dz) == 5 or abs(dx) + abs(dz) == 7)
                if is_outer:
                    # Inverted stair facing outward
                    if abs(dx) > abs(dz):
                        f = "east" if dx > 0 else "west"
                    else:
                        f = "south" if dz > 0 else "north"
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 14, z=cz + dz, block=f"{m_stairs}[facing={f},half=top]", component_name=comp))
                else:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 14, z=cz + dz, block=m_chiseled, component_name=comp))

    # y = ay + 15: Balcony Walkway Floor & Iron Railing
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            if abs(dx) + abs(dz) <= 7:
                is_perimeter = (abs(dx) == 5 or abs(dz) == 5 or abs(dx) + abs(dz) == 7)
                if is_perimeter:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 15, z=cz + dz, block=m_bars, component_name=comp))
                elif abs(dx) >= 3 or abs(dz) >= 3:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 15, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))

    # Balcony 1 Hanging Lanterns at cardinal brackets
    steps.append(ConstructionStep(x=cx, y=ay + 13, z=cz - 5, block=m_hlantern, component_name=comp))
    steps.append(ConstructionStep(x=cx + 5, y=ay + 13, z=cz, block=m_hlantern, component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 13, z=cz + 5, block=m_hlantern, component_name=comp))
    steps.append(ConstructionStep(x=cx - 5, y=ay + 13, z=cz, block=m_hlantern, component_name=comp))

    # =========================================================================
    # 5. STOREY 2 (Height: ay + 15 to ay + 22)
    # Tapered Shaft (Radius 3.2), Rounded / Semicircular Flutings Only
    # =========================================================================
    comp = "storey_2"
    # Rounded perimeter ribs at radius ~3
    round_ribs_s2: List[Tuple[int, int]] = [
        (0, -3), (1, -3), (-1, -3),
        (2, -2), (-2, -2),
        (3, -1), (3, 0), (3, 1),
        (2, 2), (-2, 2),
        (0, 3), (1, 3), (-1, 3),
        (-3, -1), (-3, 0), (-3, 1),
    ]

    for y in range(ay + 15, ay + 23):
        is_band = (y == ay + 19)

        # Inner hollow core (keep hollow for stairs)
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))

        # Intermediate backing masonry
        for dx in [-2, -1, 0, 1, 2]:
            for dz in [-2, -1, 0, 1, 2]:
                if not (abs(dx) <= 1 and abs(dz) <= 1):
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_base, component_name=comp))

        # Exterior rounded flutings
        for dx, dz in round_ribs_s2:
            # Arrow-slit windows in cardinal points at y = ay + 17 and y = ay + 21
            if (y == ay + 17 or y == ay + 21) and ((dx == 0 and abs(dz) == 3) or (dz == 0 and abs(dx) == 3)):
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_bars, component_name=comp))
            elif is_band:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_chiseled, component_name=comp))
            else:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_cut, component_name=comp))

    # =========================================================================
    # 6. BALCONY 2 (y = ay + 23 to ay + 24)
    # =========================================================================
    comp = "balcony_2"
    # Corbel brackets projecting outward to radius 4 (9x9)
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            if abs(dx) + abs(dz) <= 5:
                is_outer = (abs(dx) == 4 or abs(dz) == 4 or abs(dx) + abs(dz) == 5)
                if is_outer:
                    if abs(dx) > abs(dz):
                        f = "east" if dx > 0 else "west"
                    else:
                        f = "south" if dz > 0 else "north"
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 23, z=cz + dz, block=f"{m_stairs}[facing={f},half=top]", component_name=comp))
                else:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 23, z=cz + dz, block=m_chiseled, component_name=comp))

    # Balcony 2 Floor & Railing
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            if abs(dx) + abs(dz) <= 5:
                is_perimeter = (abs(dx) == 4 or abs(dz) == 4 or abs(dx) + abs(dz) == 5)
                if is_perimeter:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 24, z=cz + dz, block=m_bars, component_name=comp))
                elif abs(dx) >= 2 or abs(dz) >= 2:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 24, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))

    # =========================================================================
    # 7. STOREY 3 (Height: ay + 24 to ay + 30)
    # Tapered Shaft (Radius 2.8), Angular / Triangular Flutings Only
    # =========================================================================
    comp = "storey_3"
    angular_ribs_s3: List[Tuple[int, int, str]] = [
        (0, -3, "north"), (1, -2, "north"), (-1, -2, "north"),
        (2, -1, "east"), (3, 0, "east"), (2, 1, "east"),
        (1, 2, "south"), (0, 3, "south"), (-1, 2, "south"),
        (-2, 1, "west"), (-3, 0, "west"), (-2, -1, "west"),
    ]

    for y in range(ay + 24, ay + 31):
        is_band = (y == ay + 27)

        # Hollow shaft core
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))

        # Intermediate backing
        for dx in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if abs(dx) == 1 and abs(dz) == 1:
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_base, component_name=comp))

        # Exterior angular flutings
        for dx, dz, f_dir in angular_ribs_s3:
            if y == ay + 28 and ((dx == 0 and abs(dz) == 3) or (dz == 0 and abs(dx) == 3)):
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_bars, component_name=comp))
            elif is_band:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_chiseled, component_name=comp))
            else:
                steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_stairs}[facing={f_dir},half=bottom]", component_name=comp))

    # =========================================================================
    # 8. BALCONY 3 (y = ay + 31 to ay + 32)
    # =========================================================================
    comp = "balcony_3"
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) <= 4:
                is_outer = (abs(dx) == 3 or abs(dz) == 3 or abs(dx) + abs(dz) == 4)
                if is_outer:
                    if abs(dx) > abs(dz):
                        f = "east" if dx > 0 else "west"
                    else:
                        f = "south" if dz > 0 else "north"
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 31, z=cz + dz, block=f"{m_stairs}[facing={f},half=top]", component_name=comp))
                else:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 31, z=cz + dz, block=m_chiseled, component_name=comp))

    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) <= 4:
                is_perimeter = (abs(dx) == 3 or abs(dz) == 3 or abs(dx) + abs(dz) == 4)
                if is_perimeter:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 32, z=cz + dz, block=m_bars, component_name=comp))
                elif abs(dx) >= 2 or abs(dz) >= 2:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 32, z=cz + dz, block=f"{m_slab}[type=bottom]", component_name=comp))

    # =========================================================================
    # 9. STOREY 4 (Height: ay + 32 to ay + 37)
    # White Marble Facing (Smooth Quartz & Pillars) with Red Sandstone Bands
    # =========================================================================
    comp = "storey_4"
    # Radius 2 (5x5 cross section with cut corners)
    for y in range(ay + 32, ay + 38):
        is_red_band = (y == ay + 34)

        # Hollow shaft core
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) <= 0 and abs(dz) <= 0:
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))

        # Octagonal 5x5 exterior
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if abs(dx) == 2 and abs(dz) == 2:
                    continue  # cut corner
                if abs(dx) == 2 or abs(dz) == 2:
                    if is_red_band:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_cut, component_name=comp))
                    elif (abs(dx) == 1 and abs(dz) == 2) or (abs(dx) == 2 and abs(dz) == 1):
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_pillar}[axis=y]", component_name=comp))
                    elif y == ay + 35 and (abs(dx) == 2 and dz == 0 or abs(dz) == 2 and dx == 0):
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_bars, component_name=comp))
                    else:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_marble, component_name=comp))

    # =========================================================================
    # 10. BALCONY 4 (y = ay + 38)
    # =========================================================================
    comp = "balcony_4"
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if abs(dx) + abs(dz) <= 3:
                is_outer = (abs(dx) + abs(dz) == 3 or abs(dx) == 2 or abs(dz) == 2)
                if is_outer:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 38, z=cz + dz, block=f"{m_mslab}[type=bottom]", component_name=comp))
                else:
                    steps.append(ConstructionStep(x=cx + dx, y=ay + 38, z=cz + dz, block=m_marble, component_name=comp))

    # =========================================================================
    # 11. STOREY 5 (Height: ay + 39 to ay + 43)
    # White Marble Top Observation Tier with Arched Windows
    # =========================================================================
    comp = "storey_5"
    for y in range(ay + 39, ay + 44):
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if abs(dx) == 2 and abs(dz) == 2:
                    # Corner marble pillar
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=f"{m_pillar}[axis=y]", component_name=comp))
                elif abs(dx) == 2 or abs(dz) == 2:
                    # Facade walls with arched panoramic lookouts
                    if y == ay + 41 or y == ay + 42:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_air, component_name=comp))
                    elif y == ay + 43:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_mchiseled, component_name=comp))
                    else:
                        steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=m_marble, component_name=comp))
                elif abs(dx) <= 1 and abs(dz) <= 1:
                    # Open observation floor
                    b = m_air if y > ay + 39 else m_mchiseled
                    steps.append(ConstructionStep(x=cx + dx, y=y, z=cz + dz, block=b, component_name=comp))

    # =========================================================================
    # 12. UPPER CUPOLA PAVILION & DECORATIVE FINIAL (Height: ay + 44 to ay + 48)
    # =========================================================================
    comp = "cupola_and_finial"
    # y = ay + 44: Cupola base & corner pillars
    for dx in [-1, 1]:
        for dz in [-1, 1]:
            steps.append(ConstructionStep(x=cx + dx, y=ay + 44, z=cz + dz, block=f"{m_pillar}[axis=y]", component_name=comp))
    # Arched capitals (y = ay + 45)
    steps.append(ConstructionStep(x=cx, y=ay + 45, z=cz - 1, block=f"{m_mstairs}[facing=north,half=top]", component_name=comp))
    steps.append(ConstructionStep(x=cx + 1, y=ay + 45, z=cz, block=f"{m_mstairs}[facing=east,half=top]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 45, z=cz + 1, block=f"{m_mstairs}[facing=south,half=top]", component_name=comp))
    steps.append(ConstructionStep(x=cx - 1, y=ay + 45, z=cz, block=f"{m_mstairs}[facing=west,half=top]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 44, z=cz, block=m_lantern, component_name=comp))

    # Domed Roof (y = ay + 46)
    steps.append(ConstructionStep(x=cx, y=ay + 46, z=cz - 1, block=f"{m_stairs}[facing=south,half=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=cx + 1, y=ay + 46, z=cz, block=f"{m_stairs}[facing=west,half=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 46, z=cz + 1, block=f"{m_stairs}[facing=north,half=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=cx - 1, y=ay + 46, z=cz, block=f"{m_stairs}[facing=east,half=bottom]", component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 46, z=cz, block=m_cut, component_name=comp))

    # Golden Cap & Towering Lightning Rod Finial (y = ay + 47 to ay + 48)
    steps.append(ConstructionStep(x=cx, y=ay + 47, z=cz, block=m_gold, component_name=comp))
    steps.append(ConstructionStep(x=cx, y=ay + 48, z=cz, block=f"{m_rod}[facing=up]", component_name=comp))

    # =========================================================================
    # 13. INTERIOR SPIRAL STAIRCASE & LANDING LIGHTS (ay + 2 to ay + 40)
    # =========================================================================
    comp = "interior_staircase"
    # Helical stairs rotating around the central core
    stair_cycle = [
        (0, -1, "east"),
        (1, -1, "south"),
        (1, 0, "south"),
        (1, 1, "west"),
        (0, 1, "west"),
        (-1, 1, "north"),
        (-1, 0, "north"),
        (-1, -1, "east"),
    ]

    for y in range(ay + 2, ay + 40):
        cycle_idx = (y - ay) % len(stair_cycle)
        dx, dz, f_dir = stair_cycle[cycle_idx]
        stair_mat = m_mstairs if y >= ay + 33 else m_stairs
        steps.append(ConstructionStep(
            x=cx + dx,
            y=y,
            z=cz + dz,
            block=f"{stair_mat}[facing={f_dir},half=bottom]",
            component_name=comp,
        ))

        # Lanterns placed at landings
        if y in (ay + 8, ay + 16, ay + 25, ay + 33, ay + 39):
            steps.append(ConstructionStep(x=cx, y=y, z=cz, block=m_lantern, component_name=comp))

    return steps

