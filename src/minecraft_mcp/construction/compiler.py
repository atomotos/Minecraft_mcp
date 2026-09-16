import uuid
from typing import Dict, Any, List, Optional, Union
from minecraft_mcp.models.blueprint import (
    ArchitecturalBlueprint,
    BlueprintComponent,
    ComponentType,
    Dimensions,
    RelativeBounds,
    StructureType,
)
from minecraft_mcp.models.construction import (
    ConstructionPlan,
    ConstructionStep,
)
from minecraft_mcp.construction.components import (
    build_floor_blocks,
    build_pillar_blocks,
    build_wall_blocks,
    build_roof_blocks,
    build_doorway_blocks,
    build_window_blocks,
)

# ---------------------------------------------------------------------------
# Predefined Blueprint Templates
# ---------------------------------------------------------------------------

def create_watchtower_template() -> ArchitecturalBlueprint:
    """7x7 defensive stone watchtower with battlements and lantern."""
    return ArchitecturalBlueprint(
        id="watchtower",
        name="Watchtower",
        structure_type=StructureType.TOWER,
        dimensions=Dimensions(width=7, depth=7, height=14),
        palette={
            "foundation": "minecraft:stone_bricks",
            "walls": "minecraft:stone_bricks",
            "corners": "minecraft:stone_bricks",
            "floor": "minecraft:oak_planks",
            "platform": "minecraft:stone_bricks",
            "crenellations": "minecraft:stone_brick_wall",
            "door": "minecraft:oak_door",
            "lighting": "minecraft:lantern[hanging=true]",
        },
        description="A 7x7 fortified stone watchtower with elevated observation platform and battlements.",
        components=[
            BlueprintComponent(name="foundation", component_type=ComponentType.FOUNDATION, order=1, material_role="foundation"),
            BlueprintComponent(name="corner_pillars", component_type=ComponentType.PILLAR, order=2, material_role="corners"),
            BlueprintComponent(name="walls", component_type=ComponentType.WALL, order=3, material_role="walls"),
            BlueprintComponent(name="doorway", component_type=ComponentType.OPENING, order=4, material_role="door"),
            BlueprintComponent(name="observation_deck", component_type=ComponentType.FLOOR, order=5, material_role="platform"),
            BlueprintComponent(name="battlements", component_type=ComponentType.ROOF, order=6, material_role="crenellations"),
            BlueprintComponent(name="lighting", component_type=ComponentType.INTERIOR, order=7, material_role="lighting"),
        ],
    )

def create_oak_cabin_template() -> ArchitecturalBlueprint:
    """7x7 residential timber-framed oak cabin with pitched roof and interior."""
    return ArchitecturalBlueprint(
        id="oak_cabin",
        name="Oak Cabin",
        structure_type=StructureType.HOUSE,
        dimensions=Dimensions(width=7, depth=7, height=6),
        palette={
            "foundation": "minecraft:cobblestone",
            "floor": "minecraft:oak_planks",
            "walls": "minecraft:oak_planks",
            "corners": "minecraft:oak_log[axis=y]",
            "roof": "minecraft:oak_stairs",
            "slab": "minecraft:oak_slab",
            "door": "minecraft:oak_door",
            "window": "minecraft:glass",
            "interior_work": "minecraft:crafting_table",
            "interior_cook": "minecraft:furnace[facing=west]",
            "interior_light": "minecraft:lantern[hanging=true]",
        },
        description="A warm, furnished 7x7 wooden cottage with cobblestone foundation and gable roof.",
        components=[
            BlueprintComponent(name="foundation_and_floor", component_type=ComponentType.FLOOR, order=1, material_role="floor"),
            BlueprintComponent(name="corner_logs", component_type=ComponentType.PILLAR, order=2, material_role="corners"),
            BlueprintComponent(name="walls", component_type=ComponentType.WALL, order=3, material_role="walls"),
            BlueprintComponent(name="doorway", component_type=ComponentType.OPENING, order=4, material_role="door"),
            BlueprintComponent(name="windows", component_type=ComponentType.OPENING, order=5, material_role="window"),
            BlueprintComponent(name="pitched_roof", component_type=ComponentType.ROOF, order=6, material_role="roof"),
            BlueprintComponent(name="interior", component_type=ComponentType.INTERIOR, order=7, material_role="interior_light"),
        ],
    )

