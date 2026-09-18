"""
Built-in Procedural Architectural Template Library (Prefabs) for Minecraft MCP.
Provides parameterized, composable architectural templates (Gothic Cathedral, Roman Colosseum,
Mughal Monument, Medieval Castle, Greek Peripteral Temple, Islamic Fluted Minaret).
"""

from typing import Dict, Any, List, Optional
import math


def build_greek_peripteral_temple_spec(
    colonnade_length: int = 24,
    colonnade_width: int = 14,
    column_height: int = 6,
    roof_pitch: float = 0.5,
    stylobate_material: str = "minecraft:smooth_quartz",
    column_material: str = "minecraft:quartz_pillar",
    wall_material: str = "minecraft:quartz_block",
    roof_material: str = "minecraft:sandstone_stairs",
    floor_material: str = "minecraft:polished_andesite",
    accent_material: str = "minecraft:lantern",
) -> Dict[str, Any]:
    """
    Generates a classical Greek peripteral temple (e.g. Parthenon style) specification:
    - 3-stepped stereobate / stylobate
    - Peripteral colonnade with fluted columns & capitals
    - Cella sanctuary chamber with entrance
    - Entablature with pediment gables and pitched tile roof
    """
    half_l = colonnade_length // 2
    half_w = colonnade_width // 2

    # 1. Stepped Stylobate (3 tiers)
    stylobate_tiers = [
        {
            "type": "box",
            "min_pt": [-half_l - 2, 0, -half_w - 2],
            "max_pt": [half_l + 2, 0, half_w + 2],
            "material": stylobate_material,
        },
        {
            "type": "box",
            "min_pt": [-half_l - 1, 1, -half_w - 1],
            "max_pt": [half_l + 1, 1, half_w + 1],
            "material": stylobate_material,
        },
        {
            "type": "box",
            "min_pt": [-half_l, 2, -half_w],
            "max_pt": [half_l, 2, half_w],
            "material": floor_material,
        },
    ]

    # 2. Peripteral Colonnade (columns along perimeter spaced every 4 blocks)
    columns = []
    col_spacing = 4
    # Along length (+Z and -Z edges)
    for x in range(-half_l + 1, half_l, col_spacing):
        columns.append({
            "type": "column",
            "style": "classical",
            "base_height": 1,
            "shaft_height": column_height - 2,
            "capital_height": 1,
            "radius": 1,
            "material": column_material,
            "transform": {"translation": [x, 3, half_w - 1]}
        })
        columns.append({
            "type": "column",
            "style": "classical",
            "base_height": 1,
            "shaft_height": column_height - 2,
            "capital_height": 1,
            "radius": 1,
            "material": column_material,
            "transform": {"translation": [x, 3, -half_w + 1]}
        })
    # Along width (+X and -X ends)
    for z in range(-half_w + 1, half_w, col_spacing):
        columns.append({
            "type": "column",
            "style": "classical",
            "base_height": 1,
            "shaft_height": column_height - 2,
            "capital_height": 1,
            "radius": 1,
            "material": column_material,
            "transform": {"translation": [half_l - 1, 3, z]}
        })
        columns.append({
            "type": "column",
            "style": "classical",
            "base_height": 1,
            "shaft_height": column_height - 2,
            "capital_height": 1,
            "radius": 1,
            "material": column_material,
            "transform": {"translation": [-half_l + 1, 3, z]}
        })

    # 3. Inner Cella Sanctuary
    cella_min_x = -half_l + 4
    cella_max_x = half_l - 4
    cella_min_z = -half_w + 3
    cella_max_z = half_w - 3
    cella_y = 3
    cella_top_y = cella_y + column_height

    cella = {
        "type": "subtract",
        "base": {
            "type": "box",
            "min_pt": [cella_min_x, cella_y, cella_min_z],
            "max_pt": [cella_max_x, cella_top_y, cella_max_z],
            "material": wall_material,
            "hollow": True,
            "wall_thickness": 1,
        },
        "subtrahends": [
            # Front portal doorway opening
            {
                "type": "box",
                "min_pt": [cella_min_x - 1, cella_y, -1],
                "max_pt": [cella_min_x + 2, cella_y + 3, 1],
                "material": "minecraft:air",
            }
        ]
    }

    # 4. Entablature & Architrave beam
    entablature_y = 3 + column_height
    entablature = {
        "type": "box",
        "min_pt": [-half_l, entablature_y, -half_w],
        "max_pt": [half_l, entablature_y + 1, half_w],
        "material": stylobate_material,
    }

    # 5. Pitched Gable Roof
    roof_base_y = entablature_y + 2
    roof_layers = []
    roof_steps = half_w + 1
    for step in range(roof_steps):
        ry = roof_base_y + step
        rz_min = -half_w + step
        rz_max = half_w - step
        if rz_min <= rz_max:
            roof_layers.append({
                "type": "box",
                "min_pt": [-half_l - 1, ry, rz_min],
                "max_pt": [half_l + 1, ry, rz_max],
                "material": roof_material,
            })

    all_children = stylobate_tiers + columns + [cella, entablature] + roof_layers
    return {
        "type": "union",
        "children": all_children
    }


