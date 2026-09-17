from typing import Dict, Any, List
from minecraft_mcp.models.knowledge import (
    BlockKnowledge,
    BlockProperties,
    BlockAppearance,
    BlockConstructionUses,
    BlockRelationships,
    MaterialPaletteKnowledge,
    ArchitectureKnowledge,
)

VERIFIED_BLOCKS: List[BlockKnowledge] = [
    BlockKnowledge(
        id="minecraft:oak_planks",
        name="Oak Planks",
        appearance=BlockAppearance(color="brown", texture_category="wood"),
        properties=BlockProperties(solid=True, transparent=False, flammable=True, gravity=False),
        construction=BlockConstructionUses(uses=["wall", "floor", "ceiling", "interior"]),
        relationships=BlockRelationships(
            family="oak",
            stairs="minecraft:oak_stairs",
            slab="minecraft:oak_slab",
            door="minecraft:oak_door",
            fence="minecraft:oak_fence",
        ),
    ),
    BlockKnowledge(
        id="minecraft:oak_log",
        name="Oak Log",
        appearance=BlockAppearance(color="brown", texture_category="wood"),
        properties=BlockProperties(solid=True, transparent=False, flammable=True, gravity=False),
        construction=BlockConstructionUses(uses=["pillar", "beam", "corner_support", "frame"]),
        relationships=BlockRelationships(family="oak"),
    ),
    BlockKnowledge(
        id="minecraft:stone_bricks",
        name="Stone Bricks",
        appearance=BlockAppearance(color="gray", texture_category="stone"),
        properties=BlockProperties(solid=True, transparent=False, flammable=False, gravity=False),
        construction=BlockConstructionUses(uses=["wall", "foundation", "pillar", "battlement"]),
        relationships=BlockRelationships(
            family="stone_brick",
            stairs="minecraft:stone_brick_stairs",
            slab="minecraft:stone_brick_slab",
            wall="minecraft:stone_brick_wall",
        ),
    ),
    BlockKnowledge(
        id="minecraft:cobblestone",
        name="Cobblestone",
        appearance=BlockAppearance(color="gray", texture_category="stone"),
        properties=BlockProperties(solid=True, transparent=False, flammable=False, gravity=False),
        construction=BlockConstructionUses(uses=["foundation", "wall", "path", "perimeter"]),
        relationships=BlockRelationships(
            family="cobblestone",
            stairs="minecraft:cobblestone_stairs",
            slab="minecraft:cobblestone_slab",
            wall="minecraft:cobblestone_wall",
        ),
    ),
    BlockKnowledge(
        id="minecraft:glass_pane",
        name="Glass Pane",
        appearance=BlockAppearance(color="clear", texture_category="glass"),
        properties=BlockProperties(solid=True, transparent=True, flammable=False, gravity=False),
        construction=BlockConstructionUses(uses=["window", "skylight", "viewpoint"]),
        relationships=BlockRelationships(family="glass"),
    ),
    BlockKnowledge(
        id="minecraft:torch",
        name="Torch",
        appearance=BlockAppearance(color="yellow", texture_category="light"),
        properties=BlockProperties(solid=False, transparent=True, flammable=False, gravity=False),
        construction=BlockConstructionUses(uses=["lighting", "hazard_prevention", "interior_decor"]),
        relationships=BlockRelationships(family="torch"),
    ),
    BlockKnowledge(
        id="minecraft:sandstone",
        name="Sandstone",
        appearance=BlockAppearance(color="tan", texture_category="sandstone"),
        properties=BlockProperties(solid=True, transparent=False, flammable=False, gravity=False),
        construction=BlockConstructionUses(uses=["wall", "foundation", "path", "desert_building"]),
        relationships=BlockRelationships(
            family="sandstone",
            stairs="minecraft:sandstone_stairs",
            slab="minecraft:sandstone_slab",
            wall="minecraft:sandstone_wall",
        ),
    ),
]

MATERIAL_PALETTES: List[MaterialPaletteKnowledge] = [
    MaterialPaletteKnowledge(
        id="rustic_wood",
        name="Rustic Woodland",
        category="medieval",
        blocks=[
            "minecraft:oak_planks",
            "minecraft:oak_log",
            "minecraft:oak_stairs",
            "minecraft:oak_slab",
            "minecraft:cobblestone",
            "minecraft:glass_pane",
            "minecraft:oak_door",
        ],
    ),
    MaterialPaletteKnowledge(
        id="castle_stone",
        name="Castle Masonry",
        category="fortress",
        blocks=[
            "minecraft:stone_bricks",
            "minecraft:cobblestone",
            "minecraft:stone_brick_stairs",
            "minecraft:stone_brick_slab",
            "minecraft:iron_bars",
            "minecraft:dark_oak_door",
        ],
    ),
    MaterialPaletteKnowledge(
        id="desert_oasis",
        name="Desert Adobe",
        category="desert",
        blocks=[
            "minecraft:sandstone",
            "minecraft:smooth_sandstone",
            "minecraft:cut_sandstone",
            "minecraft:sandstone_stairs",
            "minecraft:sandstone_slab",
            "minecraft:acacia_planks",
        ],
    ),
    MaterialPaletteKnowledge(
        id="nether_keep",
        name="Nether Citadel",
        category="underworld",
        blocks=[
            "minecraft:nether_bricks",
            "minecraft:red_nether_bricks",
            "minecraft:nether_brick_fence",
            "minecraft:nether_brick_stairs",
            "minecraft:obsidian",
        ],
    ),
]

ARCHITECTURE_INFO = ArchitectureKnowledge(
    templates=[
        "watchtower",
        "oak_cabin",
        "stone_bridge",
        "curtain_wall",
        "wheat_farm",
        "pillared_temple",
        "custom",
    ],
    styles=["medieval", "rustic", "classical", "fortress", "agrarian"],
    component_types=[
        "foundation",
        "floor",
        "pillars",
        "walls",
        "windows",
        "doorway",
        "roof",
        "crenellations",
        "interior",
    ],
)