def create_stone_bridge_template() -> ArchitecturalBlueprint:
    """5x15 arched stone bridge spanning a river, ravine, or roadway."""
    return ArchitecturalBlueprint(
        id="stone_bridge",
        name="Stone Bridge",
        structure_type=StructureType.BRIDGE,
        dimensions=Dimensions(width=5, depth=15, height=4),
        palette={
            "piers": "minecraft:stone_bricks",
            "road": "minecraft:cobblestone",
            "parapet": "minecraft:stone_brick_wall",
            "lighting": "minecraft:lantern",
        },
        description="A durable 5-wide stone bridge with safety parapets and support piers.",
        components=[
            BlueprintComponent(name="piers", component_type=ComponentType.PILLAR, order=1, material_role="piers"),
            BlueprintComponent(name="deck", component_type=ComponentType.FLOOR, order=2, material_role="road"),
            BlueprintComponent(name="parapets", component_type=ComponentType.WALL, order=3, material_role="parapet"),
            BlueprintComponent(name="lanterns", component_type=ComponentType.INTERIOR, order=4, material_role="lighting"),
        ],
    )

def create_curtain_wall_template() -> ArchitecturalBlueprint:
    """3x15 fortified perimeter curtain wall with battlements and inner walkway."""
    return ArchitecturalBlueprint(
        id="curtain_wall",
        name="Curtain Wall",
        structure_type=StructureType.WALL,
        dimensions=Dimensions(width=3, depth=15, height=5),
        palette={
            "base": "minecraft:cobblestone",
            "body": "minecraft:stone_bricks",
            "crenellations": "minecraft:stone_bricks",
            "walkway": "minecraft:spruce_slab",
        },
        description="A thick, defensible stone curtain wall with upper walkway and crenellations.",
        components=[
            BlueprintComponent(name="foundation", component_type=ComponentType.FOUNDATION, order=1, material_role="base"),
            BlueprintComponent(name="wall_body", component_type=ComponentType.WALL, order=2, material_role="body"),
            BlueprintComponent(name="crenellations", component_type=ComponentType.ROOF, order=3, material_role="crenellations"),
        ],
    )

def create_wheat_farm_template() -> ArchitecturalBlueprint:
    """9x9 irrigated crop farm with central reservoir and perimeter fence."""
    return ArchitecturalBlueprint(
        id="wheat_farm",
        name="Wheat Farm",
        structure_type=StructureType.FARM,
        dimensions=Dimensions(width=9, depth=9, height=2),
        palette={
            "soil": "minecraft:farmland[moisture=7]",
            "water": "minecraft:water",
            "crop": "minecraft:wheat[age=7]",
            "fence": "minecraft:oak_fence",
            "gate": "minecraft:oak_fence_gate",
            "water_cover": "minecraft:oak_slab[type=top]",
        },
        description="A 9x9 agricultural farm with irrigated farmland, wheat crops, and fence enclosure.",
        components=[
            BlueprintComponent(name="soil_and_irrigation", component_type=ComponentType.FLOOR, order=1, material_role="soil"),
            BlueprintComponent(name="crops", component_type=ComponentType.CUSTOM, order=2, material_role="crop"),
            BlueprintComponent(name="fence_perimeter", component_type=ComponentType.WALL, order=3, material_role="fence"),
        ],
    )

