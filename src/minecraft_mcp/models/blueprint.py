from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class StructureType(str, Enum):
    HOUSE = "house"
    TOWER = "tower"
    BRIDGE = "bridge"
    WALL = "wall"
    CASTLE = "castle"
    FARM = "farm"
    TEMPLE = "temple"
    MONUMENT = "monument"
    ROAD = "road"
    CUSTOM = "custom"

class ComponentType(str, Enum):
    FOUNDATION = "foundation"
    FLOOR = "floor"
    WALL = "wall"
    PILLAR = "pillar"
    ROOF = "roof"
    OPENING = "opening"
    INTERIOR = "interior"
    TRIM = "trim"
    CUSTOM = "custom"

class Dimensions(BaseModel):
    width: int = Field(gt=0, description="Footprint along X axis")
    depth: int = Field(gt=0, description="Footprint along Z axis")
    height: int = Field(gt=0, description="Total vertical height along Y axis")

class RelativeBounds(BaseModel):
    min_x: int = 0
    min_y: int = 0
    min_z: int = 0
    max_x: int = 0
    max_y: int = 0
    max_z: int = 0

class BlueprintComponent(BaseModel):
    name: str
    component_type: ComponentType = ComponentType.CUSTOM
    bounds: Optional[RelativeBounds] = None
    material_role: str = "main"  # e.g. "foundation", "wall", "pillar", "roof", "accent"
    properties: Dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    # Optional explicit list of relative voxel blocks [{"x": dx, "y": dy, "z": dz, "block": "minecraft:..."}]
    explicit_blocks: Optional[List[Dict[str, Any]]] = None

class ArchitecturalBlueprint(BaseModel):
    id: str
    name: str
    structure_type: StructureType = StructureType.CUSTOM
    dimensions: Dimensions
    palette: Dict[str, str] = Field(default_factory=dict)  # e.g. {"foundation": "minecraft:cobblestone", "wall": "minecraft:oak_planks"}
    components: List[BlueprintComponent] = Field(default_factory=list)
    clear_envelope: bool = True
    orientation: str = "north"
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