def build_roman_colosseum_spec(
    outer_radius: int = 24,
    inner_radius: int = 16,
    arcade_levels: int = 2,
    bays_count: int = 24,
    sandstone_type: str = "minecraft:cut_sandstone",
    column_type: str = "minecraft:smooth_sandstone",
    keystone_type: str = "minecraft:chiseled_sandstone",
    arena_material: str = "minecraft:sand",
    seating_material: str = "minecraft:stone_brick_slab",
) -> Dict[str, Any]:
    """
    Generates a classical Roman Colosseum arena & arcade specification:
    - Circular/elliptical plinth foundation
    - Radial arcade bays with Roman round arches and columns
    - Concentric stepped cavea seating tiers
    - Arena pit floor
    """
    children: List[Dict[str, Any]] = []

    # 1. Ground Terrace Plinth
    children.append({
        "type": "cylinder",
        "center": [0, 0, 0],
        "radius": outer_radius + 2,
        "height": 2,
        "material": sandstone_type,
    })

    # 2. Central Sand Arena Floor
    children.append({
        "type": "circle",
        "center": [0, 2, 0],
        "radius": inner_radius - 4,
        "filled": True,
        "material": arena_material,
    })

    # 3. Concentric Stepped Cavea Seating (3 tiers)
    for tier in range(3):
        tier_r_in = inner_radius - 3 + tier * 2
        tier_r_out = tier_r_in + 2
        tier_y = 2 + tier
        children.append({
            "type": "ring",
            "center": [0, tier_y, 0],
            "outer_radius": tier_r_out,
            "inner_radius": tier_r_in,
            "height": 1,
            "material": seating_material,
        })

    # 4. Multi-level Radial Arcades
    for lvl in range(arcade_levels):
        lvl_y = 2 + lvl * 6
        lvl_radius = outer_radius - lvl

        # Outer ring perimeter wall
        children.append({
            "type": "ring",
            "center": [0, lvl_y, 0],
            "outer_radius": lvl_radius,
            "inner_radius": lvl_radius - 2,
            "height": 6,
            "material": sandstone_type,
        })

        # Radial bays (arch + columns)
        bay_spec = {
            "type": "arch",
            "style": "roman_round",
            "width": 4,
            "height": 5,
            "depth": 2,
            "material": column_type,
            "keystone": True,
        }
        children.append({
            "type": "radial_array",
            "child": bay_spec,
            "count": bays_count,
            "radius": float(lvl_radius - 1),
            "arc_angle": 360.0,
            "start_angle": 0.0,
            "center": [0.0, float(lvl_y), 0.0],
            "orient": "tangent",
        })

    # 5. Attic Wall & Cornice
    attic_y = 2 + arcade_levels * 6
    children.append({
        "type": "ring",
        "center": [0, attic_y, 0],
        "outer_radius": outer_radius - arcade_levels + 1,
        "inner_radius": outer_radius - arcade_levels - 1,
        "height": 3,
        "material": keystone_type,
    })

    return {
        "type": "union",
        "children": children
    }