def create_pillared_temple_template() -> ArchitecturalBlueprint:
    """9x11 sandstone open-air colonnaded temple dais."""
    return ArchitecturalBlueprint(
        id="pillared_temple",
        name="Pillared Temple",
        structure_type=StructureType.TEMPLE,
        dimensions=Dimensions(width=9, depth=11, height=6),
        palette={
            "dais": "minecraft:smooth_sandstone",
            "pillars": "minecraft:cut_sandstone",
            "beam": "minecraft:smooth_sandstone",
            "roof": "minecraft:sandstone_slab",
            "altar": "minecraft:chiseled_sandstone",
        },
        description="An ancient sandstone monument featuring outer pillars, dais, and central altar.",
        components=[
            BlueprintComponent(name="dais", component_type=ComponentType.FOUNDATION, order=1, material_role="dais"),
            BlueprintComponent(name="columns", component_type=ComponentType.PILLAR, order=2, material_role="pillars"),
            BlueprintComponent(name="architrave", component_type=ComponentType.WALL, order=3, material_role="beam"),
            BlueprintComponent(name="roof_slabs", component_type=ComponentType.ROOF, order=4, material_role="roof"),
            BlueprintComponent(name="altar", component_type=ComponentType.INTERIOR, order=5, material_role="altar"),
        ],
    )

TEMPLATES: Dict[str, ArchitecturalBlueprint] = {
    "watchtower": create_watchtower_template(),
    "tower": create_watchtower_template(),
    "oak_cabin": create_oak_cabin_template(),
    "house": create_oak_cabin_template(),
    "stone_bridge": create_stone_bridge_template(),
    "bridge": create_stone_bridge_template(),
    "curtain_wall": create_curtain_wall_template(),
    "wall": create_curtain_wall_template(),
    "wheat_farm": create_wheat_farm_template(),
    "farm": create_wheat_farm_template(),
    "pillared_temple": create_pillared_temple_template(),
    "temple": create_pillared_temple_template(),
}

# ---------------------------------------------------------------------------
# Blueprint Compiler
# ---------------------------------------------------------------------------