def build_gothic_cathedral_spec(
    length: int = 30,
    width: int = 16,
    vault_height: int = 14,
    tower_height: int = 24,
    stone_material: str = "minecraft:stone_bricks",
    accent_material: str = "minecraft:deepslate_bricks",
    stained_glass_material: str = "minecraft:blue_stained_glass",
    roof_material: str = "minecraft:dark_prismarine",
) -> Dict[str, Any]:
    """
    Generates a High Gothic Cathedral specification:
    - Nave with pointed arch rib vaults
    - Side aisles and clerestory walls
    - Twin westwork bell towers with pointed spires
    - Rose window opening with stained glass
    - Apse choir rear
    """
    children: List[Dict[str, Any]] = []
    half_l = length // 2
    half_w = width // 2

    # 1. Foundation Slab
    children.append({
        "type": "box",
        "min_pt": [-half_l, 0, -half_w],
        "max_pt": [half_l, 1, half_w],
        "material": stone_material,
    })

    # 2. Nave High Vaulted Shell
    nave_h = vault_height
    nave_shell = {
        "type": "box",
        "min_pt": [-half_l + 4, 2, -half_w + 2],
        "max_pt": [half_l - 4, nave_h, half_w - 2],
        "material": stone_material,
        "hollow": True,
        "wall_thickness": 1,
    }
    children.append(nave_shell)

    # 3. Pitched Gothic Roof
    roof_steps = (half_w - 2) + 2
    for step in range(roof_steps):
        ry = nave_h + step
        rz_min = -half_w + 2 + step
        rz_max = half_w - 2 - step
        if rz_min <= rz_max:
            children.append({
                "type": "box",
                "min_pt": [-half_l + 3, ry, rz_min],
                "max_pt": [half_l - 3, ry, rz_max],
                "material": roof_material,
            })

    # 4. Twin Westwork Bell Towers (at -X facade)
    tower_size = 4
    for tz_sign in [-1, 1]:
        tz_center = tz_sign * (half_w - 2)
        # Tower body
        children.append({
            "type": "box",
            "min_pt": [-half_l, 2, tz_center - tower_size // 2],
            "max_pt": [-half_l + tower_size, tower_height - 6, tz_center + tower_size // 2],
            "material": accent_material,
            "hollow": True,
            "wall_thickness": 1,
        })
        # Pointed Spire
        children.append({
            "type": "loft",
            "layers": [
                {"y": tower_height - 6, "radius": tower_size / 2.0, "sides": 4},
                {"y": tower_height - 2, "radius": tower_size / 3.0, "sides": 4},
                {"y": tower_height + 4, "radius": 0.5, "sides": 4},
            ],
            "material": roof_material,
            "transform": {"translation": [-half_l + tower_size // 2, 0, tz_center]}
        })

    # 5. Rose Window (Circular opening on West facade)
    children.append({
        "type": "circle",
        "center": [-half_l + 4, nave_h - 4, 0],
        "radius": 3.0,
        "filled": True,
        "plane": "YZ",
        "material": stained_glass_material,
    })

    return {
        "type": "union",
        "children": children
    }


def build_mughal_monument_spec(
    plinth_size: int = 28,
    dome_radius: int = 6,
    minaret_height: int = 26,
    marble_material: str = "minecraft:quartz_block",
    inlay_material: str = "minecraft:gold_block",
    dome_material: str = "minecraft:smooth_quartz",
    pool_material: str = "minecraft:water",
) -> Dict[str, Any]:
    """
    Generates an Indo-Islamic Mughal Mausoleum specification (Taj Mahal style):
    - Raised square plinth terrace
    - Central octagonal tomb structure with 4 vaulted pishtaq iwans
    - Central double onion dome with golden finial
    - 4 corner freestanding tapering minarets with balconies
    """
    children: List[Dict[str, Any]] = []
    half_p = plinth_size // 2

    # 1. Raised Plinth Terrace
    children.append({
        "type": "box",
        "min_pt": [-half_p, 0, -half_p],
        "max_pt": [half_p, 3, half_p],
        "material": marble_material,
    })

    # 2. Central Octagonal Mausoleum Body
    tomb_r = dome_radius + 4
    children.append({
        "type": "cylinder",
        "center": [0, 4, 0],
        "radius": tomb_r,
        "height": 10,
        "hollow": True,
        "wall_thickness": 2,
        "material": marble_material,
    })

    # 3. 4 Pishtaq Iwans (Arches at 4 cardinal directions)
    for rot in [0, 90, 180, 270]:
        children.append({
            "type": "arch",
            "style": "islamic_horseshoe",
            "width": 6,
            "height": 8,
            "depth": 3,
            "material": inlay_material,
            "transform": {
                "translation": [0, 4, tomb_r],
                "rotation_y": float(rot),
            }
        })

    # 4. Central Onion Dome & Finial
    dome_y = 14
    children.append({
        "type": "dome",
        "style": "onion",
        "radius": dome_radius,
        "height": dome_radius + 3,
        "base_y": dome_y,
        "material": dome_material,
        "finial": True,
    })

    # 5. 4 Corner Freestanding Minarets
    corner_offset = half_p - 3
    for mx in [-corner_offset, corner_offset]:
        for mz in [-corner_offset, corner_offset]:
            children.append({
                "type": "loft",
                "layers": [
                    {"y": 4, "radius": 2.5, "sides": 8},
                    {"y": 12, "radius": 2.2, "sides": 8},
                    {"y": 20, "radius": 1.8, "sides": 8},
                    {"y": minaret_height, "radius": 1.4, "sides": 8},
                ],
                "material": marble_material,
                "transform": {"translation": [mx, 0, mz]}
            })
            # Minaret Balcony
            children.append({
                "type": "ring",
                "center": [mx, 12, mz],
                "outer_radius": 3.0,
                "inner_radius": 1.8,
                "height": 1,
                "material": inlay_material,
            })
            # Minaret Cupola Dome
            children.append({
                "type": "dome",
                "style": "onion",
                "radius": 2,
                "height": 3,
                "base_y": minaret_height,
                "material": dome_material,
                "finial": True,
                "transform": {"translation": [mx, 0, mz]}
            })

    return {
        "type": "union",
        "children": children
    }


def build_medieval_castle_spec(
    outer_span: int = 28,
    wall_height: int = 8,
    keep_floors: int = 3,
    bastion_radius: int = 3,
    stone_material: str = "minecraft:stone_bricks",
    accent_material: str = "minecraft:mossy_stone_bricks",
    wood_material: str = "minecraft:dark_oak_planks",
) -> Dict[str, Any]:
    """
    Generates a European Medieval Castle fortress specification:
    - Outer square curtain walls with crenellations
    - 4 round corner bastions / towers
    - Fortified gatehouse entrance with portcullis arch
    - Multi-storey central keep (donjon) with battlements
    """
    children: List[Dict[str, Any]] = []
    half_s = outer_span // 2

    # 1. Outer Curtain Walls
    curtain_wall = {
        "type": "subtract",
        "base": {
            "type": "box",
            "min_pt": [-half_s, 0, -half_s],
            "max_pt": [half_s, wall_height, half_s],
            "material": stone_material,
            "hollow": True,
            "wall_thickness": 2,
        },
        "subtrahends": [
            # Gatehouse passage opening at +Z
            {
                "type": "box",
                "min_pt": [-3, 0, half_s - 3],
                "max_pt": [3, 4, half_s + 1],
                "material": "minecraft:air",
            }
        ]
    }
    children.append(curtain_wall)

    # 2. Crenellations along curtain wall top
    children.append({
        "type": "ring",
        "center": [0, wall_height + 1, 0],
        "outer_radius": half_s,
        "inner_radius": half_s - 1,
        "height": 1,
        "material": stone_material,
    })

    # 3. 4 Corner Round Bastion Towers
    bastion_h = wall_height + 4
    for bx in [-half_s, half_s]:
        for bz in [-half_s, half_s]:
            children.append({
                "type": "cylinder",
                "center": [bx, 0, bz],
                "radius": bastion_radius,
                "height": bastion_h,
                "material": accent_material,
                "hollow": True,
                "wall_thickness": 1,
            })
            # Bastion battlements
            children.append({
                "type": "ring",
                "center": [bx, bastion_h, bz],
                "outer_radius": bastion_radius + 1,
                "inner_radius": bastion_radius - 1,
                "height": 1,
                "material": stone_material,
            })

    # 4. Central Multi-Storey Keep (Donjon)
    keep_half = half_s // 2
    keep_total_h = keep_floors * 5
    children.append({
        "type": "box",
        "min_pt": [-keep_half, 0, -keep_half],
        "max_pt": [keep_half, keep_total_h, keep_half],
        "material": stone_material,
        "hollow": True,
        "wall_thickness": 2,
    })
    # Keep roof parapet
    children.append({
        "type": "box",
        "min_pt": [-keep_half - 1, keep_total_h, -keep_half - 1],
        "max_pt": [keep_half + 1, keep_total_h + 1, keep_half + 1],
        "material": stone_material,
        "hollow": True,
        "wall_thickness": 1,
    })

    return {
        "type": "union",
        "children": children
    }


def build_islamic_fluted_minaret_spec(
    base_radius: float = 4.0,
    top_radius: float = 2.0,
    total_height: int = 36,
    storeys: int = 4,
    balconies_count: int = 3,
    sandstone_material: str = "minecraft:cut_red_sandstone",
    marble_material: str = "minecraft:quartz_block",
    accent_material: str = "minecraft:iron_bars",
) -> Dict[str, Any]:
    """
    Generates an Indo-Islamic fluted tapering minaret (Qutub Minar style) specification:
    - Multi-storey tapering shaft
    - Alternating rounded and angular flutings
    - Projecting muqarnas corbel balconies with iron railings
    - Cupola summit observation kiosk
    """
    children: List[Dict[str, Any]] = []

    # 1. Base Octagonal Plinth
    children.append({
        "type": "cylinder",
        "center": [0, 0, 0],
        "radius": int(base_radius + 2),
        "height": 2,
        "material": sandstone_material,
    })

    # 2. Tapered Shaft Lofts per storey
    h_per_storey = (total_height - 6) // storeys
    r_step = (base_radius - top_radius) / storeys

    for s in range(storeys):
        sy_start = 2 + s * h_per_storey
        sy_end = sy_start + h_per_storey
        r_bottom = base_radius - s * r_step
        r_top = base_radius - (s + 1) * r_step
        mat = marble_material if s >= 2 else sandstone_material

        children.append({
            "type": "loft",
            "layers": [
                {"y": sy_start, "radius": r_bottom, "sides": 16},
                {"y": sy_end, "radius": r_top, "sides": 16},
            ],
            "material": mat,
        })

        # Balcony at top of storey
        if s < balconies_count:
            children.append({
                "type": "ring",
                "center": [0, sy_end - 1, 0],
                "outer_radius": int(r_top + 2),
                "inner_radius": int(r_top),
                "height": 1,
                "material": sandstone_material,
            })
            children.append({
                "type": "ring",
                "center": [0, sy_end, 0],
                "outer_radius": int(r_top + 2),
                "inner_radius": int(r_top + 1),
                "height": 1,
                "material": accent_material,
            })

    # 3. Summit Cupola & Dome
    cupola_y = total_height - 4
    children.append({
        "type": "dome",
        "style": "onion",
        "radius": int(top_radius + 1),
        "height": 4,
        "base_y": cupola_y,
        "material": marble_material,
        "finial": True,
    })

    return {
        "type": "union",
        "children": children
    }


# Template registry dictionary mapping template IDs to builder functions and schema metadata
TEMPLATES_METADATA: Dict[str, Dict[str, Any]] = {
    "greek_peripteral_temple": {
        "name": "Greek Peripteral Temple",
        "style": "Classical Hellenic",
        "description": "Parthenon-style classical temple with 3-stepped stylobate, Doric peristyle colonnade, pediment gables, cella sanctuary, and pitched tile roof.",
        "builder": build_greek_peripteral_temple_spec,
        "default_parameters": {
            "colonnade_length": 24,
            "colonnade_width": 14,
            "column_height": 6,
            "roof_pitch": 0.5,
            "stylobate_material": "minecraft:smooth_quartz",
            "column_material": "minecraft:quartz_pillar",
            "wall_material": "minecraft:quartz_block",
            "roof_material": "minecraft:sandstone_stairs",
        }
    },
    "roman_colosseum_complex": {
        "name": "Roman Colosseum Arena & Arcade",
        "style": "Classical Roman",
        "description": "Multi-tier amphitheater with radial Roman round arches, Doric/Ionic columns, concentric cavea seating tiers, attic cornice, and central sand arena.",
        "builder": build_roman_colosseum_spec,
        "default_parameters": {
            "outer_radius": 24,
            "inner_radius": 16,
            "arcade_levels": 2,
            "bays_count": 24,
            "sandstone_type": "minecraft:cut_sandstone",
            "arena_material": "minecraft:sand",
            "seating_material": "minecraft:stone_brick_slab",
        }
    },
    "gothic_cathedral_complex": {
        "name": "High Gothic Cathedral Complex",
        "style": "High Gothic",
        "description": "Monumental cathedral featuring twin westwork towers with spires, rose window stained glass facade, rib vaulted nave, and clerestory lancets.",
        "builder": build_gothic_cathedral_spec,
        "default_parameters": {
            "length": 30,
            "width": 16,
            "vault_height": 14,
            "tower_height": 24,
            "stone_material": "minecraft:stone_bricks",
            "stained_glass_material": "minecraft:blue_stained_glass",
            "roof_material": "minecraft:dark_prismarine",
        }
    },
    "mughal_monument_complex": {
        "name": "Mughal Mausoleum & Minarets (Taj Mahal Style)",
        "style": "Indo-Islamic / Mughal",
        "description": "Raised marble plinth, central octagonal mausoleum with 4 pishtaq iwans, central double onion dome, and 4 corner tapering minarets with balconies.",
        "builder": build_mughal_monument_spec,
        "default_parameters": {
            "plinth_size": 28,
            "dome_radius": 6,
            "minaret_height": 26,
            "marble_material": "minecraft:quartz_block",
            "dome_material": "minecraft:smooth_quartz",
            "inlay_material": "minecraft:gold_block",
        }
    },
    "medieval_castle_fortress": {
        "name": "Medieval Concentric Castle Fortress",
        "style": "European Feudal",
        "description": "Heavy fortified castle with crenellated curtain walls, 4 round corner bastions, portcullis gatehouse, and a 3-storey central keep donjon.",
        "builder": build_medieval_castle_spec,
        "default_parameters": {
            "outer_span": 28,
            "wall_height": 8,
            "keep_floors": 3,
            "bastion_radius": 3,
            "stone_material": "minecraft:stone_bricks",
        }
    },
    "islamic_fluted_minaret": {
        "name": "Islamic Fluted Tapering Minaret (Qutub Minar Style)",
        "style": "Sultanate / Indo-Islamic",
        "description": "Multi-storey fluted tapering tower with alternating angular/circular flutings, muqarnas balconies with iron railings, and cupola summit.",
        "builder": build_islamic_fluted_minaret_spec,
        "default_parameters": {
            "base_radius": 4.0,
            "top_radius": 2.0,
            "total_height": 36,
            "storeys": 4,
            "balconies_count": 3,
            "sandstone_material": "minecraft:cut_red_sandstone",
            "marble_material": "minecraft:quartz_block",
        }
    }
}


def register_builtin_templates(session_mgr: Any) -> None:
    """Registers all built-in architectural templates into the ProceduralSessionManager."""
    for template_id, meta in TEMPLATES_METADATA.items():
        # Build the default spec
        spec = meta["builder"](**meta["default_parameters"])
        session_mgr.define_template(template_id, spec)


def get_template_catalog() -> List[Dict[str, Any]]:
    """Returns a list of all registered templates with their descriptive metadata."""
    catalog = []
    for tid, meta in TEMPLATES_METADATA.items():
        catalog.append({
            "id": tid,
            "name": meta["name"],
            "style": meta["style"],
            "description": meta["description"],
            "parameters": meta["default_parameters"],
        })
    return catalog


def build_template_spec(template_id: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Builds a template spec using default parameters overridden by any custom arguments."""
    if template_id not in TEMPLATES_METADATA:
        raise ValueError(f"Unknown architectural template '{template_id}'. Available: {list(TEMPLATES_METADATA.keys())}")
    meta = TEMPLATES_METADATA[template_id]
    params = meta["default_parameters"].copy()
    if custom_params:
        params.update(custom_params)
    return meta["builder"](**params)