class BlueprintCompiler:
    @classmethod
    def list_templates(cls) -> List[str]:
        return list(TEMPLATES.keys())

    @classmethod
    def get_template(cls, template_id: str) -> Optional[ArchitecturalBlueprint]:
        return TEMPLATES.get(template_id.lower())

    @classmethod
    def compile(
        cls,
        blueprint_input: Union[str, ArchitecturalBlueprint, Dict[str, Any]],
        anchor: Dict[str, int],
        orientation: str = "north",
        materials_override: Optional[Dict[str, str]] = None
    ) -> ConstructionPlan:
        """
        Compiles any ArchitecturalBlueprint (predefined template or custom) into
        a sequenced, coordinate-exact ConstructionPlan.
        """
        # Resolve blueprint model
        if isinstance(blueprint_input, str):
            tpl = cls.get_template(blueprint_input)
            if not tpl:
                raise ValueError(f"Unknown architectural blueprint template '{blueprint_input}'. Available: {cls.list_templates()}")
            blueprint = tpl.model_copy(deep=True)
        elif isinstance(blueprint_input, dict):
            blueprint = ArchitecturalBlueprint.model_validate(blueprint_input)
        elif isinstance(blueprint_input, ArchitecturalBlueprint):
            blueprint = blueprint_input.model_copy(deep=True)
        else:
            raise ValueError(f"Invalid blueprint input type: {type(blueprint_input)}")

        # Merge palette overrides
        palette = blueprint.palette.copy()
        if materials_override:
            palette.update(materials_override)

        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        w = blueprint.dimensions.width
        d = blueprint.dimensions.depth
        h = blueprint.dimensions.height

        min_x, max_x = ax, ax + w - 1
        min_y, max_y = ay, ay + h - 1
        min_z, max_z = az, az + d - 1

        bounds = {
            "min": {"x": min_x, "y": min_y, "z": min_z},
            "max": {"x": max_x, "y": max_y, "z": max_z},
        }

        project_id = f"proj_{blueprint.id}_{uuid.uuid4().hex[:8]}"
        all_steps: List[ConstructionStep] = []

        # Dispatch specialized compiler based on structure type
        if blueprint.structure_type == StructureType.TOWER or blueprint.id in ("watchtower", "tower"):
            all_steps = cls._compile_watchtower(anchor, w, d, h, palette)
        elif blueprint.structure_type == StructureType.BRIDGE or blueprint.id in ("stone_bridge", "bridge"):
            all_steps = cls._compile_bridge(anchor, w, d, h, palette)
        elif blueprint.structure_type == StructureType.WALL or blueprint.id in ("curtain_wall", "wall"):
            all_steps = cls._compile_wall(anchor, w, d, h, palette)
        elif blueprint.structure_type == StructureType.HOUSE or blueprint.id in ("oak_cabin", "house"):
            all_steps = cls._compile_house(anchor, w, d, h, palette, orientation)
        elif blueprint.structure_type == StructureType.FARM or blueprint.id in ("wheat_farm", "farm"):
            all_steps = cls._compile_farm(anchor, w, d, h, palette)
        elif blueprint.structure_type == StructureType.TEMPLE or blueprint.id in ("pillared_temple", "temple"):
            all_steps = cls._compile_temple(anchor, w, d, h, palette)
        else:
            # Generic Custom Blueprint Compiler
            all_steps = cls._compile_generic(anchor, blueprint, palette)

        # Remove redundant/duplicate block coordinates (keep last step for that coordinate)
        coord_map: Dict[Tuple[int, int, int], ConstructionStep] = {}
        for s in all_steps:
            coord_map[(s.x, s.y, s.z)] = s

        deduped_steps = list(coord_map.values())

        # Calculate materials required histogram
        materials_req: Dict[str, int] = {}
        for step in deduped_steps:
            # Clean namespace for raw item representation
            mat_id = step.block.split("[")[0]
            materials_req[mat_id] = materials_req.get(mat_id, 0) + 1

        return ConstructionPlan(
            project_id=project_id,
            blueprint_id=blueprint.id,
            anchor=anchor,
            bounds=bounds,
            steps=deduped_steps,
            total_blocks=len(deduped_steps),
            materials_required=materials_req,
        )

    # -----------------------------------------------------------------------
    # Structure-Specific Compilation Routines
    # -----------------------------------------------------------------------

    @classmethod
    def _compile_watchtower(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        stone = palette.get("walls", "minecraft:stone_bricks")
        wood = palette.get("floor", "minecraft:oak_planks")
        parapet = palette.get("crenellations", "minecraft:stone_brick_wall")
        lantern = palette.get("lighting", "minecraft:lantern[hanging=true]")

        # 1. Foundation
        for b in build_floor_blocks(x1, x2, z1, z2, ay, stone):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="foundation"))

        # 2. Hollow Tower Shaft (ay+1 to ay+h-2)
        deck_y = ay + h - 2
        for y in range(ay + 1, deck_y):
            for x in range(x1, x2 + 1):
                # North and South walls
                steps.append(ConstructionStep(x=x, y=y, z=z1, block=stone, component_name="walls"))
                steps.append(ConstructionStep(x=x, y=y, z=z2, block=stone, component_name="walls"))
            for z in range(z1 + 1, z2):
                # West and East walls
                steps.append(ConstructionStep(x=x1, y=y, z=z, block=stone, component_name="walls"))
                steps.append(ConstructionStep(x=x2, y=y, z=z, block=stone, component_name="walls"))

        # 3. Doorway at center of front wall (z1)
        mid_x = (x1 + x2) // 2
        door = palette.get("door", "minecraft:oak_door")
        for b in build_doorway_blocks(mid_x, ay + 1, z1, facing="north", door_material=door):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="doorway"))

        # 4. Observation Deck (wooden floor)
        for b in build_floor_blocks(x1, x2, z1, z2, deck_y, wood):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="observation_deck"))

        # 5. Parapets / Battlements on deck perimeter (deck_y + 1)
        top_y = deck_y + 1
        for x in range(x1, x2 + 1):
            if (x - x1) % 2 == 0:
                steps.append(ConstructionStep(x=x, y=top_y, z=z1, block=parapet, component_name="battlements"))
                steps.append(ConstructionStep(x=x, y=top_y, z=z2, block=parapet, component_name="battlements"))
        for z in range(z1 + 1, z2):
            if (z - z1) % 2 == 0:
                steps.append(ConstructionStep(x=x1, y=top_y, z=z, block=parapet, component_name="battlements"))
                steps.append(ConstructionStep(x=x2, y=top_y, z=z, block=parapet, component_name="battlements"))

        # 6. Hanging Central Lantern
        steps.append(ConstructionStep(x=mid_x, y=deck_y + 2, z=(z1 + z2) // 2, block="minecraft:oak_fence", component_name="lighting"))
        steps.append(ConstructionStep(x=mid_x, y=deck_y + 1, z=(z1 + z2) // 2, block=lantern, component_name="lighting"))

        return steps

    @classmethod
    def _compile_house(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str], orientation: str) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        fnd = palette.get("foundation", "minecraft:cobblestone")
        floor = palette.get("floor", "minecraft:oak_planks")
        wall = palette.get("walls", "minecraft:oak_planks")
        corner = palette.get("corners", "minecraft:oak_log[axis=y]")
        stair = palette.get("roof", "minecraft:oak_stairs")
        slab = palette.get("slab", "minecraft:oak_slab")
        glass = palette.get("window", "minecraft:glass")
        door = palette.get("door", "minecraft:oak_door")

        # 1. Foundation & Floor
        for b in build_floor_blocks(x1, x2, z1, z2, ay, fnd):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="foundation"))
        for b in build_floor_blocks(x1 + 1, x2 - 1, z1 + 1, z2 - 1, ay, floor):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="floor"))

        # 2. Corner Pillars (ay+1 to ay+h-1)
        roof_base_y = ay + h - 1
        for cx, cz in [(x1, z1), (x2, z1), (x1, z2), (x2, z2)]:
            for b in build_pillar_blocks(cx, cz, ay + 1, h - 1, corner):
                steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="corner_pillars"))

        # 3. Perimeter Walls
        for y in range(ay + 1, roof_base_y):
            for x in range(x1 + 1, x2):
                steps.append(ConstructionStep(x=x, y=y, z=z1, block=wall, component_name="walls"))
                steps.append(ConstructionStep(x=x, y=y, z=z2, block=wall, component_name="walls"))
            for z in range(z1 + 1, z2):
                steps.append(ConstructionStep(x=x1, y=y, z=z, block=wall, component_name="walls"))
                steps.append(ConstructionStep(x=x2, y=y, z=z, block=wall, component_name="walls"))

        # 4. Windows (on East & West walls)
        mid_z = (z1 + z2) // 2
        for b in build_window_blocks(x1, ay + 2, mid_z, width=1, height=1, glass_material=glass, axis="z"):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="windows"))
        for b in build_window_blocks(x2, ay + 2, mid_z, width=1, height=1, glass_material=glass, axis="z"):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="windows"))

        # 5. Front Door (on North wall, z1)
        mid_x = (x1 + x2) // 2
        for b in build_doorway_blocks(mid_x, ay + 1, z1, facing="north", door_material=door):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="doorway"))

        # 6. Pitched Roof
        for b in build_roof_blocks(x1, x2, z1, z2, roof_base_y, style="pitched", stair_material=stair, slab_material=slab, overhang=1):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="roof"))

        # 7. Interior Fixtures
        work_table = palette.get("interior_work", "minecraft:crafting_table")
        furnace = palette.get("interior_cook", "minecraft:furnace[facing=west]")
        light = palette.get("interior_light", "minecraft:lantern[hanging=true]")

        steps.append(ConstructionStep(x=x2 - 1, y=ay + 1, z=z2 - 1, block=work_table, component_name="interior"))
        steps.append(ConstructionStep(x=x2 - 1, y=ay + 1, z=z1 + 1, block=furnace, component_name="interior"))
        steps.append(ConstructionStep(x=mid_x, y=roof_base_y - 1, z=mid_z, block=light, component_name="interior"))

        return steps

    @classmethod
    def _compile_bridge(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        piers_mat = palette.get("piers", "minecraft:stone_bricks")
        deck_mat = palette.get("road", "minecraft:cobblestone")
        parapet_mat = palette.get("parapet", "minecraft:stone_brick_wall")
        lantern_mat = palette.get("lighting", "minecraft:lantern")

        deck_y = ay + h - 1

        # 1. Piers at start, middle, and end
        z_piers = [z1, (z1 + z2) // 2, z2]
        for pz in z_piers:
            for y in range(ay, deck_y):
                for x in range(x1, x2 + 1):
                    steps.append(ConstructionStep(x=x, y=y, z=pz, block=piers_mat, component_name="piers"))

        # 2. Road Deck
        for b in build_floor_blocks(x1, x2, z1, z2, deck_y, deck_mat):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="deck"))

        # 3. Parapet Walls along outer edges (x1 and x2)
        for z in range(z1, z2 + 1):
            steps.append(ConstructionStep(x=x1, y=deck_y + 1, z=z, block=parapet_mat, component_name="parapets"))
            steps.append(ConstructionStep(x=x2, y=deck_y + 1, z=z, block=parapet_mat, component_name="parapets"))

        # 4. Lanterns at pier locations on parapets
        for pz in z_piers:
            steps.append(ConstructionStep(x=x1, y=deck_y + 2, z=pz, block=lantern_mat, component_name="lanterns"))
            steps.append(ConstructionStep(x=x2, y=deck_y + 2, z=pz, block=lantern_mat, component_name="lanterns"))

        return steps

    @classmethod
    def _compile_wall(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        stone = palette.get("body", "minecraft:stone_bricks")
        base = palette.get("base", "minecraft:cobblestone")

        # Foundation line
        for b in build_floor_blocks(x1, x2, z1, z2, ay, base):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="foundation"))

        # Solid Wall with battlements
        for b in build_wall_blocks(x1, z1, x2, z2, ay + 1, h - 1, thickness=w, material=stone, crenellations=True):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="wall_body"))

        return steps

    @classmethod
    def _compile_farm(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        soil = palette.get("soil", "minecraft:farmland[moisture=7]")
        water = palette.get("water", "minecraft:water")
        crop = palette.get("crop", "minecraft:wheat[age=7]")
        fence = palette.get("fence", "minecraft:oak_fence")
        gate = palette.get("gate", "minecraft:oak_fence_gate")
        cover = palette.get("water_cover", "minecraft:oak_slab[type=top]")

        mid_x = (x1 + x2) // 2
        mid_z = (z1 + z2) // 2

        # 1. Soil and central water reservoir
        for x in range(x1 + 1, x2):
            for z in range(z1 + 1, z2):
                if x == mid_x and z == mid_z:
                    steps.append(ConstructionStep(x=x, y=ay, z=z, block=water, component_name="irrigation"))
                    steps.append(ConstructionStep(x=x, y=ay + 1, z=z, block=cover, component_name="irrigation"))
                else:
                    steps.append(ConstructionStep(x=x, y=ay, z=z, block=soil, component_name="farmland"))
                    steps.append(ConstructionStep(x=x, y=ay + 1, z=z, block=crop, component_name="crops"))

        # 2. Perimeter Fence
        fence_y = ay + 1
        for x in range(x1, x2 + 1):
            if x == mid_x:
                steps.append(ConstructionStep(x=x, y=fence_y, z=z1, block=gate, component_name="fence"))
            else:
                steps.append(ConstructionStep(x=x, y=fence_y, z=z1, block=fence, component_name="fence"))
            steps.append(ConstructionStep(x=x, y=fence_y, z=z2, block=fence, component_name="fence"))
        for z in range(z1 + 1, z2):
            steps.append(ConstructionStep(x=x1, y=fence_y, z=z, block=fence, component_name="fence"))
            steps.append(ConstructionStep(x=x2, y=fence_y, z=z, block=fence, component_name="fence"))

        return steps

    @classmethod
    def _compile_temple(cls, anchor: Dict[str, int], w: int, d: int, h: int, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]
        x1, x2 = ax, ax + w - 1
        z1, z2 = az, az + d - 1

        dais = palette.get("dais", "minecraft:smooth_sandstone")
        pillar = palette.get("pillars", "minecraft:cut_sandstone")
        beam = palette.get("beam", "minecraft:smooth_sandstone")
        slab = palette.get("roof", "minecraft:sandstone_slab")
        altar = palette.get("altar", "minecraft:chiseled_sandstone")

        # 1. Raised Dais
        for b in build_floor_blocks(x1, x2, z1, z2, ay, dais):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="dais"))

        # 2. Outer Colonnade Pillars
        col_y = ay + 1
        col_height = h - 2
        col_positions = [
            (x1 + 1, z1 + 1), (x2 - 1, z1 + 1),
            (x1 + 1, z2 - 1), (x2 - 1, z2 - 1),
            (x1 + 1, (z1 + z2) // 2), (x2 - 1, (z1 + z2) // 2),
        ]
        for cx, cz in col_positions:
            for b in build_pillar_blocks(cx, cz, col_y, col_height, pillar):
                steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="pillars"))

        # 3. Architrave / Beams connecting columns (ay + h - 2)
        beam_y = ay + h - 2
        for x in range(x1 + 1, x2):
            steps.append(ConstructionStep(x=x, y=beam_y, z=z1 + 1, block=beam, component_name="architrave"))
            steps.append(ConstructionStep(x=x, y=beam_y, z=z2 - 1, block=beam, component_name="architrave"))
        for z in range(z1 + 1, z2):
            steps.append(ConstructionStep(x=x1 + 1, y=beam_y, z=z, block=beam, component_name="architrave"))
            steps.append(ConstructionStep(x=x2 - 1, y=beam_y, z=z, block=beam, component_name="architrave"))

        # 4. Roof Slabs (ay + h - 1)
        for b in build_floor_blocks(x1, x2, z1, z2, ay + h - 1, slab):
            steps.append(ConstructionStep(x=b["x"], y=b["y"], z=b["z"], block=b["block"], component_name="roof"))

        # 5. Central Altar
        mid_x = (x1 + x2) // 2
        mid_z = (z1 + z2) // 2
        steps.append(ConstructionStep(x=mid_x, y=ay + 1, z=mid_z, block=altar, component_name="altar"))

        return steps

    @classmethod
    def _compile_generic(cls, anchor: Dict[str, int], blueprint: ArchitecturalBlueprint, palette: Dict[str, str]) -> List[ConstructionStep]:
        steps: List[ConstructionStep] = []
        ax, ay, az = anchor["x"], anchor["y"], anchor["z"]

        for comp in sorted(blueprint.components, key=lambda c: c.order):
            mat = palette.get(comp.material_role, palette.get("main", "minecraft:stone"))
            if comp.explicit_blocks:
                for b in comp.explicit_blocks:
                    steps.append(ConstructionStep(
                        x=ax + b.get("x", 0),
                        y=ay + b.get("y", 0),
                        z=az + b.get("z", 0),
                        block=b.get("block", mat),
                        component_name=comp.name,
                    ))
            elif comp.bounds:
                bx1, bx2 = ax + comp.bounds.min_x, ax + comp.bounds.max_x
                by1, by2 = ay + comp.bounds.min_y, ay + comp.bounds.max_y
                bz1, bz2 = az + comp.bounds.min_z, az + comp.bounds.max_z
                for x in range(min(bx1, bx2), max(bx1, bx2) + 1):
                    for y in range(min(by1, by2), max(by1, by2) + 1):
                        for z in range(min(bz1, bz2), max(bz1, bz2) + 1):
                            steps.append(ConstructionStep(
                                x=x, y=y, z=z, block=mat, component_name=comp.name
                            ))

        return steps
